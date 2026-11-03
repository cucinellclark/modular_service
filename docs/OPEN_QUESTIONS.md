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

## Open: needs someone outside this project

None.

## Follow-ups (for us, no decision needed)
- **Indexing mechanism** (deferred with RASTtk): find how Genome Annotation loads a GTO into Solr (its
  `skip_indexing` / `indexing_url` params; `genomeObj2solr.pl` / `complete-load.pl` in app_service).
- **RASTtk in-process wrapper** (deferred): `rast-*` CLIs default to the remote annotation service; modules
  would need a local `GenomeAnnotationImpl` wrapper.
- **Resource cap numbers**: confirm the 32 CPU / 256 GB / 48 h cap against the largest current services'
  preflight values, and against Slurm partition limits.
