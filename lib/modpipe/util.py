"""Small shared helpers: repo paths, resource parsing, issue collection."""
import json
import os
import re

import yaml

def _find_root():
    """Directory holding modules/, types/, resources/, pipelines/ (and reference/ in a checkout).

    MODPIPE_REPO overrides. A source checkout is found relative to lib/modpipe. A deployment installs the data
    under $KB_TOP/services/modular_pipeline (see the Makefile deploy-data target)."""
    if os.environ.get("MODPIPE_REPO"):
        return os.path.abspath(os.environ["MODPIPE_REPO"])
    checkout = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if os.path.exists(os.path.join(checkout, "types", "types.yaml")):
        return checkout
    for top in (os.environ.get("KB_TOP"), "/opt/p3/deployment"):
        if top:
            cand = os.path.join(top, "services", "modular_pipeline")
            if os.path.exists(os.path.join(cand, "types", "types.yaml")):
                return cand
    return checkout


REPO = _find_root()


def repo_path(*parts):
    return os.path.join(REPO, *parts)


def read_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def read_json(path):
    with open(path) as f:
        return json.load(f)


_MEM = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([KMGT])B?\s*$", re.I)
_MEM_MULT = {"K": 1 / (1024 * 1024), "M": 1 / 1024, "G": 1, "T": 1024}


def parse_memory_gb(s):
    """'8G' -> 8.0, '512M' -> 0.5, '1T' -> 1024.0. Raises ValueError."""
    m = _MEM.match(str(s))
    if not m:
        raise ValueError(f"bad memory value {s!r} (expected e.g. 8G, 512M)")
    return float(m.group(1)) * _MEM_MULT[m.group(2).upper()]


_DUR = re.compile(r"(\d+(?:\.\d+)?)\s*([smhd])", re.I)
_DUR_MULT = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_runtime_s(s):
    """'1h30m' -> 5400, '45m' -> 2700, 3600 -> 3600. Raises ValueError."""
    if isinstance(s, (int, float)):
        return float(s)
    txt = str(s).strip()
    parts = _DUR.findall(txt)
    if not parts or _DUR.sub("", txt).strip():
        raise ValueError(f"bad runtime value {s!r} (expected e.g. 1h, 30m, 1h30m)")
    return sum(float(n) * _DUR_MULT[u.lower()] for n, u in parts)


def fmt_runtime(sec):
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m = rem // 60
    return f"{h}h{m:02d}m" if h else f"{m}m"


class Issues:
    """Collects errors/warnings with a location prefix."""

    def __init__(self):
        self.errors, self.warnings = [], []
        self.items = []                     # structured: {severity, where, msg} (for UIs that point at a step/port)

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")
        self.items.append({"severity": "error", "where": where, "msg": msg})

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")
        self.items.append({"severity": "warning", "where": where, "msg": msg})

    def extend(self, other):
        self.errors += other.errors
        self.warnings += other.warnings
        self.items += other.items

    @property
    def ok(self):
        return not self.errors

    def report(self, out, quiet=False):
        for e in self.errors:
            print(f"ERROR {e}", file=out)
        if not quiet:
            for w in self.warnings:
                print(f"WARN  {w}", file=out)
