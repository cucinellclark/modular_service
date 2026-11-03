"""Pipeline loading, validation (types, attributes, scatter/gather, params, dbs) and resource planning."""
import json
import re

from .registry import check_param_value
from .template import ENV, _fake_value, check_step_render, resolve_output_type
from .util import Issues, fmt_runtime, parse_memory_gb, read_json

PIPELINE_SCHEMA = "modpipe/pipeline/v1"
TOP_KEYS = {"schema", "name", "description", "inputs", "outputs", "steps", "template", "ui"}
UI_KEYS = {"positions", "disabled", "optional", "links", "viewport", "notes"}
STEP_KEYS = {"module", "in", "params", "module_version", "description", "auto"}
INPUT_KEYS = {"type", "source", "collection", "attributes", "description", "label"}
SOURCE_KEYS = {"paired_end_libs", "single_end_libs", "srr_ids", "srr_libs", "wsid", "wsids", "files",
               "genome_ids", "genome_group", "feature_group", "feature_ids", "fasta_data", "fixture", "database_file"}

# Names that become directory names, Snakefile rule names and workspace paths.
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
GENOME_ID_RE = re.compile(r"^\d+\.\d+$")
SAMPLE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

# Pipeline job limits (decided 2026-11-03: "cap like the big services").
CAPS = {"cpu": 32, "memory_gb": 256, "runtime_s": 48 * 3600}


class Binding:
    """What flows along an edge: a type, known attributes, and whether it is a per-sample collection."""

    def __init__(self, type_id, attrs, collection, origin, conditional=False):
        self.type, self.attrs, self.collection, self.origin, self.conditional = type_id, attrs, collection, origin, conditional

    def __repr__(self):
        c = f" x{self.collection}" if self.collection else ""
        return f"{self.type}{c}"


def _collection_size(src):
    if not isinstance(src, dict):
        return None
    n = 0
    for k in ("paired_end_libs", "single_end_libs", "srr_libs", "files", "wsids", "genome_ids"):
        if isinstance(src.get(k), list):
            n += len(src[k])
    if isinstance(src.get("srr_ids"), list):
        n += len(src["srr_ids"])
    return n or None


def _empty_source_value(v):
    """Why a source value is unusable (empty string, empty list, list with blanks, read pair without a file), or None."""
    if v is None or (isinstance(v, str) and not v.strip()):
        return "empty"
    if isinstance(v, (list, dict)) and not v:
        return "nothing selected"
    if isinstance(v, list):
        for i, x in enumerate(v):
            if x is None or (isinstance(x, str) and not x.strip()):
                return f"item {i + 1} is empty"
            if isinstance(x, dict):
                for key in ("read1", "read2", "read", "srr_accession"):
                    if key in x and not str(x[key] or "").strip():
                        return f"item {i + 1}: {key} is empty"
    return None


def load_pipeline(path):
    return read_json(path)


class Validator:
    def __init__(self, ts, modules, dbs):
        self.ts, self.mods, self.dbs = ts, modules, dbs

    def validate(self, p, where="pipeline"):
        iss = Issues()
        plan = {"steps": {}, "outputs": {}, "order": []}
        ts = self.ts
        if not isinstance(p, dict):
            iss.error(where, "pipeline must be a JSON object")
            return iss, plan
        if p.get("schema") != PIPELINE_SCHEMA:
            iss.error(where, f"schema must be {PIPELINE_SCHEMA!r}")
        for k in p:
            if k not in TOP_KEYS:
                iss.error(where, f"unknown top-level key {k!r}")
        ui = p.get("ui")
        if ui is not None:
            if not isinstance(ui, dict):
                iss.error("ui", "must be an object")
            else:
                for k in ui:
                    if k not in UI_KEYS:
                        iss.error("ui", f"unknown key {k!r} (known: {sorted(UI_KEYS)})")
        steps = p.get("steps") or {}
        if not steps:
            iss.error(where, "no steps")

        # ---------------------------------------------------------------- pipeline inputs
        bindings = {}
        sizes = {}
        for name, d in (p.get("inputs") or {}).items():
            w = f"inputs.{name}"
            if not NAME_RE.match(str(name)):
                iss.error(w, "input names must match [A-Za-z][A-Za-z0-9_-]* (max 64)")
                continue
            if not isinstance(d, dict) or "type" not in d:
                iss.error(w, "needs a type")
                continue
            for k in d:
                if k not in INPUT_KEYS:
                    iss.error(w, f"unknown key {k!r}")
            t = d["type"]
            if t not in ts:
                iss.error(w, f"unknown type {t}")
                continue
            if ts.is_abstract(t):
                iss.error(w, f"input type {t} is abstract; give a concrete type")
            if ts.is_registry_only(t):
                iss.error(w, f"{t} is registry-only (use a database parameter)")
            src = d.get("source")
            if not isinstance(src, dict) or not src:
                iss.error(w, "needs a source object")
            else:
                unknown = set(src) - SOURCE_KEYS
                if unknown:
                    iss.error(w, f"unknown source keys {sorted(unknown)} (known: {sorted(SOURCE_KEYS)})")
                for k, v in src.items():
                    if k == "fixture" or k in unknown:
                        continue
                    empty = _empty_source_value(v)
                    if empty:
                        iss.error(w, f"no data chosen ({k}: {empty})")
                if ts.is_a(t, "reads.short.paired") and not {"paired_end_libs", "srr_ids", "srr_libs", "fixture"} & set(src):
                    iss.error(w, "paired reads need paired_end_libs, srr_ids/srr_libs (or fixture)")
                if ts.is_a(t, "reads.short.single") and "paired_end_libs" in src:
                    iss.error(w, "single-end type but paired_end_libs given")
                if "database_file" in src:
                    dbid, _, key = str(src["database_file"]).partition(":")
                    e = self.dbs.get(dbid)
                    if not e:
                        iss.error(w, f"database_file: unknown database {dbid!r}")
                    elif key not in (e.get("files") or {}):
                        iss.error(w, f"database_file: {dbid} has no file {key!r} (files: {sorted(e.get('files') or {})})")
                for fid in src.get("feature_ids") or []:
                    if not re.match(r"^fig\|\d+\.\d+\.[a-z_]+\.\d+$", str(fid)):
                        iss.error(w, f"bad feature id {fid!r} (expected a BV-BRC patric_id like fig|1206109.14.peg.1)")
                for gid in src.get("genome_ids") or []:
                    if not GENOME_ID_RE.match(str(gid)):
                        iss.error(w, f"bad genome id {gid!r} (expected e.g. 1206109.14)")
                for lib in (src.get("paired_end_libs") or []) + (src.get("single_end_libs") or []) + (src.get("srr_libs") or []):
                    sid = lib.get("sample_id") if isinstance(lib, dict) else None
                    if sid is not None and not SAMPLE_ID_RE.match(str(sid)):
                        iss.error(w, f"bad sample_id {sid!r} (letters, digits, . _ - ; max 128)")
                for acc in (src.get("srr_ids") or []) + [l.get("srr_accession") for l in (src.get("srr_libs") or []) if isinstance(l, dict)]:
                    if acc is not None and not re.match(r"^[SED]RR\d+$", str(acc)):
                        iss.error(w, f"bad SRA run accession {acc!r} (expected SRR/ERR/DRR + digits)")
            attrs = dict(ts.fixed_attributes(t))
            for a, v in (d.get("attributes") or {}).items():
                allowed = ts.allowed_attribute_values(t, a)
                if a not in ts.attributes:
                    iss.error(w, f"unknown attribute {a}")
                elif allowed and v not in allowed:
                    iss.error(w, f"attribute {a}={v!r} not allowed for {t} ({allowed})")
                attrs[a] = v
            coll = name if d.get("collection") else None
            if coll:
                sizes[coll] = _collection_size(src)
            bindings[f"$inputs.{name}"] = Binding(t, attrs, coll, f"$inputs.{name}")

        # ---------------------------------------------------------------- step order (dependencies via refs)
        deps = {}
        for sid, s in steps.items():
            w = f"steps.{sid}"
            if not NAME_RE.match(str(sid)):
                iss.error(w, "step ids must match [A-Za-z][A-Za-z0-9_-]* (max 64)")
            if not isinstance(s, dict):
                iss.error(w, "step must be an object")
                continue
            for k in s:
                if k not in STEP_KEYS:
                    iss.error(w, f"unknown key {k!r}")
            refs = []
            for port, r in (s.get("in") or {}).items():
                refs += r if isinstance(r, list) else [r]
            deps[sid] = set()
            for r in refs:
                if not isinstance(r, str):
                    iss.error(w, f"bad reference {r!r}")
                elif r.startswith("$inputs."):
                    if r not in bindings and r[len("$inputs."):] not in (p.get("inputs") or {}):
                        iss.error(w, f"unknown pipeline input {r}")
                elif "." in r:
                    up = r.split(".", 1)[0]
                    if up not in steps:
                        iss.error(w, f"reference {r}: unknown step {up!r}")
                    elif up == sid:
                        iss.error(w, f"reference {r}: a step cannot consume its own output")
                    else:
                        deps[sid].add(up)
                else:
                    iss.error(w, f"bad reference {r!r} (use $inputs.<name> or <step>.<output>)")
        order, pending = [], {k: set(v) for k, v in deps.items()}
        while pending:
            ready = sorted(k for k, v in pending.items() if not v)
            if not ready:
                iss.error(where, f"cycle between steps {sorted(pending)}")
                break
            for k in ready:
                order.append(k)
                del pending[k]
            for v in pending.values():
                v.difference_update(ready)
        plan["order"] = order

        # ---------------------------------------------------------------- per-step checks
        for sid in order:
            s = steps[sid]
            w = f"steps.{sid}"
            m = self.mods.get(s.get("module"))
            if m is None:
                iss.error(w, f"unknown module {s.get('module')!r}")
                continue
            if "module_version" in s and s["module_version"] != m.version:
                iss.error(w, f"pinned module_version {s['module_version']} but {m.id} is version {m.version} "
                             f"(incompatible descriptor change: update the pipeline)")
            step_in = s.get("in") or {}
            errors_before = len(iss.errors)
            scatter = None
            input_types = {}
            in_attrs = {}
            for port in step_in:
                if port not in m.inputs:
                    iss.error(w, f"module {m.id} has no input {port!r} (inputs: {sorted(m.inputs)})")
            for pid, port in m.inputs.items():
                pw = f"{w}.in.{pid}"
                if pid not in step_in:
                    if port.get("required", True):
                        iss.error(pw, f"required input of {m.id} is not connected")
                    continue
                raw = step_in[pid]
                many = port.get("cardinality", "one") == "many"
                if isinstance(raw, list) and not many:
                    iss.error(pw, "a list of references needs a cardinality: many port")
                    continue
                for r in (raw if isinstance(raw, list) else [raw]):
                    b = self._resolve(r, bindings, steps, iss, pw)
                    if b is None:
                        continue
                    if not ts.is_a(b.type, port["type"]):
                        conv = ts.converters_between(b.type, port["type"])
                        fix = self._fixer(b, port)
                        if fix:
                            plan.setdefault("fixable", []).append({"step": sid, "port": pid, "ref": r, **fix})
                        hint = f"; converter available: {', '.join(c['module'] for c in conv)}" if conv else ""
                        iss.error(pw, f"type mismatch: {r} is {b.type}, {m.id}.{pid} needs {port['type']}{hint}")
                        continue
                    attr_problem = False
                    for a, v in (port.get("requires") or {}).items():
                        have = b.attrs.get(a)
                        if a == "compression" and v == "none":
                            continue  # the engine decompresses automatically (materialize._decompress_if_needed)
                        if have is None:
                            iss.warn(pw, f"{m.id}.{pid} requires {a}={v}; {r} does not declare {a}")
                        elif have != v:
                            attr_problem = True
                            iss.error(pw, f"{m.id}.{pid} requires {a}={v}, but {r} has {a}={have}")
                    if attr_problem:
                        fix = self._fixer(b, port)
                        if fix:
                            plan.setdefault("fixable", []).append({"step": sid, "port": pid, "ref": r, **fix})
                    if b.conditional:
                        iss.warn(pw, f"{r} is a conditional output (has `when:`); it may not exist")
                    input_types.setdefault(pid, b.type)
                    in_attrs.setdefault(pid, b.attrs)
                    if b.collection and not many:
                        if scatter and scatter != b.collection:
                            iss.error(pw, f"step scatters over two collections ({scatter}, {b.collection}); "
                                          f"v1 supports one per step")
                        scatter = scatter or b.collection
            # params
            params = {}
            for k, v in (s.get("params") or {}).items():
                if k not in m.params:
                    iss.error(f"{w}.params.{k}", f"module {m.id} has no parameter {k!r} (has: {sorted(m.params)})")
                    continue
                e = check_param_value(m.params[k], v, ts, self.dbs)
                if e:
                    iss.error(f"{w}.params.{k}", e)
                params[k] = v
            for k, spec in m.params.items():
                if k not in params:
                    if "default" in spec and spec["default"] is not None:
                        params[k] = spec["default"]
                    elif spec.get("required", True):
                        iss.error(f"{w}.params.{k}", f"required parameter of {m.id} has no value and no default")
            db_reqs = []
            for k, spec in m.params.items():
                if spec["type"] == "database" and params.get(k):
                    e = self.dbs.get(params[k])
                    if e:
                        db_reqs.append({"param": k, "db": e["id"], "status": e.get("status"),
                                        "requirements": e.get("requirements") or {}})
                        if e.get("status") == "unverified":
                            iss.warn(f"{w}.params.{k}", f"database {e['id']} is unverified (not yet exercised by a test run)")
            # outputs
            outs = {}
            for oid, op in m.outputs.items():
                rt = resolve_output_type(m, op, input_types, ts)
                if rt is None:
                    if op.get("type_from") is not None and any(input_types.values()):
                        iss.error(f"{w}.out.{oid}", f"cannot derive output type from inputs {input_types} (type_from)")
                    rt = op["type"]
                attrs = dict(ts.fixed_attributes(rt))
                tf = op.get("type_from")
                if isinstance(tf, str) and tf in in_attrs:
                    attrs = {**in_attrs[tf], **attrs}
                attrs.update(op.get("attributes") or {})
                conditional, never = False, False
                if op.get("when"):
                    v = _eval_when(op["when"], params, input_types, ts)
                    if v is None:
                        conditional = True          # depends on something unknown at validation time
                    elif v is False:
                        never = True
                outs[oid] = Binding(rt, attrs, scatter, f"{sid}.{oid}", conditional=conditional)
                outs[oid].never = never
            if (m.d.get("command") and len(iss.errors) == errors_before
                    and all(pid in input_types or not p.get("required", True) for pid, p in m.inputs.items())):
                e = check_step_render(m, input_types, params, ts, self.dbs)
                if e:
                    iss.error(w, e)
            for oid, b in outs.items():
                bindings[f"{sid}.{oid}"] = b
            plan["steps"][sid] = {"module": m.id, "module_version": m.version, "scatter": scatter,
                                  "scatter_size": sizes.get(scatter) if scatter else None,
                                  "inputs": {k: repr(bindings_for(step_in.get(k), bindings)) for k in m.inputs if k in step_in},
                                  "outputs": {k: repr(v) for k, v in outs.items()},
                                  "output_types": {k: {"type": v.type, "collection": v.collection, "attributes": v.attrs,
                                                       "conditional": v.conditional, "never": getattr(v, "never", False)}
                                                   for k, v in outs.items()},
                                  "params": params, "databases": db_reqs, "resources": m.resources}

        # references to never-produced outputs
        for sid in order:
            for port, r in ((steps[sid].get("in") or {}).items()):
                for x in (r if isinstance(r, list) else [r]):
                    b = bindings.get(x)
                    if b is not None and getattr(b, "never", False):
                        iss.error(f"steps.{sid}.in.{port}", f"{x} is never produced with these parameters (`when:` is false)")

        # ---------------------------------------------------------------- pipeline outputs & template
        if not p.get("outputs"):
            iss.warn(where, "no pipeline outputs declared (nothing would be saved)")
        for name, r in (p.get("outputs") or {}).items():
            if not NAME_RE.match(str(name)):
                iss.error(f"outputs.{name}", "output names must match [A-Za-z][A-Za-z0-9_-]* (max 64)")
                continue
            b = self._resolve(r, bindings, steps, iss, f"outputs.{name}")
            if b is not None:
                plan["outputs"][name] = repr(b)
                if getattr(b, "never", False):
                    iss.error(f"outputs.{name}", f"{r} is never produced with these parameters")
        tmpl = p.get("template") or {}
        for k in tmpl:
            if k not in ("expose", "links", "label", "category", "description", "optional"):
                iss.error("template", f"unknown key {k!r}")
        for step, o in (tmpl.get("optional") or {}).items():
            if step not in steps:
                iss.error("template.optional", f"{step!r} is not a step")
            elif not isinstance(o, dict) or not isinstance(o.get("default", True), bool):
                iss.error("template.optional", f"{step!r}: expected {{label, default: true|false, bypass: {{...}}}}")
            else:
                m = self.mods.get(steps[step].get("module"))
                for port, ref in (o.get("bypass") or {}).items():
                    if m and port not in m.outputs:
                        iss.error("template.optional", f"{step}.bypass: module {m.id} has no output {port!r}")
                    if not isinstance(ref, str) or ref.split(".", 1)[0] == step:
                        iss.error("template.optional", f"{step}.bypass.{port}: must reference another step or input")
        for target, source in (tmpl.get("links") or {}).items():
            for e in (target, source):
                parts = str(e).split(".")
                if len(parts) != 3 or parts[1] != "params" or parts[0] not in steps:
                    iss.error("template.links", f"{e!r}: expected <step>.params.<id> of an existing step")
                else:
                    m = self.mods.get(steps[parts[0]].get("module"))
                    if m and parts[2] not in m.params:
                        iss.error("template.links", f"{e!r}: module {m.id} has no parameter {parts[2]}")
            if target in (tmpl.get("expose") or []):
                iss.error("template.links", f"{target!r} is linked; it must not also be exposed")
        for e in (tmpl.get("expose") or []):
            parts = str(e).split(".")
            if len(parts) != 3 or parts[1] != "params":
                iss.error("template.expose", f"{e!r}: expected <step>.params.<id>")
            elif parts[0] not in steps:
                iss.error("template.expose", f"{e!r}: unknown step")
            else:
                m = self.mods.get(steps[parts[0]].get("module"))
                if m and parts[2] not in m.params:
                    iss.error("template.expose", f"{e!r}: module {m.id} has no parameter {parts[2]}")

        plan["resources"] = self._resources(plan, deps, iss)
        return iss, plan

    def _fixer(self, b, port):
        """A single available converter module that turns binding `b` into something `port` accepts."""
        ts = self.ts
        for c in ts.converters:
            if c.get("status") != "available" or not ts.is_a(b.type, c["from"]):
                continue
            m = self.mods.get(c["module"])
            if m is None:
                continue
            ins = [pid for pid, p in m.inputs.items() if p.get("required", True)]
            if len(ins) != 1 or not ts.is_a(b.type, m.inputs[ins[0]]["type"]):
                continue
            for oid, op in m.outputs.items():
                ot = op["type"] if op.get("type_from") is None else c["to"]
                if not ts.is_a(ot, port["type"]):
                    continue
                attrs = {**ts.fixed_attributes(ot), **(op.get("attributes") or {})}
                if all(attrs.get(a) == v for a, v in (port.get("requires") or {}).items()
                       if not (a == "compression" and v == "none")):
                    return {"module": m.id, "in_port": ins[0], "out_port": oid}
        return None

    def _resolve(self, r, bindings, steps, iss, w):
        if not isinstance(r, str):
            iss.error(w, f"bad reference {r!r}")
            return None
        b = bindings.get(r)
        if b is not None:
            return b
        if r.startswith("$inputs."):
            return None  # already reported (unknown or invalid input)
        sid, _, port = r.partition(".")
        if sid in steps:
            m = self.mods.get(steps[sid].get("module"))
            if m is not None and port not in m.outputs:
                iss.error(w, f"{r}: module {m.id} has no output {port!r} (outputs: {sorted(m.outputs)})")
        return None

    def _resources(self, plan, deps, iss):
        """Preflight aggregation: max cpu/mem over steps, runtime = critical path (scattered steps x n)."""
        cpu = mem = 0.0
        partition, constraint = None, None
        finish = {}
        for sid in plan["order"]:
            st = plan["steps"].get(sid)
            if not st:
                continue
            r = st["resources"]
            n = st["scatter_size"] or 1
            m = r["memory_gb"]
            for d in st["databases"]:
                req = d["requirements"]
                if req.get("mem"):
                    m = max(m, parse_memory_gb(req["mem"]))
                partition = req.get("partition") or partition
                constraint = req.get("constraint") or constraint
            # Scattered items run side by side (Snakemake) as far as the CPU and memory caps allow.
            step_cpu = min(r["cpu"], CAPS["cpu"])
            slots = max(1, min(CAPS["cpu"] // max(step_cpu, 1), int(CAPS["memory_gb"] // max(m, 1e-9))))
            parallel = min(n, slots)
            waves = -(-n // parallel)
            cpu = max(cpu, min(CAPS["cpu"], step_cpu * parallel))
            mem = max(mem, m * parallel)
            st["estimate"] = {"parallel": parallel, "waves": waves, "runtime_s": r["runtime_s"] * waves,
                              "memory_gb": m * parallel}
            start = max([finish.get(u, 0) for u in deps.get(sid, ())] or [0])
            finish[sid] = start + r["runtime_s"] * waves
        runtime = max(finish.values() or [0])
        out = {"cpu": int(cpu), "memory_gb": mem, "runtime_s": runtime, "runtime": fmt_runtime(runtime),
               "partition": partition, "constraint": constraint, "caps": CAPS}
        big = [sid for sid, st in plan["steps"].items() if st["resources"]["cpu"] > CAPS["cpu"]]
        if big:
            iss.warn("resources", f"steps {big} ask for more than {CAPS['cpu']} CPUs; they will get {CAPS['cpu']}")
        if mem > CAPS["memory_gb"]:
            iss.error("resources", f"needs {mem:.0f} GB memory; cap is {CAPS['memory_gb']} GB")
        if runtime > CAPS["runtime_s"]:
            iss.error("resources", f"estimated runtime {fmt_runtime(runtime)} exceeds the {CAPS['runtime_s'] // 3600}h cap")
        if any(st.get("scatter") and not st.get("scatter_size") for st in plan["steps"].values()):
            iss.warn("resources", "collection size unknown at validation time; runtime assumes 1 item per collection")
        return out


def auto_convert(validator, p, where="pipeline", max_rounds=4):
    """Validate; where an edge can be fixed by one available converter module, insert that step and re-validate.
    Returns (pipeline, issues, plan); inserted steps are reported as warnings and marked "auto": true."""
    import copy
    p = copy.deepcopy(p)
    notes = []
    ui_issue = None
    try:
        p = apply_ui(p)
    except ValueError as e:
        ui_issue = str(e)
    for _ in range(max_rounds):
        iss, plan = validator.validate(p, where=where)
        fixes = plan.get("fixable") or []
        if not fixes:
            break
        made = {}
        for f in fixes:
            key = (f["ref"], f["module"])
            if key not in made:
                base = f"{f['module']}_{f['ref'].replace('$inputs.', 'in_').replace('.', '_')}"[:60]
                sid, n = base, 2
                while sid in p["steps"]:
                    sid, n = f"{base}_{n}", n + 1
                p["steps"][sid] = {"module": f["module"], "in": {f["in_port"]: f["ref"]}, "auto": True}
                made[key] = f"{sid}.{f['out_port']}"
                notes.append(f"inserted converter step {sid!r} ({f['module']}) for {f['ref']} -> {f['step']}.{f['port']}")
            step_in = p["steps"][f["step"]]["in"]
            v = step_in[f["port"]]
            step_in[f["port"]] = [made[key] if x == f["ref"] else x for x in v] if isinstance(v, list) else made[key]
    for n in notes:
        iss.warn("auto-converter", n)
    if ui_issue:
        iss.error("ui.disabled", ui_issue)
    plan["auto_converters"] = notes
    return p, iss, plan


def apply_ui(p):
    """Editor state in a pipeline's `ui` key that changes what runs: `ui.disabled` lists optional steps switched off;
    they are removed with `ui.optional.<step>.bypass` rewiring (same rules as template optional steps).
    Returns a new pipeline (input unchanged); raises ValueError if a remaining step needs a disabled one."""
    import copy
    ui = p.get("ui") if isinstance(p, dict) else None
    disabled = set((ui or {}).get("disabled") or []) if isinstance(ui, dict) else set()
    if not disabled:
        return p
    from .templates import TemplateError, _remove_steps
    p = copy.deepcopy(p)
    opt = p["ui"].get("optional") or {}
    bypass = {}
    for st in disabled:
        for port, ref in ((opt.get(st) or {}).get("bypass") or {}).items():
            bypass[f"{st}.{port}"] = ref
    try:
        _remove_steps(p, disabled & set(p.get("steps") or {}), bypass)
    except TemplateError as e:
        raise ValueError(str(e))
    p["ui"] = {k: v for k, v in p["ui"].items() if k != "disabled"}
    return p


def bindings_for(r, bindings):
    if r is None:
        return None
    if isinstance(r, list):
        return [bindings.get(x) for x in r]
    return bindings.get(r)


def _eval_when(expr, params, input_types, ts):
    """True/False if decidable from params and resolved input types, else None."""
    inputs = {k: _fake_value(ts, t, k) for k, t in input_types.items()}
    try:
        return bool(ENV.compile_expression(expr)(params=params, inputs=inputs))
    except Exception:
        return None
