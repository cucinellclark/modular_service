# Module descriptor & pipeline schema (v1)

Enforced by `modpipe` (`lib/modpipe/`): `bin/modpipe lint` for modules, `bin/modpipe validate` for pipelines.
Types come from [`types/types.yaml`](../types/types.yaml) and databases from
[`resources/databases.yaml`](../resources/databases.yaml).

## Module descriptor: `modules/<id>.yaml` (`schema: modpipe/module/v1`)

```yaml
schema: modpipe/module/v1
id: fastp                       # unique, [a-z0-9_]+ ; file name must be <id>.yaml
version: 1                      # descriptor MAJOR version (int). Bump on incompatible port/param changes.
label: "fastp: read trimming & QC"
description: "..."
category: read_qc               # free text, used for grouping in UIs
tool:
  id: fastp                     # tool id in tools/tool_list.json (versions from reference/tools/index.json)
  binary: fastp                 # executable actually invoked
  version: 1.3.2                # version the descriptor was written and tested against
environment: container          # default; or the name of a separately sourced environment (temporary)

inputs:                         # ports
  - id: reads
    type: reads.short           # may be abstract on inputs (accepts any descendant)
    required: true              # default true
    cardinality: one            # one (default) | many  (many = gathers a collection / list)
    requires: {}                # attribute constraints, e.g. {alphabet: dna}
    description: "..."

outputs:
  - id: trimmed_reads
    type: reads.short           # abstract allowed only together with type_from
    type_from: reads            # output type = actual type of input port `reads`
    # or: type_from: {port: sequences, map: {sequences.dna: alignment.msa.dna, sequences.protein: alignment.msa.protein}}
    path: trimmed.fastq.gz      # single-file result (relative to the step's work dir)
    parts: {r1: trimmed_1.fastq.gz, r2: trimmed_2.fastq.gz}   # used when the resolved type has parts
    required: true              # default true; false = may legitimately be absent
    when: "params.mode != 'rnaviral'"   # optional Jinja expression; output exists only when true
    attributes: {}              # attributes the output guarantees, e.g. {sorted: coordinate}
    description: "..."

parameters:
  - id: qualified_quality_phred
    type: int                   # int | float | bool | string | enum | database
    default: 15                 # parameters without a default are required unless `required: false`
    min: 0
    max: 60
    enum: [...]                 # for type: enum
    db_type: database.kraken2   # for type: database; value is a registry id of this type (or a descendant)
    pattern: "[A-Za-z0-9_.-]{0,64}"   # string params: required regex (full match); see docs/SECURITY.md
    label: "..."
    description: "..."
    advanced: false             # UI hint: hide behind "advanced"

resources:                      # per-step request; preflight takes max cpu/mem and sums runtime on the critical path
  cpu: 4
  memory: 8G                    # K/M/G/T
  runtime: 1h                   # s/m/h/d, combinable ("1h30m")

command: |                      # Jinja2 template (StrictUndefined); rendered in the step work dir
  fastp -w {{ cpu }} ...
# adapter: modpipe.adapters.spades   # alternative to `command` for complex tools (Python class)

tests:
  discovery_runs: [fastp_pe, fastp_se]   # P4 runs (reference/tools/<tool>/runs/) that lint checks outputs against
  observed: {max_rss_mb: 1163, max_wall_s: 37, note: "Portiera fixtures"}

provenance:
  bvbrc_invocations: [reference_guided_assembly.py]
  nfcore: [fastp]
notes: "..."
```

### Template context
**Pipe every input path, label and string parameter through `| q`.** Lint enforces this with hostile
rendering ([SECURITY.md](SECURITY.md)).

A template renders **one shell command**: its lines are joined with spaces (so arguments may be spread over
lines). Chain several commands explicitly with `&&`. The command runs in the step's work directory.

| name | value |
|---|---|
| `inputs.<port>` | `None` if an optional input is absent. Otherwise a value object: `str()` gives the path; `.r1`/`.r2` (or other part names) for multi-part types; `.paired` (bool); `.type`; `.attrs` (dict); `.label` (the sample id for collection items, otherwise `<step>.<port>` or the input name; use it to name things in reports, e.g. QUAST `-l`). For `cardinality: many`, a list of value objects (`{{ inputs.contigs \| join(' ') }}` works). |
| `outputs.<port>` | relative output path, or an object with `.r1`/`.r2` (part names) when the output has parts |
| `params.<id>` | parameter value (defaults applied) |
| `dbs.<param id>` | resolved filesystem path of a `database` parameter (registry `path`) |
| `cpu`, `memory_gb` | the step's allocation |

## Pipeline definition: JSON (`schema: modpipe/pipeline/v1`)

```json
{
  "schema": "modpipe/pipeline/v1",
  "name": "...", "description": "...",
  "inputs": {
    "reads": {"type": "reads.short.paired", "collection": true,
              "source": {"paired_end_libs": [{"sample_id": "s1", "read1": "...", "read2": "..."}]},
              "attributes": {"platform": "illumina"}}
  },
  "steps": {
    "trim":     {"module": "fastp",  "in": {"reads": "$inputs.reads"}, "params": {}, "module_version": 1},
    "assemble": {"module": "spades", "in": {"reads": "trim.trimmed_reads"}},
    "qc":       {"module": "quast",  "in": {"contigs": "assemble.contigs"}}
  },
  "outputs": {"contigs": "assemble.contigs", "qc_report": "qc.report"},
  "template": {"label": "Genome assembly with QC", "category": "assembly",
               "expose": ["assemble.params.mode"],
               "links": {"abundance.params.db": "classify.params.db"}}
}
```

- Step ids, input names and output names must match `[A-Za-z][A-Za-z0-9_-]{0,63}`.
- References: `"$inputs.<name>"` or `"<step>.<output port>"`. A `cardinality: many` port may take a list of references.
- **Scatter**: a pipeline input with `"collection": true` (one item per sample) feeding a `cardinality: one`
  port makes that step run once per item. Its outputs are collections, and steps downstream keep
  scattering. A step can scatter over only one collection.
- **Gather**: a collection feeding a `cardinality: many` port is collected into one list, so that step
  runs once.
- `module_version` (optional) pins the descriptor major version. A mismatch blocks validation.
- `template` (curated templates only): `label`/`category` for the picker, and `expose`, the `step.params.<id>`
  entries a template-picker UI shows (every other parameter keeps its value or default). `links` copies one
  parameter's value to another when the template is filled (e.g. Bracken uses the Kraken2 database); a linked
  target may not also be exposed. Fill with `modpipe instantiate`, list with `modpipe list-templates --json`.
