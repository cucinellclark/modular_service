# Running modules through GoWe

Decided 2026-11-05 ([OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)): every module is its own GoWe workflow (a CWL
CommandLineTool), and pipelines are CWL workflows that chain them. Each tool runs the **ModularStep** BV-BRC app
([SERVICE.md](SERVICE.md#modularstep-parameters)), one module per job. Data moves between steps as workspace
output folders tagged with `modpipe_*` metadata. modpipe still validates; GoWe only schedules.

GoWe: `~/bvbrc-dev/Copilot/Agents/GoWe` (docs there: `README.md`, `SPECIFICATION.md`, `docs/cwl-hints.md`).

## `modpipe export-cwl`

```bash
bin/modpipe export-cwl --out cwl/tools                 # all 51 modules, worker mode
bin/modpipe export-cwl --mode bvbrc --out DIR fastp    # once ModularStep is registered with the BV-BRC scheduler
```
Options: `--image` (Apptainer image, default `singularity_container_ref.txt`), `--modpipe-home` (this checkout's
path on the worker, default this checkout). `cwl/tools/` is generated (git-ignored): it embeds those paths.

Tool shape (`lib/modpipe/cwl.py`):

| CWL input | from | type |
|---|---|---|
| `module` | the module id | `string`, fixed default |
| one per input port | the descriptor's `inputs` | `Any` (`["null", "Any"]` if optional). A workspace path, a `ws://` File/Directory (an earlier step's output), a list, or a source object. The modpipe type is in `doc` and `modpipe:type`. |
| one per parameter | `parameters` | `int` / `float` / `boolean` / `string` / `enum`, optional, module default as CWL default; `database` params list the registry ids in `doc` |
| `input_types` | | `Any?` |
| `output_path`, `output_file` | framework | `string` |

Outputs: one `Directory?` per output port, the port folder `ws://<output_path>/.<output_file>/<port>`. A port folder
holds the value itself, or one value folder per sample; ModularStep accepts either as an input (a port folder is
expanded into its sample folders).

Port types are `Any` on purpose. CWL's File/Directory can't express modpipe types (paired reads, BAM+index, abstract
ports), and the step is validated again inside the job (`modpipe step-pipeline`). `modpipe compile` will run the
full pipeline validation before submitting.

No tool `id`: GoWe up to 0.26.1 files an unbundled tool under its `id`, so a workflow step's `run: tools/x.cwl` then
doesn't resolve ("run reference not found in $graph"). Fixed on the GoWe `modular-step` branch (93ec029, which also
makes `cwl-runner validate` print the field errors); leaving `id` out works with both. The module id is in
`modpipe:module`.

### Worker mode (now)

```yaml
hints:
  gowe:Execution: {executor: worker, worker_group: modpipe, inject_bvbrc_token: true}
  DockerRequirement: {dockerPull: /vol/patric3/production/containers/ubuntu-176-build12-2.sif}
requirements:
  NetworkAccess: {networkAccess: true}            # Workspace / data API
  ResourceRequirement: {coresMin: <cpu>, ramMin: <MB>}   # from the descriptor's resources
  EnvVarRequirement: {envDef: {MODPIPE_HOME: <checkout>}}
  InitialWorkDirRequirement: {listing: [{entryname: job.json, entry: $(JSON.stringify(inputs))}]}
baseCommand: [<checkout>/bin/modpipe, cwl-step, job.json]
arguments: [--cores, $(runtime.cores), --ram-mb, $(runtime.ram)]
```

`modpipe cwl-step` (inside the container):
1. turns the CWL job into ModularStep params: File/Directory objects become their path (`ws://` stripped), nulls
   are dropped;
2. runs `App-ModularStep.pl` in `./app` with `P3_ALLOCATED_CPU`/`P3_ALLOCATED_MEMORY` from the CWL runtime and the
   token GoWe injects (`BVBRC_TOKEN`/`KB_AUTH_TOKEN`; never logged);
3. reads the app's local `modpipe_step_result.json` and writes `cwl.output.json` (one `ws://` Directory per
   produced port); exits non-zero if the app failed.

The worker needs: the image, this checkout and the BV-BRC data folders bind-mounted (`--extra-bind`), network
access, and the user's token. GoWe only injects the token into tools an admin has **blessed** (digest of the tool
document + pinned image sha256; ADR-0012), or into any tool in `--token-blessing=dev` mode. The blessing does not
cover this checkout's code, which is bind-mounted rather than in the image: acceptable for a dev server, and not
an issue in bvbrc mode.

### bvbrc mode (production)

`hints: {gowe:Execution: {executor: bvbrc, bvbrc_app_id: ModularStep}}`, no container or shim: GoWe's BV-BRC
executor passes the inputs to `AppService.start_app` as top-level params (File/Directory -> workspace path).
Directory outputs: GoWe branch **`modular-step`** (commit 03eff9f, in `~/bvbrc-dev/Copilot/Agents/GoWe`) resolves
an output typed `Directory`/`Directory?` with a plain-name glob to `ws://<result folder>/<glob>` when that folder
exists. Before it, the executor matched output *file names* against globs and always made Files, so per-port
folders couldn't be returned. Also unconfirmed: whether `start_app` passes undeclared params through (OPEN_QUESTIONS.md).

## The GoWe server on ash (`:12007`)

`~/GoWeServer/start_gowe_alpha.sh` starts `bin/gowe-server` from `~/bvbrc-dev/Copilot/Agents/GoWe` (branch
`modular-step`). Set up for modpipe (2026-11-06):
- `--worker-keys ~/GoWeServer/worker-keys.json`: workers must present a key (id `modpipe-slurm`, group `modpipe`);
  the worker side reads `~/GoWeServer/modpipe-worker.key` (mode 600, outside every bind mount). Checked: no key or
  a wrong key -> 401.
- Tools registered as `modpipe-<module>` (51), next to the 30 Copilot workflows:
  `bin/modpipe export-cwl && GOWE_SERVER=http://localhost:12007 deploy/gowe/register_tools.py`. Registration is
  append-only: unchanged tools dedup, changed ones become a new version under the same name. The token comes from
  `MODPIPE_TOKEN_FILE` (default `~/.patric_token`), never argv.
- Parsed hints: `executor: worker`, `worker_group: modpipe`, `inject_bvbrc_token: true`, the production image.
- Releases (`deploy/gowe/release.sh`, below) register and bless the tools; then start workers
  (`GOWE_SERVER=http://ash.cels.anl.gov:12007 GOWE_WORKER_KEY_FILE=~/GoWeServer/modpipe-worker.key sbatch
  deploy/gowe/worker.sbatch`) and submit.

### Releases and blessing

A blessing pins the tool document and the image sha256, but the code the tools run is bind-mounted from outside
the image. So tools are only blessed for an immutable snapshot of a commit:

```bash
deploy/gowe/release.sh --dry-run    # checks + plan, changes nothing
deploy/gowe/release.sh              # gowe prompts once per tool after printing its review report
deploy/gowe/release.sh --yes        # no prompts (reports are still saved in the release)
```
1. checks: clean checkout, HEAD pushed, unit tests, GoWe healthy, `gowe` CLI logged in
   (`~/.gowe/credentials.json`; `bin/gowe login < ~/.patric_token`);
2. `git archive HEAD` -> `~/GoWeServer/modpipe/releases/<sha>/`, made read-only (reused if it exists);
3. sha256 of the production image (cached in `~/GoWeServer/modpipe/image-sha256/`);
4. `export-cwl --modpipe-home <snapshot>` into `<snapshot>/cwl/tools`, so the commit is part of each tool;
5. register (`register_tools.py --json-out <snapshot>/registered.json`);
6. `gowe admin bless <wf id> --image-sha256 <sha> --groups modpipe --note "modpipe <sha>"` per tool, by workflow
   id (a name means "newest version"); reports in `<snapshot>/bless/`;
7. `<snapshot>/RELEASE.json`; `~/GoWeServer/modpipe/current` -> this release.

Submitting `modpipe-<module>` by name runs the newest registered version, i.e. the latest release. Older blessings
stay valid (each points at its own frozen snapshot); revoke with `gowe admin unbless` if wanted. Workers bind
`~/GoWeServer/modpipe/releases` (not the working checkout). Tested 2026-11-06 on a throwaway base: the snapshot is
fully read-only, all tools validate, the engine runs from it without writing.

## Testing without a GoWe server

`tests/cwl/run_cwl.sbatch <tool-or-workflow.cwl> <job.json>` runs GoWe's standalone `cwl-runner` with Apptainer on a
compute node, the way a worker would: production image, repo + BV-BRC data bound, the user's token injected
through a mode-600 `--env-file`. Compute nodes have `singularity` (3.10) but no `apptainer`; the script links one to
the other.

Server-side staging (`--workspace-staging server`, as on the ash server) only pre-stages `ws://` File/Directory
objects in a submission's *top-level* inputs. Give pipeline inputs as plain workspace paths or source objects (as
`modpipe compile` will), so the steps get the paths themselves; `ws://` Directories passed between steps are not
staged.

| test | exercises |
|---|---|
| `cwl1_mafft.json` on `mafft.cwl`, then `cwl2_fasttree.json` on `fasttree.cwl` | a tool end to end; a `ws://` Directory output fed to the next tool as-is |
| `reads_chain.cwl` + `reads_chain.json` | hand-written 3-step workflow (fastp -> minimap2 -> samtools coverage) passing port folders; preview of `modpipe compile` |

Results 2026-11-05:
- mafft and fasttree OK via cwl-runner (outputs reported as `ws://` Directories; fasttree took mafft's Directory).
- `reads_chain.cwl` OK: each step got the previous step's *port* folder and expanded it to the `SRR2838702` sample
  folder; same coverage numbers as the ModularStep chain (SERVICE.md). The first attempt failed in ReadSet: NCBI
  returned no SRA metadata (it worked on retry, and in both container modes by hand), so treat it as transient;
  GoWe's task retries cover it.
- AppScript only *warns* about params missing from the app spec ("provided in the job submission but not
  specified in the app spec") and keeps them in `raw_params`.

## Next
1. `modpipe compile`: validated pipeline -> CWL workflow over these tools (scatter for sample collections, a
   per-step `output_file`, `input_types` from the plan's resolved types).
2. A dev GoWe server on ash with workers as Slurm jobs (`--token-blessing=dev`), tools registered by name.
3. The UI's submit goes to GoWe.
