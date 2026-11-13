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

Outputs: one per output port, the port folder `<output_path>/.<output_file>/<port>`. A port folder holds the value
itself, or one value folder per sample; ModularStep accepts either as an input (a port folder is expanded into its
sample folders). Worker mode: a `string?`, the plain workspace path. bvbrc mode: a `Directory?` (glob = port id).

Why strings in worker mode (2026-11-09): a GoWe worker stages every File/Directory input. Given a `ws://` Directory
it fails without `--workspace-stager`; with it, it downloads the whole folder and hands the step a *local* path,
which has none of the `modpipe_*` metadata ModularStep types its inputs by ("cannot tell which kind of reads this
is"), and every intermediate (BAMs) would move twice. A string is never staged; the step reads the workspace
itself.

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
3. reads the app's local `modpipe_step_result.json` and writes `cwl.output.json` (the workspace path of each
   produced port, null for the others); exits non-zero if the app failed.

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

## `modpipe compile`

```bash
bin/modpipe compile pipeline.json --out DIR --output-path /<user>@bvbrc/home/folder [--run-name NAME] [--tools DIR]
gowe --server http://localhost:12007 submit DIR/<name>.cwl -i DIR/job.json
```
Validates the pipeline as `modpipe run` does (editor state, automatic converters; stops on errors), then writes
`DIR/<name>.cwl` (name from the pipeline's `name`, `modpipe-<slug>`; GoWe registers it under the file name),
`DIR/job.json` and `DIR/tools`, a symlink to the released tools, resolved (default the release `current` points
at), so the workflow is pinned to a release and `gowe bundle` finds the tools by relative path
(`lib/modpipe/compile.py`):

| pipeline | workflow |
|---|---|
| step | one step running `tools/<module>.cwl` = one ModularStep job. No CWL `scatter`: ModularStep runs a sample collection inside the job (port folder of sample folders, expanded again by the next step) |
| `$inputs.<name>` | workflow input `Any`; `job.json` gives `{type, source[, attributes]}`, so the type is explicit |
| `<step>.<output>` | `<step>/<output>`, the upstream port folder's workspace path |
| `[ref, ...]` (list port) | `source: [...]`, `linkMerge: merge_flattened`, `pickValue: all_non_null` (+ `MultipleInputFeatureRequirement`) |
| step params | fixed step inputs (`default:`); module defaults for the rest |
| `output_path`, `output_file` | the run folder `<--output-path>/<run name>` and the step id: results in `<run folder>/.<step>/<port>/` (one folder per run; the Workspace creates the run folder with the first step's result folder). No expressions, so no workflow-level requirements |
| pipeline outputs | workflow outputs `string?` (workspace folders) |

Refused up front: `fixture` sources (local test data), a module without a released tool or whose released tool has
another module version than this checkout, and a list port fed by refs of different types (ModularStep takes one
type per list port). Steps keep their blessings: the dry run passes the token check with the workflow-level
requirements.

Tested 2026-11-13 through the server (worker on `pear`), test pipelines in `tests/gowe/`:
- `gowe_align_tree.json`: mafft -> fasttree on the rpoB feature group, COMPLETED (~2 min).
- `gowe_reads_qc.json`: fastp (SRR2838702) -> minimap2 (511145.12) -> samtools coverage, plus multiqc over
  `[map.flagstat, cov.stats]` (two sources merged into one list) and `[cov.coverage]`; 4/4 steps COMPLETED in
  ~2.5 min, multiqc got both reports. No token in the task logs.

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
- **Current release (2026-11-06): `21610b109b`**: `~/GoWeServer/modpipe/current -> releases/21610b109b`, 51 tools
  registered and blessed (group `modpipe`, image sha256 `8d36e97e75ab…`), checked with `gowe admin blessings`.
  The 51 tools registered earlier from the working checkout stay unblessed (they never get a token). Three
  blessings from an interrupted release of `c1c7ee334d` (amrfinder, bcftools_call, bcftools_consensus) are still
  active; harmless (by-name submission runs the newest version, and that snapshot is frozen), revoke with
  `gowe admin unbless <tb_id>` if wanted.
- Tools are registered **packed** (`gowe bundle`, as `gowe register` does). A bare tool is wrapped by the server
  with its hints copied onto the step, and a step-level `DockerRequirement` on a token tool is refused at submit
  (`TOKEN_TOOL_OVERRIDE_REFUSED`). Packing doesn't change the tool hash, so the blessings carry over; the 51 packed
  versions are now the newest under each name. Exception: packed mafft is named `mafft` (`wf_4b41977e…`, first
  registered by a `gowe submit --dry-run`), so `modpipe-mafft` by name still resolves to the refused bare version.
- Release `38def09013` (2026-11-13, string outputs) is current, all 51 blessed. The reads chain ran through the
  server (`modpipe-reads-chain`, `reads_chain.cwl` with `run:` pointing at the release's tools): fastp ->
  minimap2 -> samtools coverage COMPLETED, each step given the previous step's workspace path
  (`.gowewf4_*/…/SRR2838702/`), no token in the task logs. `gowe bundle` resolves `run:` paths relative to the
  workflow even when absolute: link the release's `cwl/tools` next to the workflow.
- First runs through the server (2026-11-09, worker Slurm job on `lemon`): `mafft` (feature group ->
  `.gowe1_mafft/alignment`, ~5 min) then `modpipe-fasttree` on that folder given as a plain workspace path
  (`.gowe2_fasttree/tree/tree.nwk`). Both COMPLETED; no token in the task logs.

### Releases and blessing

A blessing pins the tool document and the image sha256, but the code the tools run is bind-mounted from outside
the image. So tools are only blessed for an immutable snapshot of a commit:

```bash
deploy/gowe/release.sh --dry-run    # checks + plan, changes nothing
deploy/gowe/release.sh              # gowe prompts once per tool after printing its review report
deploy/gowe/release.sh --yes        # no prompts (reports are still saved in the release)
```
Run it **on ash**: `GOWE_SERVER` defaults to `http://localhost:12007` (from another host set
`GOWE_SERVER=http://ash.cels.anl.gov:12007`). Without `--yes` it needs a real terminal for the prompts (it reads
`/dev/tty`); Claude Code's `!` commands have none, so use `--yes` there. Blessing gives tools the user's token, so
it is the admin's action (Claude Code's permission check refuses to run it for you). The image hash (37 GB, a few
minutes) is computed once and cached.
1. checks: clean checkout, HEAD pushed, unit tests, GoWe healthy, `gowe` CLI logged in
   (`~/.gowe/credentials.json`; `bin/gowe login < ~/.patric_token`);
2. `git archive HEAD` -> `~/GoWeServer/modpipe/releases/<sha>/`, made read-only (reused if it exists);
3. sha256 of the production image, from/into the workers' digest file `~/GoWeServer/modpipe/image-digests.json`;
4. `export-cwl --modpipe-home <snapshot>` into `<snapshot>/cwl/tools`, so the commit is part of each tool;
5. register (`register_tools.py --json-out <snapshot>/registered.json`);
6. `gowe admin bless <wf id> --image-sha256 <sha> --groups modpipe --note "modpipe <sha>"` per tool, by workflow
   id (a name means "newest version"), only for tools the server still lists as pending
   (`gowe admin blessings --pending`): blessing an already-blessed hash is a `CONFLICT`, so an interrupted
   release can simply be rerun; reports in `<snapshot>/bless/`;
7. `<snapshot>/RELEASE.json`; `~/GoWeServer/modpipe/current` -> this release.

Submitting `modpipe-<module>` by name runs the newest registered version, i.e. the latest release. Older blessings
stay valid (each points at its own frozen snapshot); revoke with `gowe admin unbless` if wanted. Workers bind
`~/GoWeServer/modpipe/releases` (not the working checkout). Tested 2026-11-06 on a throwaway base: the snapshot is
fully read-only, all tools validate, the engine runs from it without writing.

### Worker notes
- **Node runtimes differ**: `lemon` has Apptainer 1.5.3, `fir` only singularity-ce 3.10. GoWe passes the tool
  environment, including the injected token, as `APPTAINERENV_*`, which singularity ignores; with a plain
  `apptainer -> singularity` symlink the token was silently dropped ("cwl-step: no BV-BRC token in the
  environment"). `worker.sbatch` and `run_cwl.sbatch` install `deploy/gowe/apptainer-on-singularity.sh` instead,
  which copies `APPTAINERENV_*` to `SINGULARITYENV_*`. Submit `worker.sbatch` from the repo root (or set
  `MODPIPE_REPO`).
- **Image hash, once**: before injecting the token a worker checks the image's sha256 against the blessing; for
  the 37 GB `.sif` that is ~10 min. GoWe branch `modular-step` adds a persistent cache:
  `gowe-worker --image-digest-file F` reuses a digest recorded for the same image identity (real path, inode, size,
  mtime, ctime; no device number, which differs per NFS client: 80 on ash, 74 on fir, everything else equal) and
  records new ones. `release.sh` step 3 seeds it (`gowe-worker --record-image-digest`), `worker.sbatch` passes
  `~/GoWeServer/modpipe/image-digests.json`. Replacing or modifying the image changes its identity, so it is hashed
  again; the file must be mode 600, owned by the worker uid and outside every bind (checked), since whoever can
  edit it can vouch for an image.
- A failed step's dependents are still dispatched (with null inputs) and fail too; read the first failure.

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

## UI submit through GoWe

`bin/modpipe serve --backend gowe --gowe-server http://localhost:12007` ([UI.md](UI.md)): `POST /api/submit`
validates, compiles into the job's state folder, packs with `gowe bundle`, then registers
(`POST /api/v1/workflows/`) and submits (`POST /api/v1/submissions/`) with the user's token as `Bearer`
(`lib/modpipe/gowe_backend.py`). The run name is the job name with other characters replaced by `_`; a run folder
that already exists is refused (409), since steps would write into it. `/api/jobs`
reads each submission (state, `task_summary`, outputs) and `/api/jobs/<id>/log` each task's stdout/stderr tail,
again as the user. Tested 2026-11-13 with a local API instance: `tests/gowe/gowe_align_tree.json` submitted
through `/api/submit`, COMPLETED (2/2 steps, 31 s), outputs and logs through the API, no token on disk or in
logs; no token -> 401, a `fixture` source -> 400 with the compile error.

## Next
1. Run the UI on dev-5 with `--backend gowe` and submit from the browser.
2. Small: `release.sh` without `--yes` should check for a terminal up front. `~/GoWeServer/modpipe/image-sha256/`
   (the old release cache) is unused and can be deleted.
