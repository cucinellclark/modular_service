# Plan: graphical pipeline editor (BV-BRC-Web)

> **Status (2026-11-03): milestones M1–M4 are built** (see docs/UI.md "Graph editor"). Differences from this plan:
> - The layout is a small built-in layered layout, not dagre. dagre is only loaded through the site bundle, so using it
>   would mean a dependency on the bundle.
> - Pipeline outputs are marked on their output port ("saved as ..."), not drawn as separate sink nodes, to reduce
>   clutter.
> - Workspace save/open is built (M4). Pipelines are saved by default to `/<user>/home/pipeline` and listed as
>   "[my pipelines]" in the editor's template dropdown.
> - Nodes added by an edit are moved down until they don't overlap other nodes (`PipelineModel.avoidOverlap`).
> - Still open from M5: a minimap and help text in the site's docs.

Goal: an interactive canvas where users string tool modules together. Connections are checked against the type
system as you draw them, so incompatible wiring can't be made. Curated templates load as editable graphs, and the
result runs through the same validate/submit path as the form.

## 1. What the user sees

```
+----------------------------------------------------------------------------------------------+
| [Form] [Graph] [JSON]        Template: [Isolate assembly v]  [Auto-layout] [Fit] [Undo][Redo] |
+--------------+------------------------------------------------------------+------------------+
| Modules      |                                                            | Inspector        |
| [search    ] |   (reads)==>[ fastp ]--trimmed-->[ SPAdes ]--contigs-->(*) | step: assemble   |
| > Read QC    |      x3      report.json \           \--> [ QUAST ]        | module: spades   |
|   fastp      |                           \--> [ MultiQC ]                 | mode: [isolate]  |
|   trim_galore|                                                            | k-mers: [auto ]  |
| > Assembly   |                                                            | ports / types    |
|   spades ... |                                                            |                  |
+--------------+------------------------------------------------------------+------------------+
| Check: 0 errors, 1 note (auto converter reads->fasta inserted)  ~16 CPU / 64 GB / 6 h  [Validate] [Run] |
+----------------------------------------------------------------------------------------------+
```

- **Nodes.** Pipeline *inputs* are source nodes (the reads, genomes or files chosen in the inspector). *Steps* are
  module boxes with input ports on the left and output ports on the right; each port is labelled with its type.
  Pipeline *outputs* are sink nodes, marked as "saved to workspace".
- **Wiring.** Drag from an output port. While dragging, every input port on the canvas is colored:
  - green: compatible;
  - amber: may be compatible, depending on the concrete type at run time;
  - blue: compatible through an automatic converter;
  - grey: not allowed, and the drop is refused with the reason as a tooltip.
  Wiring also refuses cycles. Dropping on a single-valued port that is already connected replaces the old edge.
  List ports accept several edges (fan-in, i.e. gather).
- **"What can come next?"** Right-click an output port to see the modules that can consume it. Choosing one adds
  it already wired. The palette also has a filter: "show only modules compatible with the selected port".
- **Scatter and gather made visible.** Collection inputs draw as stacked edges. Steps that run once per sample show
  a "×N per sample" badge. Fan-in to a list port is drawn as converging edges.
- **Inspector.** Shows the selected step's parameters, using the same typed widgets and pattern checks as the form.
  For an input node it shows the source picker reused from the form (workspace reads, SRA, genome group, ...). For
  an edge it shows the declared and resolved types and any converter.
- **Live validation.** About 0.5 s after each edit, the server validates the whole pipeline. Errors and warnings
  appear as badges on the affected node or port; clicking a badge selects it. Auto-inserted converters appear as
  dashed nodes, and "Make explicit" turns one into a normal step. The status bar shows the resource estimate.
- **Templates.** Loading a template draws it as a graph, laid out automatically the first time. Optional steps have
  an on/off toggle, and a disabled step is greyed out with its bypass edge shown.
- **Save and open.** Save the pipeline JSON to the workspace (positions included), open a saved one, and download
  it. Run uses the existing Output Folder/Name fields, the submit call and the job list.

## 2. Technical approach (website)

**Rendering: a custom HTML/SVG canvas with `dagre` for layout.** I recommend this over Cytoscape. Port-to-port
wiring is the core interaction, and Cytoscape has no ports (it would need child-node tricks and an edge-drawing
plugin the site doesn't ship). With the custom canvas:
- nodes are absolutely positioned HTML boxes, so they can hold Dojo widgets, badges and tooltips;
- edges are SVG Bézier curves;
- pan and zoom are a CSS transform on one container;
- `dagre`, already in `public/js/dagre`, only computes the left-to-right layered positions.

This takes roughly 1–1.5k lines of plain Dojo/ES5-compatible code, with no new dependencies and no build changes.
The fallback, if we want to move faster and accept weaker port UX, is Cytoscape + cytoscape-dagre, which the site
already uses in `InteractionGraphContainer.js`.

**One model, three views.** A single `PipelineModel` holds the `modpipe/pipeline/v1` JSON plus positions. The Form,
Graph and JSON tabs are all views of it, so switching tabs never loses work and the JSON tab doubles as a debug
view. The Form tab keeps working for templates.

New files under `public/js/p3/widget/modpipe/`:

| file | role |
|---|---|
| `Catalog.js` | fetches `/api/catalog` (cached by version hash); type logic: `isA`, `isAbstract`, `convertersBetween`, `compatible(outPort, inPort)` |
| `PipelineModel.js` | graph ↔ pipeline JSON, edit operations (add/remove step, connect, disconnect, rename, set param/source), events, undo/redo (snapshot stack) |
| `GraphCanvas.js` | rendering, pan/zoom, drag-to-wire with compatibility coloring, selection, context menus, issue badges |
| `Palette.js` | module list by category, search, "compatible with selection" filter, drag onto canvas |
| `Inspector.js` | step params, input sources, edge info |
| `SourceEditor.js`, `ParamEditor.js` | moved out of `ModularPipeline.js` so the form and the graph share them |
| `IssuesBar.js` | validation summary, resources, Validate and Run |

`ModularPipeline.js` becomes the page shell: tabs, output folder, submit and jobs.

**Two tiers of checking.**
1. *Instant, in the browser* (while dragging). Declared port types against the type hierarchy, list or single
   ports, cycles, and whether a converter exists. This is a small JS port of `TypeSystem.is_a` and
   `converters_between`, using the data from `/api/catalog`.
2. *Authoritative, on the server* (debounced `/api/validate`). Types resolved through `type_from`, required
   attributes, scatter/gather, constraints, parameter values and the resource estimate. The server is always the
   final word, and Run is disabled while there are errors.

A **parity test** keeps the two tiers consistent. Python generates the expected compatibility answer for every
(output port, input port) pair in the catalog, and a Jest test (the site already has Jest) checks the JS logic
against it.

## 3. Backend changes (ModularService API)

- `GET /api/catalog`, one payload:
  - types (parents, abstract flag, kind, attributes) and converters;
  - modules (ports with type, list/optional/`type_from`; params; category; label; resources);
  - a `version` hash for caching.
- **Structured issues.** `Issues` already records a location, today as a `"where: msg"` string. Add
  `{msg, step, port, input, severity}` objects alongside the existing strings, so badges attach to the right node.
- **Resolved types and scatter per step** in the `/api/validate` response (the plan already computes them), used for
  edge labels and the "×N" badges.
- **`ui` key allowed in pipeline JSON** (`{"ui": {"positions": {...}}}`). The validator and runner ignore it, and
  saved pipelines keep their layout.
- *(Later)* workspace save/open runs from the browser through the site's existing Workspace client, so no backend
  is needed for it.

## 4. Milestones

| # | deliverable | done when |
|---|---|---|
| M1 | `/api/catalog`, `Catalog.js`, `PipelineModel.js`, read-only graph: load any template, auto-layout, pan/zoom, select → inspector (read-only) | all 17 templates render, and graph → JSON round-trips byte-identical |
| M2 | editing: palette drag-in, drag-to-wire with instant checks, delete, rename, params in the inspector, undo/redo, JSON tab synced | a user can rebuild `isolate_assembly` from scratch; the parity test passes |
| M3 | live server validation: structured issues → badges, auto-converter nodes, resolved types on edges, resource bar; Run from the graph | invalid wiring is impossible or flagged; a graph-built pipeline runs end to end on dev-5 |
| M4 | input-source nodes with the reused source editor, scatter/gather visuals, optional-step toggles, save/open in the workspace | a saved custom pipeline reopens with its layout and reruns |
| M5 | polish: right-click "what can come next", keyboard shortcuts (delete, undo), minimap if needed, help text | user-testing feedback addressed |

M1–M3 are the core, and each milestone can be tested on dev-5.

## 5. Decisions (recommendations in bold)

1. Renderer: **custom HTML/SVG canvas + dagre** vs Cytoscape.
2. Placement: **Graph tab on the existing `/app/ModularPipeline` page** vs a separate `/app/ModularPipelineBuilder`.
3. Users can build pipelines from scratch, not just edit templates: **yes**. The type checks keep this safe.
4. Custom pipelines saved as JSON files in the workspace (type `json`), with no new workspace type for now: **yes**.
