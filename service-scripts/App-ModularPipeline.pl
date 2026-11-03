#
# App-ModularPipeline: run a modpipe pipeline (connected tool modules) as a BV-BRC job.
#
# The Perl shell does the BV-BRC-specific parts; the Python core (bin/modpipe) does the rest:
#   preflight : modpipe instantiate (templates) + modpipe validate --json  ->  cpu / memory / runtime / partition
#   run       : stage inputs (ReadSet for reads incl. SRA, workspace files, genome & feature groups via the data API)
#               -> modpipe run (Snakemake) -> upload outputs/manifest.json entries with their workspace types
#               -> save pipeline.json + pipeline_run.json (provenance)
#
# Params (app_specs/ModularPipeline.json): pipeline | pipeline_template (+ inputs, template_params),
# keep_intermediates, output_path, output_file.
#
use strict;
use warnings;
use Bio::KBase::AppService::AppScript;
use Bio::KBase::AppService::ReadSet;
use P3DataAPI;
use Cwd qw(getcwd abs_path);
use Data::Dumper;
use File::Basename;
use File::Path qw(make_path);
use File::Slurp;
use File::Temp;
use FindBin;
use IPC::Run;
use JSON::XS;

my $json = JSON::XS->new->pretty(1)->canonical(1);

my $script = Bio::KBase::AppService::AppScript->new(\&run_pipeline, \&preflight);
exit $script->run(\@ARGV);

# ---------------------------------------------------------------- helpers

#
# Locate the modpipe CLI. Deployed: $KB_TOP/bin/modpipe (wrap_python3 wrapper; data in services/modular_pipeline).
# Source checkout: <repo>/bin/modpipe next to this script's service-scripts/ dir, or MODPIPE_HOME.
#
sub modpipe_bin
{
    for my $c (($ENV{MODPIPE_HOME} ? "$ENV{MODPIPE_HOME}/bin/modpipe" : ()),
               "$FindBin::RealBin/../bin/modpipe",
               ($ENV{KB_TOP} ? "$ENV{KB_TOP}/bin/modpipe" : ()))
    {
        return abs_path($c) if -x $c;
    }
    die "Cannot find the modpipe CLI (deploy ModularService, or set MODPIPE_HOME to a checkout)\n";
}

sub modpipe
{
    my(@args) = @_;
    my @cmd = (modpipe_bin(), @args);
    print STDERR "Run: @cmd\n";
    my($out, $err);
    my $ok = IPC::Run::run(\@cmd, '>', \$out, '2>', \$err);
    print STDERR $err if $err;
    return ($ok, $out, $err);
}

#
# Build the concrete pipeline JSON from the params (full pipeline, or template + inputs + template_params).
#
sub resolve_pipeline
{
    my($params, $dir) = @_;
    my $out = "$dir/pipeline.json";
    if ($params->{pipeline} && $params->{pipeline_template})
    {
        die "Give either pipeline or pipeline_template, not both\n";
    }
    if (my $p = $params->{pipeline})
    {
        $p = decode_json($p) unless ref($p);
        write_file($out, $json->encode($p));
        return $out;
    }
    my $t = $params->{pipeline_template} or die "No pipeline or pipeline_template given\n";
    my @args = ("instantiate", $t, "--out", $out);
    if ($params->{inputs})
    {
        write_file("$dir/template_inputs.json", $json->encode($params->{inputs}));
        push(@args, "--inputs", "$dir/template_inputs.json");
    }
    if ($params->{template_params})
    {
        write_file("$dir/template_params.json", $json->encode($params->{template_params}));
        push(@args, "--params", "$dir/template_params.json");
    }
    my($ok) = modpipe(@args);
    $ok or die "Could not instantiate pipeline template $t\n";
    return $out;
}

sub validate_pipeline
{
    my($file) = @_;
    my($ok, $out) = modpipe("validate", "--json", $file);
    my $res = eval { decode_json($out) };
    if (!$res || !$res->{ok})
    {
        my $errs = $res ? join("\n  ", @{$res->{errors}}) : ($out // '');
        die "Pipeline is invalid:\n  $errs\n";
    }
    return $res;
}

# ---------------------------------------------------------------- preflight

sub preflight
{
    my($app, $app_def, $raw_params, $params) = @_;
    my $tmp = File::Temp->newdir();
    my $file = resolve_pipeline($params, "$tmp");
    my $res = validate_pipeline($file);
    my $r = $res->{plan}->{resources};

    # Storage: staged read sizes (ReadSet knows them, incl. SRA metadata) x a factor for intermediates.
    my $pipe = decode_json(scalar read_file($file));
    my $bytes = 0;
    for my $name (keys %{$pipe->{inputs} // {}})
    {
        my $src = $pipe->{inputs}->{$name}->{source} // {};
        next unless $src->{paired_end_libs} || $src->{single_end_libs} || $src->{srr_ids} || $src->{srr_libs};
        my $rs = Bio::KBase::AppService::ReadSet->create_from_asssembly_params(readset_params($src), 1);
        my($ok, $errs, $comp, $uncomp) = $rs->validate($app->workspace);
        die "Input $name: " . join("; ", @$errs) . "\n" unless $ok;
        $bytes += ($comp // 0) + ($uncomp // 0);
    }
    my $storage = $bytes ? 5 * $bytes : 20 * 1024 ** 3;

    my $policy;
    if ($r->{partition} || $r->{constraint})
    {
        $policy = { ($r->{partition} ? (partition => $r->{partition}) : ()),
                    ($r->{constraint} ? (constraint => $r->{constraint}) : ()) };
    }
    my $pf = {
        cpu => $r->{cpu},
        memory => int($r->{memory_gb} + 0.999) . "G",
        runtime => int($r->{runtime_s} * 1.2) + 1800,      # plan estimate + 20% + 30 min staging/upload
        storage => int($storage),
        ($policy ? (policy_data => $policy) : ()),
    };
    print STDERR "Preflight: " . Dumper($pf);
    return $pf;
}

# ---------------------------------------------------------------- staging

sub readset_params
{
    my($src) = @_;
    my $p = { paired_end_libs => [], single_end_libs => [], srr_libs => [] };
    push(@{$p->{paired_end_libs}}, @{$src->{paired_end_libs}}) if $src->{paired_end_libs};
    push(@{$p->{single_end_libs}}, @{$src->{single_end_libs}}) if $src->{single_end_libs};
    push(@{$p->{srr_libs}}, @{$src->{srr_libs}}) if $src->{srr_libs};
    # srr_ids -> srr_libs so each run keeps its accession as the sample id
    push(@{$p->{srr_libs}}, map { { srr_accession => $_, sample_id => $_ } } @{$src->{srr_ids}}) if $src->{srr_ids};
    return $p;
}

sub is_ws_path
{
    my($p) = @_;
    return $p =~ m,^/[^/]+@[^/]+/, && ! -e $p;
}

#
# Rewrite every pipeline input source into local files the Python runner can use directly.
#
sub stage_inputs
{
    my($app, $pipe, $staging) = @_;
    my $api = P3DataAPI->new();
    for my $name (sort keys %{$pipe->{inputs} // {}})
    {
        my $in = $pipe->{inputs}->{$name};
        my $src = $in->{source} // {};
        my $type = $in->{type};
        my $dir = "$staging/$name";
        make_path($dir);
        my %new;

        if ($src->{paired_end_libs} || $src->{single_end_libs} || $src->{srr_ids} || $src->{srr_libs})
        {
            my $rs = Bio::KBase::AppService::ReadSet->create_from_asssembly_params(readset_params($src), 1);
            my($ok, $errs) = $rs->validate($app->workspace);
            die "Input $name: " . join("; ", @$errs) . "\n" unless $ok;
            $rs->localize_libraries($dir);
            $rs->stage_in($app->workspace);
            my(@pe, @se);
            $rs->visit_libraries(
                sub { my($l) = @_; push(@pe, { read1 => abs_path($l->{read_path_1}), read2 => abs_path($l->{read_path_2}),
                                               (defined($l->{sample_id}) ? (sample_id => $l->{sample_id}) : ()) }); },
                sub { my($l) = @_; push(@se, { read => abs_path($l->{read_path}),
                                               (defined($l->{sample_id}) ? (sample_id => $l->{sample_id}) : ()) }); });
            if ($type =~ /^reads\.short\.paired/ && @se)
            {
                die "Input $name expects paired-end reads but got " . scalar(@se) . " single-end library(ies)\n";
            }
            if ($type =~ /^reads\.(short\.single|long)/ && @pe)
            {
                die "Input $name expects single-end/long reads but got " . scalar(@pe) . " paired-end library(ies)\n";
            }
            $new{paired_end_libs} = \@pe if @pe;
            $new{single_end_libs} = \@se if @se;
        }
        my @files;
        for my $p (($src->{wsid} ? ($src->{wsid}) : ()), @{$src->{wsids} // []}, @{$src->{files} // []})
        {
            if (is_ws_path($p))
            {
                my $got = $app->stage_in([$p], $dir, 1);
                push(@files, abs_path($got->{$p}));
            }
            else
            {
                push(@files, $p);
            }
        }
        if (my $gg = $src->{genome_group})
        {
            my $ids = $api->retrieve_patric_ids_from_genome_group($gg);
            @$ids or die "Input $name: genome group $gg is empty or not readable\n";
            $new{genome_ids} = [ @{$src->{genome_ids} // []}, @$ids ];
        }
        elsif ($src->{genome_ids})
        {
            $new{genome_ids} = $src->{genome_ids};
        }
        if (my $fg = $src->{feature_group})
        {
            my $aa = $type =~ /^sequences\.protein/;
            my $seqs = $aa ? $api->retrieve_protein_sequences_from_feature_group($fg)
                           : $api->retrieve_nucleotide_sequences_from_feature_group($fg);
            @$seqs or die "Input $name: feature group $fg has no sequences\n";
            my $f = "$dir/feature_group." . ($aa ? "faa" : "ffn");
            open(my $fh, ">", $f) or die "Cannot write $f: $!";
            for my $s (@$seqs)
            {
                my $id = $s->{patric_id} // $s->{feature_id};
                print $fh ">$id $s->{annotation}\n$s->{sequence}\n" if $s->{sequence};
            }
            close($fh);
            push(@files, $f);
        }
        if (defined(my $fd = $src->{fasta_data}))
        {
            my $f = "$dir/fasta_data.fasta";
            write_file($f, $fd);
            push(@files, $f);
        }
        $new{files} = \@files if @files;
        $new{fixture} = $src->{fixture} if $src->{fixture};       # test runs only
        if ($src->{feature_ids})
        {
            die "Input $name: feature_ids sources are not supported yet (use a feature group)\n";
        }
        %new or die "Input $name: nothing to stage from source " . encode_json($src) . "\n";
        $in->{source} = \%new;
    }
    return $pipe;
}

# ---------------------------------------------------------------- run

# Create workspace folders between $base (exists) and $dir, parents first.
sub ws_mkdir
{
    my($ws, $base, $dir, $made) = @_;
    return if $dir eq $base || $made->{$dir};
    ws_mkdir($ws, $base, dirname($dir), $made);
    $ws->create({ objects => [[$dir, 'folder']] });
    $made->{$dir} = 1;
}

sub run_pipeline
{
    my($app, $app_def, $raw_params, $params) = @_;
    my $top = getcwd();
    my $staging = "$top/staging";
    my $work = "$top/work";
    make_path($staging, $work);

    my $file = resolve_pipeline($params, $top);
    validate_pipeline($file);
    my $pipe = decode_json(scalar read_file($file));
    my $submitted = $json->encode($pipe);
    stage_inputs($app, $pipe, $staging);
    write_file("$top/pipeline.staged.json", $json->encode($pipe));

    my $cpu = $ENV{P3_ALLOCATED_CPU} // 2;
    my $mem = $ENV{P3_ALLOCATED_MEMORY} // "8G";              # e.g. "65536M"
    if ($mem =~ /^(\d+)M$/i) { $mem = int($1 / 1024) . "G"; }
    my @run = ("run", "$top/pipeline.staged.json", "--workdir", $work, "--executor", "snakemake",
               "--cores", $cpu, "--mem", $mem);
    push(@run, "--keep-intermediates") if $params->{keep_intermediates};
    my($ok) = modpipe(@run);

    # Upload whatever exists, even on failure (provenance + partial results help debugging).
    my $folder = $app->result_folder;
    my $ws = $app->workspace;
    $ws->save_data_to_file($submitted, {}, "$folder/pipeline.json", "json", 1, 0, $app->token->token);
    if (-s "$work/pipeline_run.json")
    {
        $ws->save_file_to_file("$work/pipeline_run.json", {}, "$folder/pipeline_run.json", "json", 1, 0, $app->token->token);
    }
    my @saved;
    if (-s "$work/outputs/manifest.json")
    {
        my $manifest = decode_json(scalar read_file("$work/outputs/manifest.json"));
        my %made;
        for my $e (@$manifest)
        {
            my $rel = $e->{path};                                     # outputs/<name>[/<sample>]/<file>
            (my $dest_rel = $rel) =~ s,^outputs/,,;
            my $dest = "$folder/$dest_rel";
            ws_mkdir($ws, $folder, dirname($dest), \%made);
            my $local = abs_path("$work/$rel");                        # resolves the symlink
            my $big = (-s $local) > 10 * 1024 * 1024 ? 1 : 0;          # large files go through Shock
            print STDERR "Save $local -> $dest ($e->{wstype})\n";
            $ws->save_file_to_file($local, { modpipe_type => $e->{type} }, $dest, $e->{wstype}, 1, $big, $app->token->token);
            push(@saved, { path => $dest, type => $e->{type}, wstype => $e->{wstype}, output => $e->{output},
                           (defined($e->{sample}) ? (sample => $e->{sample}) : ()) });
        }
    }
    $ok or die "Pipeline execution failed; see pipeline_run.json in $folder\n";
    return { pipeline => $pipe->{name}, outputs => \@saved };
}
