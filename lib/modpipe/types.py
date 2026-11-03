"""Type system: loads types/types.yaml and answers is-a / attribute / kind questions."""
from .util import read_yaml, repo_path


class TypeSystem:
    def __init__(self, path=None):
        d = read_yaml(path or repo_path("types", "types.yaml"))
        self.types = d["types"]
        self.formats = d["formats"]
        self.attributes = d.get("attributes", {})
        self.converters = d.get("converters", [])

    def __contains__(self, tid):
        return tid in self.types

    def get(self, tid):
        return self.types[tid]

    @staticmethod
    def ancestors(tid):
        """'a.b.c' -> ['a.b.c', 'a.b', 'a'] (self first)."""
        parts = tid.split(".")
        return [".".join(parts[:i]) for i in range(len(parts), 0, -1)]

    def is_a(self, sub, sup):
        """True if `sub` equals `sup` or is a dotted descendant of it."""
        return sub == sup or sub.startswith(sup + ".")

    def is_abstract(self, tid):
        return bool(self.types.get(tid, {}).get("abstract"))

    def is_registry_only(self, tid):
        return bool(self.types.get(tid, {}).get("registry_only"))

    def kind(self, tid):
        for t in self.ancestors(tid):
            k = self.types.get(t, {}).get("kind")
            if k:
                return k
        return None

    def parts(self, tid):
        """Part names for kind=files types, e.g. ['r1', 'r2'] or ['bam', 'index']."""
        for t in self.ancestors(tid):
            p = self.types.get(t, {}).get("parts")
            if p:
                return list(p)
        return []

    def required_parts(self, tid):
        for t in self.ancestors(tid):
            p = self.types.get(t, {}).get("parts")
            if p:
                return [k for k, v in p.items() if not (isinstance(v, dict) and v.get("optional"))]
        return []

    def fixed_attributes(self, tid):
        """Attributes pinned to a single value by the type or its ancestors, e.g. sequences.dna -> {alphabet: dna}."""
        out = {}
        for t in reversed(self.ancestors(tid)):          # root first, so descendants override
            for a, vals in (self.types.get(t, {}).get("attributes") or {}).items():
                if isinstance(vals, list) and len(vals) == 1:
                    out[a] = vals[0]
        return out

    def allowed_attribute_values(self, tid, attr):
        for t in self.ancestors(tid):
            vals = (self.types.get(t, {}).get("attributes") or {}).get(attr)
            if vals is not None:
                return vals
        return self.attributes.get(attr, {}).get("values")

    def converters_between(self, src, dst):
        return [c for c in self.converters if self.is_a(src, c["from"]) and self.is_a(c["to"], dst)]

    def compatible_targets(self, src):
        """All concrete-or-abstract types that a value of type `src` can be connected to (its ancestors)."""
        return [t for t in self.ancestors(src) if t in self.types]
