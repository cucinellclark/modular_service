# Open Questions

## Decided (2026-11-02)
- Modules = **underlying tools**, not whole services.
- **Perl shell (AppScript) + Python core.**
- Pipelines authored by **both** devs (curated templates) and end users (builder).
- Execution backend: **generated Snakemake** (7.32.4 in container) behind an
  executor interface, with a simple local runner for dev/tests. Nextflow was
  considered and rejected for now (see ARCHITECTURE §4).
- **No whole-service nodes**: tool modules only.
- **Scatter/gather over samples is in v1.**
- Tools missing from the container: modules may name a **separate source
  environment** for now (`environment:` field). Long term, only tools in the
  container are allowed, and such modules are flagged until they are.

## Decided (2026-11-03)
- Types: **own dotted names + EDAM cross-refs**; **compression is an attribute**, handled automatically.
- Databases: **installed DBs are registry parameters** (`resources/databases.yaml`); **pipeline-built DBs and
  indexes are typed ports**.
- ~~RASTtk steps will be tool modules~~ **Deferred (2026-11-03)**: RASTtk is too complex for now. `annotation.gto` stays in
  the type vocabulary so it can be added later without redesign.
- Formats: **YAML module descriptors, JSON pipeline definitions** (pipelines are submitted as app params).
- Commands: **Jinja2 templates** for simple tools, **Python adapters** for complex ones (SPAdes recipes, RASTtk).
- **Annotated genomes are always indexed** (*deferred with RASTtk; nothing produces GTOs yet*): any RASTtk-annotated GTO a pipeline outputs is loaded into BV-BRC
  as a private genome, as the Genome Annotation service does.
- First UI: a **template picker** (curated pipelines in a form, like existing service forms); graph builder later.
- Resources: **capped like the big services** (about 32 CPUs, 256 GB, 48 h per pipeline job). A step that needs
  a large Kraken2 DB routes the whole job to the `kraken_db` partition. Preflight requests the max over steps
  (CPU, memory) and the critical-path sum (runtime).
- Versioning: **pin and warn**. A saved pipeline records each module's descriptor version and tool version.
  Re-runs use the current container and warn if a tool version changed; an incompatible descriptor version
  blocks the run until the pipeline is updated.

## Decided (2026-11-03, UI)
- Test UI: a **Dojo page in BV-BRC-Web** (like the production service forms), on the development branch
  `modular-pipeline-ui`. It talks to the prototype **modpipe API** (`bin/modpipe serve`) because the app isn't
  registered with the app service. On dev-5 the API is reached as `https://dev-5.bv-brc.org`, an nginx/Cloudflare
  proxy that forwards plain HTTP to `ash:12005`.
- Graph editor (docs/GRAPH_EDITOR_PLAN.md):
  - a custom HTML/SVG canvas, not Cytoscape;
  - a **mode on the same page** as the form;
  - users can build pipelines **from scratch**;
  - custom pipelines are saved as **JSON files in the workspace**, by default in **`/<user>/home/pipeline`**, and
    are listed as "[my pipelines]" next to the templates.

## Resolved by investigation (2026-11-03)
- **Workspace types**: `reference/workspace_types_known.json` (71 types) combines the 2021 registered list,
  types observed in production (QA outputs plus a 30k-object user workspace) and the bvbrc-mcp enum. The
  only addition since 2021 is `pdb`. `graph` (in the MCP enum) is not a real type and is excluded.
- **Data image**: use the most recent complete image, `patric-data-2022-0119` (decided 2026-11-03). The newer
  `patric-data-2022-0907.build` is an unfinished build dir. If production turns out to use a different
  image, update the `binds.data_image` entry in `resources/databases.yaml`.
- **RASTtk `--url`**: `rast-*` commands build a `GenomeAnnotation::Client`, which defaults to the remote service
  `http://pecan.mcs.anl.gov:7050`. The BV-BRC Genome Annotation service instead runs the same steps in-process
  via `Bio::KBase::GenomeAnnotation::GenomeAnnotationImpl` (GenomeAnnotationCore.pm). RASTtk modules should
  use a small local wrapper around `GenomeAnnotationImpl`, not the CLI.
- **Commented app spec**: `ComprehensiveSARS2Analysis.json` has `#` comments; `tools/summarize_app_specs.py`
  strips them. Nothing to decide.

## Decided (2026-11-05, execution through GoWe)
- **Per-tool execution via GoWe**: every module is registered as its own GoWe workflow (a generated CWL tool), and
  pipelines are CWL workflows chaining them. Each tool runs the new **`ModularStep`** BV-BRC app (one module per
  job), which is how it will run in production (GoWe's BV-BRC executor, `bvbrc_app_id: ModularStep`). Until the app
  is registered with the BV-BRC scheduler, the same app runs on a GoWe worker. Built first: the app itself
  (docs/SERVICE.md), then `modpipe export-cwl` (docs/GOWE.md). Next: `modpipe compile`, then a GoWe server + workers on
  ash.
- `ModularPipeline` (whole pipeline in one job) stays.

## Open: the user's decision
- **Verify tokens in the modpipe API** (offered 2026-11-03; no answer yet). The API trusts the token's `un=` field.
  Behind dev-5 it is internet-reachable, so a forged token could queue jobs (they fail at staging) and list
  another user's jobs. The fix is to check each token with BV-BRC before use.

## Open: needs someone outside this project
- **Undeclared app params**: ModularStep takes each port/parameter as a top-level key that the app spec doesn't
  declare. AppScript keeps them (`raw_params`, with a warning; seen 2026-11-05); whether `AppService.start_app` passes undeclared keys through needs
  confirming with the BV-BRC maintainers. Fallback: nested `inputs`/`params` objects.
- **Going live**: container build with this module, and app registration with the app service (BV-BRC maintainers).
  The prototype API and its direct Slurm submission are then replaced by `AppService.start_app2`.

## Follow-ups (for us, no decision needed)
- **Indexing mechanism** (deferred with RASTtk): find how Genome Annotation loads a GTO into Solr (its
  `skip_indexing` / `indexing_url` params; `genomeObj2solr.pl` / `complete-load.pl` in app_service).
- **RASTtk in-process wrapper** (deferred): `rast-*` CLIs default to the remote annotation service; modules
  would need a local `GenomeAnnotationImpl` wrapper.
- **Graph editor M5 polish**: minimap, help page in the site docs.
- **Resource cap numbers**: confirm the 32 CPU / 256 GB / 48 h cap against the largest current services'
  preflight values, and against Slurm partition limits.
