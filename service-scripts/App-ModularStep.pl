#
# App-ModularStep: run ONE modpipe module as a BV-BRC job.
#
# This is the unit GoWe workflows are built from: one CWL tool per module, each running this app (on a GoWe worker
# for now; through GoWe's BV-BRC executor once the app is registered). Params are flat (see lib/modpipe/step.py):
#   module, output_path, output_file, [input_types], <input port> = data, <parameter id> = value
# Port values are workspace paths (a file, or an output folder of an earlier ModularStep/ModularPipeline job, whose
# metadata carries type, parts and sample id), lists of them, or pipeline source objects.
#
# The app builds a one-step pipeline (modpipe step-pipeline) and runs it through the same path as
# App-ModularPipeline (lib/ModularPipeline/AppCommon.pm). Results: <output_path>/.<output_file>/<output port>[/<sample>]/
# plus outputs.json, pipeline.json, pipeline_run.json.
#
use strict;
use warnings;
use FindBin;
use lib "$FindBin::RealBin/../lib";
use Bio::KBase::AppService::AppScript;
use Cwd ();
use File::Slurp;
use File::Temp;
use JSON::XS;
use ModularPipeline::AppCommon qw(modpipe preflight_for run_and_upload ws_metadata);

my $json = JSON::XS->new->pretty(1)->canonical(1);
my %RESERVED = map { $_ => 1 } qw(module output_path output_file input_types);

my $script = Bio::KBase::AppService::AppScript->new(\&run_step, \&preflight);
# AppScript::run returns the child's raw wait status (e.g. 256 or 65280); `exit` of that would wrap to 0, so
# convert it to a real exit code (failures must not look like success to Slurm or GoWe).
my $status = $script->run(\@ARGV) // 0;
exit($status == 0 ? 0 : ($status >> 8) || 1);

#
# Write the one-step pipeline for these params to $dir/pipeline.json. Workspace paths given as port values are
# looked up first, so their modpipe_* metadata (type, parts, sample) can be used.
#
sub step_pipeline
{
    my($app, $raw, $dir) = @_;
    my %params = map { ($_ => $raw->{$_}) } grep { !/^_/ } keys %$raw;
    my @paths;
    for my $k (sort keys %params)
    {
        next if $RESERVED{$k};
        my $v = $params{$k};
        for my $x (ref($v) eq 'ARRAY' ? @$v : ($v))
        {
            push(@paths, $x) if defined($x) && !ref($x) && $x =~ m,^/[^/]+@[^/]+/,;
        }
    }
    my $meta = @paths ? ws_metadata($app->workspace, \@paths) : {};
    write_file("$dir/step_params.json", $json->encode(\%params));
    write_file("$dir/ws_meta.json", $json->encode($meta));
    my $out = "$dir/pipeline.json";
    my($ok, $stdout) = modpipe("step-pipeline", "$dir/step_params.json", "--ws-meta", "$dir/ws_meta.json", "--out", $out);
    if (!$ok)
    {
        my $res = eval { decode_json($stdout) };
        my $errs = $res ? join("\n  ", @{$res->{errors}}) : ($stdout // '');
        die "Invalid ModularStep parameters:\n  $errs\n";
    }
    return $out;
}

sub preflight
{
    my($app, $app_def, $raw_params, $params) = @_;
    my $tmp = File::Temp->newdir();
    return preflight_for($app, step_pipeline($app, $raw_params, "$tmp"));
}

sub run_step
{
    my($app, $app_def, $raw_params, $params) = @_;
    my $file = step_pipeline($app, $raw_params, Cwd::getcwd());
    my $res = run_and_upload($app, $file);
    return { module => $raw_params->{module}, outputs => $res->{outputs}, values => $res->{values} };
}
