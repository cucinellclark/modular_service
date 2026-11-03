"""Jinja2 command templating: context objects, rendering, `when:` evaluation, and lint rendering."""
import itertools
import shlex

import jinja2

ENV = jinja2.Environment(undefined=jinja2.StrictUndefined, trim_blocks=False, lstrip_blocks=True, autoescape=False)
ENV.filters["q"] = lambda v: shlex.quote(str(v))

# Hostile stand-in for any untrusted text (free-text params, input paths, labels) used by lint_shell_safety.
# Rendered unquoted, inside double quotes, or with broken quoting, it no longer survives shell parsing intact.
HOSTILE = "h0 st;i$(le)`x`'y\"z|&>*?"


class TemplateMisuse(Exception):
    pass


class ConstraintViolation(Exception):
    """Raised by {{ fail('...') }} in a template: an invalid input/parameter combination."""


def _fail(msg):
    raise ConstraintViolation(msg)


ENV.globals["fail"] = _fail


class Value:
    """A staged data value as seen by templates."""

    def __init__(self, type_id, path=None, parts=None, attrs=None, ts=None, label=None):
        self.type, self._path, self._parts, self.attrs = type_id, path, dict(parts or {}), dict(attrs or {})
        # human-readable name: the sample id for collection items, else "<step>.<port>" / the input name
        self.label = label
        self._kind = ts.kind(type_id) if ts else None

    def __str__(self):
        if self._path is None:
            raise TemplateMisuse(f"{self.type} has parts {sorted(self._parts)}; use .{next(iter(self._parts), 'r1')} "
                                 f"instead of the value itself")
        return str(self._path)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._parts:
            return self._parts[name]
        raise AttributeError(f"{self.type} has no part {name!r} (parts: {sorted(self._parts)})")

    @property
    def paired(self):
        return "r1" in self._parts and "r2" in self._parts

    @property
    def parts(self):
        return dict(self._parts)


def output_value(port, resolved_type, ts):
    """Context object for an output port, given the type it resolved to."""
    parts = port.get("parts")
    if parts and ts.kind(resolved_type) == "files" and set(ts.required_parts(resolved_type)) <= set(parts):
        return Value(resolved_type, path=port.get("path"), parts=parts, ts=ts)
    if port.get("path"):
        return Value(resolved_type, path=port["path"], ts=ts)
    return Value(resolved_type, parts=parts, ts=ts)


def build_context(module, inputs, outputs, params, cpu, memory_gb, dbs):
    return {"inputs": inputs, "outputs": outputs, "params": params, "dbs": dbs, "cpu": cpu, "memory_gb": memory_gb}


def render_command(module, ctx):
    tmpl = ENV.from_string(module.d["command"])
    txt = tmpl.render(**ctx)
    # A template renders ONE shell command; its lines are argument continuations, joined with spaces.
    # Use explicit `&&` / `;` inside the template for multi-command steps.
    return " ".join(l.strip() for l in txt.splitlines() if l.strip())


def eval_when(expr, ctx):
    return bool(ENV.compile_expression(expr, undefined_to_none=False)(**ctx))


def resolve_output_type(module, port, input_types, ts):
    """Concrete type of an output port given the actual types bound to the module's inputs."""
    tf = port.get("type_from")
    if tf is None:
        return port["type"]
    src_port = tf if isinstance(tf, str) else tf["port"]
    src = input_types.get(src_port)
    if src is None:
        return port["type"]
    if isinstance(tf, dict) and tf.get("map"):
        for anc in ts.ancestors(src):  # longest-prefix match
            if anc in tf["map"]:
                return tf["map"][anc]
        return None
    return src if ts.is_a(src, port["type"]) else None


# ------------------------------------------------------------------ lint

def _concrete_variants(ts, tid):
    if not ts.is_abstract(tid):
        yield tid
    for t, d in ts.types.items():
        if t != tid and ts.is_a(t, tid) and not d.get("abstract") and not d.get("registry_only"):
            yield t


def _fake_value(ts, tid, port_id):
    parts = ts.parts(tid)
    attrs = ts.fixed_attributes(tid)
    if ts.kind(tid) == "files" and parts:
        req = ts.required_parts(tid)
        return Value(tid, parts={p: f"inputs/{port_id}.{p}" for p in parts if p in req}, attrs=attrs, ts=ts, label=port_id)
    return Value(tid, path=f"inputs/{port_id}", attrs=attrs, ts=ts, label=port_id)


def _param_variants(module, dbreg, ts):
    base = {}
    variants = []
    for pid, p in module.params.items():
        if p["type"] == "database":
            cands = [e["id"] for e in dbreg.of_type(ts, p["db_type"]) if e.get("status") != "missing"]
            base[pid] = p.get("default") or (cands[0] if cands else "missing_db")
            continue
        base[pid] = p.get("default")
        if p["type"] == "enum":
            variants += [(pid, v) for v in p["enum"]]
        elif p["type"] == "bool":
            variants += [(pid, not p.get("default", False))]
    yield dict(base)
    for pid, v in variants:
        d = dict(base)
        d[pid] = v
        yield d


def lint_render(module, ts, dbreg=None, max_renders=400):
    """Render the command for every input-type variant x parameter variant; return error strings."""
    from .registry import DatabaseRegistry
    dbreg = dbreg or DatabaseRegistry()
    errs = []
    in_variants = []
    for pid, p in module.inputs.items():
        if p.get("type") not in ts:
            return errs  # unknown port type: already reported by lint; can't build stand-in values
        opts = list(dict.fromkeys(_concrete_variants(ts, p["type"])))
        many = p.get("cardinality", "one") == "many"
        vals = [[_fake_value(ts, t, f"{pid}{i}") for i in range(2)] if many else _fake_value(ts, t, pid) for t in opts]
        if not p.get("required", True):
            vals.append(None)
        in_variants.append([(pid, v) for v in vals])
    n = 0
    for combo in itertools.product(*in_variants) if in_variants else [()]:
        inputs = dict(combo)
        input_types = {k: (v[0].type if isinstance(v, list) else v.type) for k, v in inputs.items() if v is not None}
        for params in _param_variants(module, dbreg, ts):
            n += 1
            if n > max_renders:
                return errs
            outputs = {}
            for oid, op in module.outputs.items():
                rt = resolve_output_type(module, op, input_types, ts)
                if rt is None:
                    rt = op["type"]
                outputs[oid] = output_value(op, rt, ts)
            dbs = {pid: f"/db/{params[pid]}" for pid, p in module.params.items() if p["type"] == "database"}
            ctx = build_context(module, inputs, outputs, params, 4, 16, dbs)
            label = ", ".join(f"{k}={'absent' if v is None else (v[0].type + '[]' if isinstance(v, list) else v.type)}"
                              for k, v in inputs.items())
            label += "; " + ", ".join(f"{k}={v}" for k, v in params.items() if module.params[k]["type"] in ("enum", "bool"))
            try:
                cmd = render_command(module, ctx)
                if not cmd.strip():
                    errs.append(f"renders empty ({label})")
                for op in module.outputs.values():
                    if op.get("when"):
                        eval_when(op["when"], ctx)
            except ConstraintViolation:
                pass  # declared invalid combination; reported by pipeline validation, not a descriptor bug
            except (jinja2.TemplateError, TemplateMisuse, AttributeError, TypeError) as e:
                msg = f"{type(e).__name__}: {e} ({label})"
                if msg not in errs:
                    errs.append(msg)
    return errs


def check_step_render(module, input_types, params, ts, dbreg):
    """Render a step's command with stand-in paths for its resolved input types. Returns an error string or None."""
    inputs = {}
    for pid, p in module.inputs.items():
        t = input_types.get(pid)
        if t is None:
            inputs[pid] = None
        elif p.get("cardinality", "one") == "many":
            inputs[pid] = [_fake_value(ts, t, f"{pid}0")]
        else:
            inputs[pid] = _fake_value(ts, t, pid)
    outputs = {oid: output_value(op, resolve_output_type(module, op, input_types, ts) or op["type"], ts)
               for oid, op in module.outputs.items()}
    dbs = {pid: (dbreg.get(params.get(pid)) or {}).get("path", "") for pid, p in module.params.items() if p["type"] == "database"}
    try:
        render_command(module, build_context(module, inputs, outputs, params, 4, 16, dbs))
    except ConstraintViolation as e:
        return str(e)
    except (jinja2.TemplateError, TemplateMisuse, AttributeError, TypeError) as e:
        return f"command template failed: {type(e).__name__}: {e}"
    return None


# ------------------------------------------------------------------ shell-safety lint

def _hostile_value(ts, tid, port_id):
    v = _fake_value(ts, tid, port_id)
    if v._path is not None:
        v._path = f"inputs/{HOSTILE}/{port_id}"
    v._parts = {k: f"inputs/{HOSTILE}/{port_id}.{k}" for k in v._parts}
    v.label = f"{HOSTILE}{port_id}"
    return v


def _intact(cmd, needle):
    """True if every occurrence of `needle` in the shell-parsed command lies inside a single argument."""
    try:
        tokens = shlex.split(cmd, posix=True)
    except ValueError as e:
        return False, f"command does not parse as shell words ({e})"
    raw = cmd.count(needle) if needle in cmd else 0
    seen = sum(t.count(needle) for t in tokens)
    if seen == 0 and raw == 0:
        return True, None   # value not used in the command (e.g. only in conditions)
    if seen == 0:
        return False, "untrusted value is split or altered by the shell (unquoted, or inside double quotes)"
    return True, None


def lint_shell_safety(module, ts, dbreg=None, max_renders=200):
    """Render with hostile values for every untrusted string (string params without a `pattern`, input paths,
    labels) and require each to survive shell word-splitting intact. Returns error strings."""
    from .registry import DatabaseRegistry
    dbreg = dbreg or DatabaseRegistry()
    errs = []
    in_variants = []
    for pid, p in module.inputs.items():
        if p.get("type") not in ts:
            return errs
        opts = list(dict.fromkeys(_concrete_variants(ts, p["type"])))
        many = p.get("cardinality", "one") == "many"
        vals = [[_hostile_value(ts, t, f"{pid}{i}") for i in range(2)] if many else _hostile_value(ts, t, pid) for t in opts]
        if not p.get("required", True):
            vals.append(None)
        in_variants.append([(pid, v) for v in vals])
    n = 0
    for combo in itertools.product(*in_variants) if in_variants else [()]:
        inputs = dict(combo)
        input_types = {k: (v[0].type if isinstance(v, list) else v.type) for k, v in inputs.items() if v is not None}
        for params in _param_variants(module, dbreg, ts):
            n += 1
            if n > max_renders:
                return errs
            for pid, spec in module.params.items():      # free text: hostile; pattern-restricted text: keep default
                if spec["type"] == "string" and not spec.get("pattern"):
                    params[pid] = HOSTILE
            outputs = {oid: output_value(op, resolve_output_type(module, op, input_types, ts) or op["type"], ts)
                       for oid, op in module.outputs.items()}
            dbs = {pid: f"/db/{params[pid]}" for pid, p in module.params.items() if p["type"] == "database"}
            ctx = build_context(module, inputs, outputs, params, 4, 16, dbs)
            try:
                cmd = render_command(module, ctx)
            except (ConstraintViolation, jinja2.TemplateError, TemplateMisuse, AttributeError, TypeError):
                continue   # render problems are reported by lint_render
            ok, why = _intact(cmd, HOSTILE)
            if not ok:
                label = ", ".join(f"{k}={'absent' if v is None else (v[0].type + '[]' if isinstance(v, list) else v.type)}"
                                  for k, v in inputs.items())
                msg = f"shell safety: {why}, e.g. with {label}. Pipe untrusted values through `| q`, or give string params a `pattern`."
                if not any(why in e for e in errs):
                    errs.append(msg)
    return errs
