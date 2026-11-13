# Test UI: BV-BRC-Web "Modular Pipeline" page (form + graph editor) + modpipe API

The page is a normal BV-BRC-Web service page (Dojo, `AppBase`, the same workspace selectors as every
service). It lives on the BV-BRC-Web branch **`modular-pipeline-ui`** (`cucinellclark/bvbrc_website`, based on
`beta-stage`; the working checkout is `~/bvbrc-dev/Deployment/BV-BRC-Web`). It has three modes that share one
pipeline: **Template form**, **Graph editor** and **JSON**.

| file (BV-BRC-Web) | role |
|---|---|
| `public/js/p3/widget/app/ModularPipeline.js` + `templates/ModularPipeline.html` | page (route `/app/ModularPipeline`): modes, form, output folder, Run, job list |
| `public/js/p3/widget/modpipe/GraphEditor.js` | graph editor: palette, canvas, inspector, live check, workspace save/open |
| `public/js/p3/widget/modpipe/PipelineModel.js` | pipeline JSON model: edits, undo/redo, layout, overlap avoidance (UMD, no DOM) |
| `public/js/p3/widget/modpipe/TypeLogic.js` | instant connection rule, mirrored from `types.py` (UMD) |
| `public/js/p3/widget/modpipe/SourceEditor.js`, `ParamEditor.js` | input-source and parameter widgets shared by form and editor |
| `public/js/p3/widget/modpipe/modpipe.css` | editor styles (loaded by the editor itself) |
| `tests/modpipe/model_test.js` | Node tests for the model (run by `tests/unit/test_compat_parity.py`) |
| `app.js`, `p3-web.conf.sample` | config `modularPipelineServiceURL` (default `http://localhost:8765`) |
| `views/bv-brc-header.ejs` | Services menu > Prototype > Modular Pipeline |

Because the ModularPipeline app is not registered with the production app service, the form talks to a
small **modpipe API** (`bin/modpipe serve`, `lib/modpipe/api.py`) that lists templates, validates, and submits
jobs. Two backends:
- `--backend slurm` (default): one Slurm job on this host running App-ModularPipeline, exactly like
  `tests/app/run_app.sbatch`.
- `--backend gowe --gowe-server http://localhost:12007`: `modpipe compile` + submit to the GoWe server as the user
  (one ModularStep job per step on GoWe workers; [GOWE.md](GOWE.md)). The token goes to GoWe in the request and is
  never written to disk here; GoWe verifies its signature. Needs a release (`deploy/gowe/release.sh`) and a running
  worker. Data must be in the workspace (no `fixture` sources).

Jobs run with the signed-in user's BV-BRC token and write to their workspace.

## Workbench (redesign decided and built 2026-11-13)

The page was an `AppBase` service form (template form / graph / JSON modes in one narrow column, a Validate button,
one Output Folder + Output Name, a job table at the bottom). That fits "fill a form, submit one job"; a GoWe run is a
set of steps with their own state, log and outputs. Decisions (all four recommendations accepted):
1. **Standalone full-width page**, no `AppBase` (still `/app/ModularPipeline`: the router instantiates
   `p3/widget/app/ModularPipeline` with `region: 'center'`; any widget works).
2. **One pipeline, no modes**: a template opens as a graph plus a run-setup panel; JSON is a dialog.
3. **One folder per run**: steps write to `<folder>/<run name>/.<step>/<port>/` (the Workspace creates the missing
   run folder with the first step's result folder; checked).
4. **GoWe only** on the new page (the API keeps `--backend slurm` for the old flow).

Three views (tabs):
- **Pipelines** (start): template cards by category (label, description, step chain), "Open saved pipeline",
  "Blank pipeline", recent runs.
- **Build**: full-width graph editor (palette hidden until "Edit steps"); the right panel is the inspector for a
  selection and the **run setup** when nothing is selected: inputs (data editors), the template's exposed options
  (`ui.expose`) and optional steps (`ui.optional`), results folder + run name (with the resulting path), live check
  summary (errors, notes, jobs, resources) and **Run** (enabled only when the check passes). Save / Save as / JSON.
  The header always shows the run status and a **Run** button too (a selected step or input replaces the run-setup
  panel): it submits when everything is set, otherwise opens the run setup and names what is missing. Inspectors
  have a "‹ Run setup" link back.
- **Runs**: list of the user's runs; the selected run shows its steps colored by state with timing, per-step log
  and output folders, the pipeline outputs, Cancel, "Open in Build" (rerun with changes), and the run folder. Polls
  every 10 s while active; Run opens the new run here.

API additions: `GET /api/jobs/<id>` (per-step tasks and outputs, the submitted pipeline), `POST /api/jobs/<id>/cancel`,
the job record keeps the pipeline; a run name already used in the folder is refused.

Code (BV-BRC-Web): `p3/widget/app/ModularPipeline.js` (shell, tabs, Pipelines, Build), `modpipe/RunSetup.js` (the
run-setup panel), `modpipe/RunsView.js`; the graph editor runs with `embedded: true` (toolbar keeps layout/zoom/undo,
`owner.renderRunSetup` when nothing is selected, `owner.onCheck` per check, `setPaletteVisible`, `saveInPlace`).
Template exposed parameters travel as `ui.expose` (API `template_pipeline`; the model keeps them through step
renames/removal; the engine accepts the key). The results folder is remembered in `localStorage`; the default run
name is `<pipeline slug>_<yyyymmdd>_<hhmm>`; a run name already used in the folder is refused (409).

Tested 2026-11-13 in the headless harness against a test API (`--backend gowe`) and the real GoWe server: Pipelines
(17 cards), open a template, choose data, live check, inspector <-> run setup, Edit steps, Run -> Runs view polling to
COMPLETED (align/tree, 31 s, `ModularService_tests/wb_test_141517/.align/ .tree/`), per-step logs and outputs; a
template with an optional step and exposed options; the blank pipeline.

## Running it
1. On the cluster host (where Slurm and the container are), start the API from the ModularService checkout:
   ```bash
   bin/modpipe serve --port 8765            # allowed site origins default to https://dev-5.bv-brc.org and http://localhost:3000;
                                            # pass --origin <scheme://host[:port]> (repeatable) for others
   bin/modpipe serve --port 8765 --backend gowe --gowe-server http://localhost:12007   # submit through GoWe
   ```
   Job state lives in `~/.modpipe-ui/` (job params, Slurm logs; token files are mode 600 and deleted when the job ends;
   with the GoWe backend: the compiled workflow and job.json per job, no token). The workbench page needs
   `--backend gowe` (it says so in a banner otherwise), a release (`deploy/gowe/release.sh`) and a running worker.
2. If the browser is on another machine, either tunnel the port (`ssh -L 8765:localhost:8765 <cluster host>`)
   or serve on the network over HTTPS so the token isn't sent in the clear:
   ```bash
   bin/modpipe serve --host 0.0.0.0 --port 12005 --self-signed
   ```
   `--self-signed` creates a certificate for this host once (`~/.modpipe-ui/tls/`, key mode 600). Open
   `https://<host>:12005/api/health` in the browser once and accept the warning; after that the form's calls work.
   A website served over https (e.g. https://dev-5.bv-brc.org) can only call an https API. With a real certificate use `--tls-cert cert.pem --tls-key key.pem` instead. Set
   `modularPipelineServiceURL` to `https://<host>:12005`.
3. Run BV-BRC-Web from the `modular-pipeline-ui` branch with your `p3-web.conf` (add
   `"modularPipelineServiceURL": "http://localhost:8765"` if you need a different URL). Run it **unbuilt**
   (development mode): the new widgets aren't in the built release layers.
   **dev-5 setup:** `https://dev-5.bv-brc.org` is an nginx/Cloudflare proxy that forwards plain HTTP to
   `ash:12005`. Run `bin/modpipe serve --host 0.0.0.0 --port 12005` (no TLS; the proxy terminates HTTPS) and set
   `modularPipelineServiceURL` to `https://dev-5.bv-brc.org`.
4. Sign in, open **Services > Prototype > Modular Pipeline** (`/app/ModularPipeline`).

## Graph editor
Pick **Graph editor** at the top of the page (code: BV-BRC-Web `public/js/p3/widget/modpipe/`). The first time, it opens
the template that is selected in the form, with the inputs, options and parameters chosen there. Its own toolbar can
load any template, start a new pipeline, and open or save pipelines in the workspace (JSON files with their layout).
Custom pipelines are saved by default to the user's **`/<user>/home/pipeline`** folder, which is created the first time
the Save dialog opens. Pipelines in that folder are listed as "[my pipelines]" in the editor's template dropdown and at
the top of the Open dialog. Saving a pipeline that was opened from the workspace saves back to the same file
(overwrite pre-ticked). The folder name is `PIPELINE_FOLDER` in `GraphEditor.js`.

- **Palette** (left): tools by category with a search box. Drag a tool onto the canvas, or click it. When an output port is
  selected, the palette shows only the tools that can use that output, and clicking one adds it already connected.
- **Wiring**: drag from an output port (right side of a node) to an input port. While dragging, inputs are colored:
  green (fits), blue (fits through an automatic converter), amber (may fit, depending on the actual input) or grey
  (refused, with the reason as a hint). Cycles are refused. Right-click an output port, or drop a connection on empty
  canvas, to list the tools that fit. Selecting a connection shows its types; Delete removes it.
- **Inspector** (right): the selected step's parameters (typed, pattern-checked), its inputs (with "create pipeline input"
  for unconnected ports), and the outputs to save to the workspace. For a pipeline input it shows the data source picker
  (same choices as the form). Optional template steps get an on/off switch.
- **Live check**: about half a second after each edit, the server validates the pipeline (`POST /api/validate`).
  Problems appear as badges on the step or port they concern, steps that run once per sample show "×N per sample",
  converters the engine will insert show as dashed "auto" connections ("Make explicit" turns one into a step), and the
  status bar shows the resource estimate. Run is the page's normal Run button.
- Undo/redo (Ctrl+Z / Ctrl+Shift+Z), Delete, scroll to zoom, drag the background to pan, Auto-layout, Fit.

**JSON** shows the graph's pipeline as text; edits apply to the graph when you switch back.

Editor state lives in the pipeline's `ui` key (`positions`, `disabled`, `optional`, `links`), which the engine accepts:
`ui.disabled` steps are removed with their `ui.optional.<step>.bypass` rewiring (`pipeline.apply_ui`), the rest is ignored.

Checks run twice: instantly in the browser while drawing (`TypeLogic.js`, `PipelineModel.canConnect`) and authoritatively
on the server. `tests/unit/test_compat_parity.py` checks that both give the same answer for every module output/input
pair, and runs the editor's model tests (`tests/modpipe/model_test.js` in BV-BRC-Web) on the real catalog and templates
(set `MODPIPE_WEB_DIR` if the website checkout isn't at `~/bvbrc-dev/Deployment/BV-BRC-Web`).

## Using the old form (Slurm backend; replaced by the workbench)
- **Template**: 17 curated pipelines grouped by category; the step chain is shown under the description.
- **Inputs**: per input, pick a source (workspace read pairs per sample, SRA accessions, workspace file(s),
  BV-BRC genome IDs/group, feature group/IDs, pasted FASTA, bundled reference). Collections get "+ Add sample".
- **Options**: optional steps (checkboxes) and the template's exposed parameters (typed widgets; string
  parameters enforce their allowed pattern; database parameters list registry choices).
- **Validate**: server-side check: errors, notes (e.g. auto-inserted converters), estimated CPUs/memory/runtime.
- **Run**: submits; the **My Modular Pipeline jobs** panel (auto-refresh 20 s) shows Slurm state, pipeline
  status, a link to the result folder and the job log. GoWe backend: the GoWe submission state with step progress
  (`RUNNING (1/3 steps)`), a link per pipeline output, and the log as each step's tail.

## API
`GET /api/health | /api/templates | /api/templates/<name> | /api/catalog | /api/source_options?type=&collection= |
/api/modules | /api/databases?type=`, `POST /api/instantiate | /api/validate`,
`POST /api/submit` (auth), `GET /api/jobs` (auth), `GET /api/jobs/<id>/log` (auth). See `lib/modpipe/api.py`;
tests in `tests/unit/test_api.py`.

Prototype limits:
- **Tokens are not verified.** The user is read from the token's `un=` field. The workspace and data APIs still
  enforce access, so a forged token can't read or write anyone's data. But it can submit jobs to our Slurm account
  (they fail at staging) and list another user's jobs. Through dev-5 the API is reachable from the internet, so run
  it only while testing. Verifying tokens with BV-BRC is the planned fix (OPEN_QUESTIONS). With the GoWe backend,
  submissions, status and logs go to GoWe with the user's token, and GoWe verifies its signature (a forged token
  gets 401); only this API's own job list (names, ids) still trusts `un=`.
- A user only sees their own jobs, and jobs run as the Unix user that runs `modpipe serve`.
- The state directory (`MODPIPE_UI_STATE`, default `~/.modpipe-ui`) must be on a filesystem compute nodes can
  see (`/home`, not `/tmp`): the job reads its params and writes its Slurm log there.

## Testing the page without running the website
`node --check` and the Node model tests cover the plain JS. For the widgets, a headless browser works:
1. Install Playwright into a scratch venv (`pip install playwright`) and use the cached
   `~/.cache/ms-playwright/chromium_headless_shell-*` browser via `executable_path`.
2. Make a static page whose `js/` directory links Dojo/dijit/dojox/etc. from a checkout that has its submodules
   (`~/bvbrc-dev/Copilot/Agents/bvbrc_website/public/js`), with `js/p3` pointing at the branch's `public/js/p3`.
3. Set `window.App` (token, `docsServiceURL`, `user`, `modularPipelineServiceURL`) and stub `WorkspaceManager.api`
   (plus `getObject`/`create`/`createFolder`/`getFolderContents` for an in-memory workspace; preset
   `WorkspaceManager.userWorkspaces`, which the site loads at startup, or the folder picker recurses), then instantiate
   `p3/widget/app/ModularPipeline` or `p3/widget/modpipe/GraphEditor`. Workspace items a pipeline uses (e.g. a feature
   group) must exist in the in-memory workspace, or the data editor reports "choose a workspace item". For a real
   run, inject the token from the test process (Playwright `add_init_script`), never into a file.
4. Run a test API with a fake `sbatch`/`sacct` on its PATH, so Run doesn't reach Slurm.

Known noise in that setup: `registry.byClass is not a function` comes from existing site code and is not an error on
the real site.
