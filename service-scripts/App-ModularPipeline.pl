#
# App-ModularPipeline: run a modpipe pipeline (connected tool modules) as a BV-BRC job.
#
# The Perl shell does the BV-BRC-specific parts (lib/ModularPipeline/AppCommon.pm, shared with App-ModularStep);
# the Python core (bin/modpipe) does the rest:
#   preflight : modpipe instantiate (templates) + modpipe validate --json  ->  cpu / memory / runtime / partition
#   run       : stage inputs (ReadSet for reads incl. SRA, workspace files, genome & feature groups via the data API)
#               -> modpipe run (Snakemake) -> upload each output value with its workspace types and metadata
#               -> save pipeline.json, pipeline_run.json (provenance) and outputs.json
#
# Params (app_specs/ModularPipeline.json): pipeline | pipeline_template (+ inputs, template_params),
# keep_intermediates, output_path, output_file.
#
use strict;
use warnings;
use FindBin;
use lib "$FindBin::RealBin/../lib";
use Bio::KBase::AppService::AppScript;
use File::Slurp;
use Cwd ();
use File::Temp;
use JSON::XS;
use ModularPipeline::AppCommon qw(modpipe preflight_for run_and_upload);

my $json = JSON::XS->new->pretty(1)->canonical(1);

my $script = Bio::KBase::AppService::AppScript->new(\&run_pipeline, \&preflight);
# AppScript::run returns the child's raw wait status (e.g. 256 or 65280); `exit` of that would wrap to 0, so
# convert it to a real exit code (failures must not look like success to Slurm or GoWe).
my $status = $script->run(\@ARGV) // 0;
exit($status == 0 ? 0 : ($status >> 8) || 1);

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

sub preflight
{
    my($app, $app_def, $raw_params, $params) = @_;
    my $tmp = File::Temp->newdir();
    return preflight_for($app, resolve_pipeline($params, "$tmp"));
}

sub run_pipeline
{
    my($app, $app_def, $raw_params, $params) = @_;
    my $file = resolve_pipeline($params, Cwd::getcwd());
    my $res = run_and_upload($app, $file, keep_intermediates => $params->{keep_intermediates});
    return { pipeline => $res->{pipeline}, outputs => $res->{outputs} };
}
