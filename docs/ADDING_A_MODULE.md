# Adding a Tool Module (draft workflow)

1. **Confirm the tool is in the container**
   ```bash
   S=/vol/patric3/production/containers/ubuntu-176-build12-2.sif
   singularity exec $S bash -c 'command -v <tool> && <tool> --version'
   ```
   If it's missing, set `environment: <name>` in the descriptor to use a
   separately sourced environment for now (ARCHITECTURE §4, "Tool
   environments"), and request that the tool be added to the container.

2. **Add it to `tools/tool_list.json` and re-run the harvest** (see
   PREPROCESSING.md). Then read `reference/tools/<id>/` (help.txt,
   bvbrc_invocations.md, nfcore/*/meta.yml).

   **Find an existing invocation.** Check the "Used by" column in
   [TOOL_INVENTORY.md](TOOL_INVENTORY.md) and copy flags and defaults from
   working BV-BRC code:
   ```bash
   singularity exec $S grep -rn -w '<tool>' /opt/p3/deployment/plbin /opt/p3/deployment/pybin /opt/p3/deployment/lib /opt/p3/deployment/workflows
   ```

3. **Pick port types** from [`types/types.yaml`](../types/types.yaml); the rules are in
   [ARCHITECTURE.md §2](ARCHITECTURE.md#2-data-type-system). Installed databases are parameters that
   take a registry id from [`resources/databases.yaml`](../resources/databases.yaml). Use the most
   general input type the tool really accepts and the most specific output
   type it guarantees. If a new type is needed, add it to `types/types.yaml`
   **and** give it a workspace-type mapping in `types/wstypes.yaml`, then run
   `python3 tools/check_types.py`.

4. **Write `modules/<id>.yaml`** following [MODULE_SCHEMA.md](MODULE_SCHEMA.md). Copy
   [`modules/fastp.yaml`](../modules/fastp.yaml) (simple) or [`modules/spades.yaml`](../modules/spades.yaml)
   (modes, optional input, `fail()` constraints). Name outputs as the discovery run did and list the runs under
   `tests.discovery_runs`; lint then checks the declared outputs really exist.
   Use `command:` when one templated command line is enough. Otherwise use
   `adapter: <id>.py` (Python class with `build_commands()` /
   `collect_outputs()`).

4b. **Quote untrusted values**: `| q` on every input path, label and string param; give string params a
   `pattern`. `bin/modpipe lint` fails otherwise (see [SECURITY.md](SECURITY.md)).

5. **Set resources** (cpu/memory/runtime) conservatively. These feed preflight.

5b. **Discovery run matching the module**: add a spec to `tools/module_discovery_specs.yaml`, then
   `python3 tools/module_discovery.py tools/module_discovery_specs.yaml tests/discovery/sets/NN_name.yaml` and
   `tests/discovery/submit.sh NN_name`. This renders the real template with fixtures, so lint can check the declared outputs.

6. **Validate and test**
   ```bash
   bin/modpipe lint <id>                       # schema, types, params, template renders for every variant, discovery outputs
   bin/modpipe compatible --from <id>.<output> # sanity: what can follow it?
   bin/modpipe validate pipelines/<some pipeline using it>.json
   python3 -m unittest discover -s tests/unit
   ```

7. Add the module to a curated pipeline template if it belongs in one.

7. **Run it for real**: add or extend a pipeline in `tests/pipelines/` using fixtures, then
   `sbatch tests/e2e/run_pipeline.sbatch tests/pipelines/<pipeline>.json` and inspect
   `tests/e2e/results/<pipeline>/`.
