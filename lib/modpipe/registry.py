"""Module and database registries, with descriptor validation (schema modpipe/module/v1)."""
import glob
import json
import os
import re

import yaml

from .util import Issues, parse_memory_gb, parse_runtime_s, read_json, read_yaml, repo_path

MODULE_SCHEMA = "modpipe/module/v1"
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PARAM_TYPES = {"int", "float", "bool", "string", "enum", "database"}
TOP_KEYS = {"schema", "id", "version", "label", "description", "category", "tool", "environment", "inputs",
            "outputs", "parameters", "resources", "command", "adapter", "tests", "provenance", "notes"}
IN_KEYS = {"id", "type", "required", "cardinality", "requires", "description", "label"}
OUT_KEYS = {"id", "type", "type_from", "path", "parts", "required", "when", "attributes", "description", "label"}
PARAM_KEYS = {"id", "type", "default", "min", "max", "enum", "db_type", "label", "description", "required", "advanced",
              "pattern"}
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


class DatabaseRegistry:
    def __init__(self, path=None):
        d = read_yaml(path or repo_path("resources", "databases.yaml"))
        self.binds = d.get("binds", {})
        self.dbs = {e["id"]: e for e in d["databases"]}

    def get(self, dbid):
        return self.dbs.get(dbid)

    def of_type(self, ts, db_type):
        return [e for e in self.dbs.values() if ts.is_a(e["type"], db_type)]


class Module:
    def __init__(self, d, path):
        self.d = d
        self.path = path
        self.id = d.get("id")
        self.version = d.get("version")
        self.inputs = {p["id"]: p for p in d.get("inputs") or [] if isinstance(p, dict) and "id" in p}
        self.outputs = {p["id"]: p for p in d.get("outputs") or [] if isinstance(p, dict) and "id" in p}
        self.params = {p["id"]: p for p in d.get("parameters") or [] if isinstance(p, dict) and "id" in p}

    @property
    def resources(self):
        r = self.d.get("resources") or {}
        return {"cpu": int(r.get("cpu", 1)), "memory_gb": parse_memory_gb(r.get("memory", "2G")),
                "runtime_s": parse_runtime_s(r.get("runtime", "1h"))}

    def summary(self):
        return {"id": self.id, "version": self.version, "label": self.d.get("label"), "category": self.d.get("category"),
                "tool": self.d.get("tool"),
                "inputs": [{k: p.get(k) for k in ("id", "type", "required", "cardinality") if k in p} for p in self.inputs.values()],
                "outputs": [{k: p.get(k) for k in ("id", "type", "type_from", "required") if k in p} for p in self.outputs.values()],
                "parameters": [{k: p.get(k) for k in ("id", "type", "default", "enum", "db_type") if k in p} for p in self.params.values()],
                "resources": self.d.get("resources")}


class ModuleRegistry:
    def __init__(self, ts, dbs, module_dir=None):
        self.ts, self.dbreg = ts, dbs
        self.dir = module_dir or repo_path("modules")
        self.modules, self.load_issues = {}, Issues()
        for f in sorted(glob.glob(os.path.join(self.dir, "*.yaml"))):
            where = os.path.relpath(f, repo_path())
            try:
                d = read_yaml(f)
            except yaml.YAMLError as e:
                self.load_issues.error(where, f"YAML error: {e}")
                continue
            if not isinstance(d, dict) or d.get("schema") != MODULE_SCHEMA:
                self.load_issues.warn(where, f"skipped: not a {MODULE_SCHEMA} descriptor")
                continue
            m = Module(d, f)
            if m.id in self.modules:
                self.load_issues.error(where, f"duplicate module id {m.id}")
            self.modules[m.id] = m
        tl = repo_path("reference", "tools", "index.json")
        self.tool_index = read_json(tl)["tools"] if os.path.exists(tl) else {}

    def get(self, mid):
        return self.modules.get(mid)

    # ------------------------------------------------------------------ descriptor validation
    def lint(self, m):
        iss = Issues()
        w = os.path.relpath(m.path, repo_path())
        d, ts = m.d, self.ts
        for k in d:
            if k not in TOP_KEYS:
                iss.error(w, f"unknown top-level key {k!r}")
        if not m.id or not ID_RE.match(str(m.id)):
            iss.error(w, f"bad id {m.id!r} (want [a-z][a-z0-9_]*)")
        elif os.path.basename(m.path) != f"{m.id}.yaml":
            iss.error(w, f"file name must be {m.id}.yaml")
        if not isinstance(m.version, int) or m.version < 1:
            iss.error(w, "version must be a positive integer (descriptor major version)")
        for k in ("label", "tool", "outputs", "resources"):
            if not d.get(k):
                iss.error(w, f"missing {k}")
        if bool(d.get("command")) == bool(d.get("adapter")):
            iss.error(w, "exactly one of `command` or `adapter` is required")
        tool = d.get("tool") or {}
        if tool.get("id") and self.tool_index:
            ti = self.tool_index.get(tool["id"])
            if not ti:
                iss.warn(w, f"tool.id {tool['id']!r} not in reference/tools/index.json")
            elif tool.get("version") and ti.get("version") and str(ti["version"]) != str(tool["version"]):
                iss.warn(w, f"tool.version {tool['version']} differs from container version {ti['version']}")
        env = d.get("environment", "container")
        if env != "container":
            iss.warn(w, f"uses non-container environment {env!r} (allowed for now; must move into the container)")

        # ports
        seen = set()
        for kind, ports, keys in (("inputs", d.get("inputs") or [], IN_KEYS), ("outputs", d.get("outputs") or [], OUT_KEYS)):
            for p in ports:
                pw = f"{w}: {kind}.{p.get('id', '?')}"
                if not isinstance(p, dict) or "id" not in p or "type" not in p:
                    iss.error(pw, "port needs id and type")
                    continue
                for k in p:
                    if k not in keys:
                        iss.error(pw, f"unknown key {k!r}")
                if not ID_RE.match(p["id"]):
                    iss.error(pw, "bad port id")
                if (kind, p["id"]) in seen:
                    iss.error(pw, "duplicate port id")
                seen.add((kind, p["id"]))
                t = p["type"]
                if t not in ts:
                    iss.error(pw, f"unknown type {t}")
                    continue
                if ts.is_registry_only(t):
                    iss.error(pw, f"{t} is registry-only; use a `database` parameter instead of a port")
                if kind == "inputs":
                    if p.get("cardinality", "one") not in ("one", "many"):
                        iss.error(pw, "cardinality must be one|many")
                    for a, v in (p.get("requires") or {}).items():
                        if a not in ts.attributes:
                            iss.error(pw, f"requires unknown attribute {a}")
                        elif v not in (ts.attributes[a].get("values") or []):
                            iss.error(pw, f"requires {a}={v!r}, not an allowed value")
                else:
                    self._lint_output(m, p, pw, iss)
        # parameters
        for p in d.get("parameters") or []:
            pw = f"{w}: parameters.{p.get('id', '?')}"
            for k in p:
                if k not in PARAM_KEYS:
                    iss.error(pw, f"unknown key {k!r}")
            if p.get("type") not in PARAM_TYPES:
                iss.error(pw, f"type must be one of {sorted(PARAM_TYPES)}")
                continue
            if p["type"] == "enum" and not p.get("enum"):
                iss.error(pw, "enum parameter needs `enum` values")
            if p.get("pattern") is not None:
                if p["type"] != "string":
                    iss.error(pw, "`pattern` only applies to string parameters")
                else:
                    try:
                        re.compile(p["pattern"])
                    except re.error as e:
                        iss.error(pw, f"bad pattern: {e}")
            elif p["type"] == "string":
                iss.warn(pw, "free-text string parameter: add a `pattern` (it is always shell-quoted, but a pattern also "
                             "gives users a clear validation error)")
            if p["type"] == "database":
                dt = p.get("db_type")
                if not dt or dt not in ts or not (dt.startswith("database") or dt.startswith("index")):
                    iss.error(pw, "database parameter needs db_type (a database.* / index.* type)")
                elif not self.dbreg.of_type(ts, dt):
                    iss.warn(pw, f"no registry entries of type {dt}")
            if "default" in p and p["default"] is not None:
                err = check_param_value(p, p["default"], ts, self.dbreg)
                if err:
                    iss.error(pw, f"default: {err}")
        # resources
        r = d.get("resources") or {}
        try:
            int(r.get("cpu", 1))
            parse_memory_gb(r.get("memory", "2G"))
            parse_runtime_s(r.get("runtime", "1h"))
        except (ValueError, TypeError) as e:
            iss.error(f"{w}: resources", str(e))
        # template renders for every mode we can think of
        if d.get("command"):
            from .template import lint_render, lint_shell_safety
            for msg in lint_render(m, ts, self.dbreg):
                iss.error(f"{w}: command", msg)
            for msg in lint_shell_safety(m, ts, self.dbreg):
                iss.error(f"{w}: command", msg)
        # discovery cross-check
        self._lint_discovery(m, w, iss)
        return iss

    def _lint_output(self, m, p, pw, iss):
        ts = self.ts
        t = p["type"]
        tf = p.get("type_from")
        if tf is not None:
            port = tf if isinstance(tf, str) else tf.get("port")
            if port not in m.inputs:
                iss.error(pw, f"type_from refers to unknown input {port!r}")
            if isinstance(tf, dict):
                for a, b in (tf.get("map") or {}).items():
                    for x in (a, b):
                        if x not in ts:
                            iss.error(pw, f"type_from.map: unknown type {x}")
                    if b in ts and not ts.is_a(b, t):
                        iss.error(pw, f"type_from.map target {b} is not a {t}")
        elif ts.is_abstract(t):
            iss.error(pw, f"output type {t} is abstract; give a concrete type or type_from")
        if not p.get("path") and not p.get("parts"):
            iss.error(pw, "output needs `path` and/or `parts`")
        if p.get("parts"):
            names = set(p["parts"])
            # every concrete type this output may resolve to must have these parts
            for ct in self._possible_output_types(m, p):
                req = set(ts.required_parts(ct))
                if ts.kind(ct) == "files" and req and not req <= names and not p.get("path"):
                    iss.error(pw, f"parts {sorted(names)} do not cover required parts {sorted(req)} of {ct}")
        for a in (p.get("attributes") or {}):
            if a not in ts.attributes:
                iss.error(pw, f"unknown attribute {a}")

    def _possible_output_types(self, m, p):
        ts = self.ts
        t, tf = p["type"], p.get("type_from")
        if tf is None:
            return [t]
        if isinstance(tf, dict) and tf.get("map"):
            return list(tf["map"].values())
        src = m.inputs.get(tf if isinstance(tf, str) else tf.get("port"), {}).get("type", t)
        return [x for x in ts.types if ts.is_a(x, src) and not ts.is_abstract(x)] or [t]

    def _lint_discovery(self, m, w, iss):
        runs = (m.d.get("tests") or {}).get("discovery_runs") or []
        tool = (m.d.get("tool") or {}).get("id")
        for rid in runs:
            f = repo_path("reference", "tools", tool or "", "runs", f"{rid}.json")
            if not os.path.exists(f):
                iss.warn(f"{w}: tests", f"discovery run {rid} not found ({os.path.relpath(f, repo_path())})")
                continue
            r = read_json(f)
            if r.get("status") != "ok":
                iss.warn(f"{w}: tests", f"discovery run {rid} status is {r.get('status')}")
                continue
            produced = {o["path"] for o in r.get("outputs", []) if "size" in o}
            for p in m.outputs.values():
                if p.get("required", True) is False or p.get("when"):
                    continue
                candidates = [p["path"]] if p.get("path") else []
                candidates += [list(p.get("parts", {}).values())]
                ok = any((c in produced) if isinstance(c, str) else all(x in produced for x in c) for c in candidates if c)
                if not ok:
                    iss.warn(f"{w}: outputs.{p['id']}", f"not produced by discovery run {rid} "
                             f"(looked for {p.get('path') or list(p.get('parts', {}).values())})")


def check_param_value(p, v, ts, dbreg):
    """Return an error string, or None if `v` is valid for parameter spec `p`."""
    t = p["type"]
    if t == "int":
        if isinstance(v, bool) or not isinstance(v, int):
            return f"{v!r} is not an integer"
    elif t == "float":
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return f"{v!r} is not a number"
    elif t == "bool":
        if not isinstance(v, bool):
            return f"{v!r} is not true/false"
    elif t == "string":
        if not isinstance(v, str):
            return f"{v!r} is not a string"
        if CONTROL_CHARS.search(v):
            return "contains control characters (newlines, tabs, ...)"
        if len(v) > 1000:
            return "is longer than 1000 characters"
        if p.get("pattern") and not re.fullmatch(p["pattern"], v):
            return f"{v!r} does not match the allowed pattern {p['pattern']}"
    elif t == "enum":
        if v not in p.get("enum", []):
            return f"{v!r} not in {p.get('enum')}"
    elif t == "database":
        e = dbreg.get(v)
        if not e:
            return f"unknown database id {v!r}"
        if not ts.is_a(e["type"], p.get("db_type", "")):
            return f"database {v} is a {e['type']}, need {p.get('db_type')}"
        if e.get("status") == "missing":
            return f"database {v} is not installed"
    if t in ("int", "float"):
        if "min" in p and v < p["min"]:
            return f"{v} < min {p['min']}"
        if "max" in p and v > p["max"]:
            return f"{v} > max {p['max']}"
    return None
