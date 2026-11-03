# Deployment

ModularService is a standard dev_container module (Makefile on `tools/Makefile.common(.rules)`).

## What `make deploy-service` installs into `$(TARGET)` (e.g. /opt/p3/deployment)
| Path | From | Purpose |
|---|---|---|
| `bin/App-ModularPipeline` | `service-scripts/App-ModularPipeline.pl` (wrap_perl; source in `plbin/`) | the service script the scheduler runs |
| `bin/modpipe` | `scripts/modpipe.py` (wrap_python3; source in `pybin/`) | the engine CLI the shell calls |
| `lib/modpipe/` | `lib/modpipe/` | Python package (needs PyYAML + Jinja2; both are in the container's python3) |
| `services/app_service/app_specs/ModularPipeline.json` | `app_specs/` | app definition |
| `services/modular_pipeline/{modules,types,resources,pipelines}` | repo dirs | module descriptors, type system, DB registry, curated templates |
| `services/modular_pipeline/reference/tools/index.json`, `.../workspace_types_known.json` | `reference/` | tool versions (provenance), known workspace types |
| `services/modular_pipeline/DEPLOYED_AT` | | deployment timestamp |

At run time `modpipe` finds its data via `MODPIPE_REPO` if set, else a source checkout next to `lib/`, else
`$KB_TOP/services/modular_pipeline` (then `/opt/p3/deployment/services/modular_pipeline`). The Perl shell finds the
CLI via `MODPIPE_HOME`, else `<script dir>/../bin/modpipe`, else `$KB_TOP/bin/modpipe`.
Nothing under `tests/` or `reference/tools/*/runs` is deployed.

## Commands
```bash
# inside a dev_container checkout (modules/ModularService), after `source user-env.sh`:
make                     # dev wrappers in $KB_TOP/bin pointing at the checkout
make test lint           # unit tests, module lint, type checks, template validation
make deploy-service TARGET=/opt/p3/deployment DEPLOY_RUNTIME=/opt/patric-common/runtime

# from elsewhere (as tested 2026-11-03):
source /path/to/dev_container/user-env.sh
make TOP_DIR=/path/to/dev_container TARGET=/tmp/deploy DEPLOY_RUNTIME=/opt/patric-common/runtime deploy-service
```
For a scratch TARGET that isn't the container's own `/opt/p3/deployment`, set
`KB_OVERRIDE_PERL_PATH=$TARGET/lib:/opt/p3/deployment/lib` so the wrapper also sees the BV-BRC Perl libraries
(AppScript, ReadSet, P3DataAPI, Workspace client).

## Verified (2026-11-03)
- Deployed into a scratch TARGET; inside the production container the deployed `bin/modpipe` listed templates and
  validated a deployed template; the deployed `bin/App-ModularPipeline` passed preflight and ran a real job
  (feature group -> MAFFT -> FastTree), saving outputs to the workspace, using only deployed files.
- `make test` (43 tests), `make lint` (20 modules, 9 templates), and `make bin` (dev wrappers) pass.

## Going live (needs the BV-BRC maintainers)
1. Put the repo under version control and add it to the module list used to build the production deployment and
   container (the container bakes `/opt/p3/deployment`).
2. Register the app with the app service (app specs are loaded from `services/app_service/app_specs`, e.g. by
   `p3x-load-app-specs`).
3. Check data paths on the production nodes: `resources/databases.yaml` binds
   (`/vol/bvbrc/production/application-backend`, metagenome DBs, data image `patric-data-2022-0119`).
4. Optional: UI. `modpipe list-templates --json` gives a template-picker form definition.
