#
# Shared BV-BRC-side code for App-ModularPipeline and App-ModularStep: call the modpipe CLI, preflight sizing,
# input staging from the workspace / data API, and uploading outputs with their workspace types.
#
# Output layout in the job's result folder (<output_path>/.<output_file>/):
#   <output>[/<sample>]/<file>   one folder per output value, tagged with workspace metadata
#                                modpipe_type, modpipe_attrs (JSON), modpipe_files (JSON {part|"_": file name}),
#                                modpipe_sample; each file is tagged modpipe_type (+ modpipe_part)
#   outputs.json                 {output: [{sample, type, attrs, folder, files: {part|"_": ws path}}]}
#   pipeline.json, pipeline_run.json
# An output folder can be given as-is to a later App-ModularStep input port: the metadata carries its type,
# parts and sample id along.
#
package ModularPipeline::AppCommon;

use strict;
use warnings;
use Bio::KBase::AppService::ReadSet;
use P3DataAPI;
use Cwd qw(getcwd abs_path);
use Data::Dumper;
use File::Basename;
use File::Path qw(make_path);
use File::Slurp;
use FindBin;
use IPC::Run;
use JSON::XS;
use base 'Exporter';

our @EXPORT_OK = qw(modpipe validate_pipeline preflight_for stage_inputs run_and_upload ws_metadata);

my $json = JSON::XS->new->pretty(1)->canonical(1);

#
# Locate the modpipe CLI. Deployed: $KB_TOP/bin/modpipe (wrap_python3 wrapper; data in services/modular_pipeline).
# Source checkout: <repo>/bin/modpipe next to the script's service-scripts/ dir, or MODPIPE_HOME.
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

#
# Workspace metadata for a list of paths: {path => {type => <ws type>, meta => {user metadata}}}.
# Paths that can't be read are left out (staging reports them later).
#
sub ws_metadata
{
    my($ws, $paths) = @_;
    my %out;
    for my $p (@$paths)
    {
        next if $out{$p};
        my $res = eval { $ws->get({ objects => [$p], metadata_only => 1 }) };
        if (!$res || !@$res)
        {
            print STDERR "No workspace metadata for $p" . ($@ ? ": $@" : "") . "\n";
            next;
        }
        my $m = $res->[0]->[0];
        $out{$p} = { type => $m->[1], meta => $m->[7] // {} };
        # A port folder (<result>/<output>) of a per-sample output holds one value folder per sample: list them.
        if ($m->[1] eq 'folder' && !($m->[7] // {})->{modpipe_type})
        {
            my $ls = eval { $ws->ls({ paths => [$p] }) } // {};
            my @kids;
            for my $c (@{$ls->{$p} // []})
            {
                next unless $c->[1] eq 'folder' && ($c->[7] // {})->{modpipe_type};
                my $cp = "$c->[2]$c->[0]";
                $out{$cp} = { type => 'folder', meta => $c->[7] };
                push(@kids, $cp);
            }
            $out{$p}->{children} = [sort @kids] if @kids;
        }
    }
    return \%out;
}

# ---------------------------------------------------------------- preflight

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

sub preflight_for
{
    my($app, $file) = @_;
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

sub is_ws_path
{
    my($p) = @_;
    return $p =~ m,^/[^/]+@[^/]+/, && ! -e $p;
}

# Download one workspace file into $dir (callers pass a per-item subdirectory where needed, so equal file names
# from different folders, e.g. two samples' sorted.bam, don't collide). Local paths are used in place.
sub stage_file
{
    my($app, $p, $dir) = @_;
    return $p unless is_ws_path($p);
    make_path($dir);
    my $got = $app->stage_in([$p], $dir, 1);
    return abs_path($got->{$p});
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
            push(@files, stage_file($app, $p, $dir));
        }
        if (my $parts = $src->{parts})
        {
            my $i = 0;
            my @items;
            for my $it (ref($parts) eq 'ARRAY' ? @$parts : ($parts))
            {
                $i++;
                my %loc = map { $_ eq 'sample_id' ? ($_ => $it->{$_}) : ($_ => stage_file($app, $it->{$_}, "$dir/$i")) }
                          keys %$it;
                push(@items, \%loc);
            }
            $new{parts} = \@items;
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
        $new{database_file} = $src->{database_file} if $src->{database_file};   # registry file, resolved by modpipe
        if (my $fids = $src->{feature_ids})
        {
            my $aa = $type =~ /^sequences\.protein/;
            my $seqs = $aa ? $api->retrieve_protein_feature_sequence($fids) : $api->retrieve_nucleotide_feature_sequence($fids);
            my @missing = grep { !$seqs->{$_} } @$fids;
            die "Input $name: no sequence for feature(s) @missing\n" if @missing;
            my $f = "$dir/feature_ids." . ($aa ? "faa" : "ffn");
            open(my $fh, ">", $f) or die "Cannot write $f: $!";
            print $fh ">$_\n$seqs->{$_}\n" foreach @$fids;
            close($fh);
            push(@files, $f);
            $new{files} = \@files;
        }
        %new or die "Input $name: nothing to stage from source " . encode_json($src) . "\n";
        $in->{source} = \%new;
    }
    return $pipe;
}

# ---------------------------------------------------------------- run + upload

# Create workspace folders between $base (exists) and $dir, parents first; $meta tags the leaf.
sub ws_mkdir
{
    my($ws, $base, $dir, $made, $meta) = @_;
    return if $dir eq $base || $made->{$dir};
    ws_mkdir($ws, $base, dirname($dir), $made);
    $ws->create({ objects => [[$dir, 'folder', $meta // {}]] });
    $made->{$dir} = 1;
}

#
# Validate + stage + run the pipeline in $file, then upload pipeline.json, pipeline_run.json, every output value
# (layout above) and outputs.json into the result folder. Dies if the run failed (after uploading what exists).
# Returns {pipeline, outputs => [saved files], values => outputs.json content}.
#
sub run_and_upload
{
    my($app, $file, %opt) = @_;
    my $top = getcwd();
    my $staging = "$top/staging";
    my $work = "$top/work";
    make_path($staging, $work);

    validate_pipeline($file);
    my $pipe = decode_json(scalar read_file($file));
    my $submitted = $json->encode($pipe);
    stage_inputs($app, $pipe, $staging);
    write_file("$top/pipeline.staged.json", $json->encode($pipe));

    my $cpu = $ENV{P3_ALLOCATED_CPU} // 2;
    my $mem = $ENV{P3_ALLOCATED_MEMORY} // "8G";              # e.g. "65536M"
    if ($mem =~ /^(\d+)M$/i) { $mem = int($1 / 1024) . "G"; }
    my @run = ("run", "$top/pipeline.staged.json", "--workdir", $work, "--executor", $opt{executor} // "snakemake",
               "--cores", $cpu, "--mem", $mem);
    push(@run, "--keep-intermediates") if $opt{keep_intermediates};
    my($ok) = modpipe(@run);

    # Upload whatever exists, even on failure (provenance + partial results help debugging).
    my $folder = $app->result_folder;
    my $ws = $app->workspace;
    my $token = $app->token->token;
    $ws->save_data_to_file($submitted, {}, "$folder/pipeline.json", "json", 1, 0, $token);
    if (-s "$work/pipeline_run.json")
    {
        $ws->save_file_to_file("$work/pipeline_run.json", {}, "$folder/pipeline_run.json", "json", 1, 0, $token);
    }
    my(@saved, %values);
    if (-s "$work/outputs/manifest.json")
    {
        my $manifest = decode_json(scalar read_file("$work/outputs/manifest.json"));
        my %made;
        # One folder per output value (<output>[/<sample>]), created with metadata before its files.
        my(%vals, @order);
        for my $e (@$manifest)
        {
            my $key = join("\0", $e->{output}, $e->{sample} // '');
            push(@order, $key) unless $vals{$key};
            my $v = $vals{$key} //= { output => $e->{output}, sample => $e->{sample}, type => $e->{type},
                                      attrs => $e->{attrs} // {}, entries => [] };
            push(@{$v->{entries}}, $e);
        }
        for my $key (@order)
        {
            my $v = $vals{$key};
            my $vdir = "$folder/$v->{output}" . (defined($v->{sample}) ? "/$v->{sample}" : "");
            my %names = map { (($_->{part} // '_') => basename($_->{path})) } @{$v->{entries}};
            my $meta = { modpipe_type => $v->{type}, modpipe_attrs => encode_json($v->{attrs}),
                         modpipe_files => encode_json(\%names),
                         (defined($v->{sample}) ? (modpipe_sample => "$v->{sample}") : ()) };
            ws_mkdir($ws, $folder, $vdir, \%made, $meta);
            my %files;
            for my $e (@{$v->{entries}})
            {
                my $dest = "$vdir/" . basename($e->{path});
                my $local = abs_path("$work/$e->{path}");                  # resolves the symlink
                my $big = (-s $local) > 10 * 1024 * 1024 ? 1 : 0;          # large files go through Shock
                print STDERR "Save $local -> $dest ($e->{wstype})\n";
                $ws->save_file_to_file($local, { modpipe_type => $e->{type},
                                                 (defined($e->{part}) ? (modpipe_part => $e->{part}) : ()) },
                                       $dest, $e->{wstype}, 1, $big, $token);
                $files{$e->{part} // '_'} = $dest;
                push(@saved, { path => $dest, type => $e->{type}, wstype => $e->{wstype}, output => $e->{output},
                               (defined($e->{part}) ? (part => $e->{part}) : ()),
                               (defined($e->{sample}) ? (sample => $e->{sample}) : ()) });
            }
            push(@{$values{$v->{output}}}, { folder => $vdir, type => $v->{type}, attrs => $v->{attrs}, files => \%files,
                                             (defined($v->{sample}) ? (sample => $v->{sample}) : ()) });
        }
        $ws->save_data_to_file($json->encode(\%values), {}, "$folder/outputs.json", "json", 1, 0, $token);
    }
    # Local copy for a wrapper running this app (modpipe cwl-step reads it to report CWL outputs).
    write_file("$top/modpipe_step_result.json", $json->encode({ result_folder => $folder, values => \%values,
                                                                 ok => ($ok ? JSON::XS::true : JSON::XS::false) }));
    $ok or die "Pipeline execution failed; see pipeline_run.json in $folder\n";
    return { pipeline => $pipe->{name}, outputs => \@saved, values => \%values };
}

1;
