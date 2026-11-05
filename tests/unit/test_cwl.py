"""CWL export (one tool per module running ModularStep) and the worker-side shim's param/output mapping."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe.cwl import app_params, cwl_outputs, export, tool_for  # noqa: E402
from modpipe.registry import DatabaseRegistry, ModuleRegistry  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402

TS = TypeSystem()
DBS = DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)
GOWE_RUNNER = os.path.expanduser(os.environ.get("GOWE_DIR", "~/bvbrc-dev/Copilot/Agents/GoWe")) + "/bin/cwl-runner"


class ExportTests(unittest.TestCase):
    def test_tool_shape_worker(self):
        t = tool_for(MODS.get("fastp"), TS, DBS, image="/img/x.sif", modpipe_home="/repo")
        self.assertEqual(t["class"], "CommandLineTool")
        self.assertEqual(t["inputs"]["module"]["default"], "fastp")
        self.assertEqual(t["inputs"]["reads"]["type"], "Any")
        self.assertEqual(t["inputs"]["reads"]["modpipe:type"], "reads.short")
        self.assertEqual(t["inputs"]["length_required"], {"type": ["null", "int"], "doc": t["inputs"]["length_required"]["doc"],
                                                          "default": 50})
        self.assertEqual(set(t["outputs"]), set(MODS.get("fastp").outputs))
        self.assertEqual(t["outputs"]["trimmed_reads"]["type"], ["null", "Directory"])
        ex = t["hints"]["gowe:Execution"]
        self.assertEqual((ex["executor"], ex["inject_bvbrc_token"]), ("worker", True))
        self.assertEqual(t["hints"]["DockerRequirement"]["dockerPull"], "/img/x.sif")
        self.assertEqual(t["baseCommand"][:2], ["/repo/bin/modpipe", "cwl-step"])
        self.assertEqual(t["requirements"]["ResourceRequirement"], {"coresMin": 4, "ramMin": 8192})

    def test_tool_shape_bvbrc(self):
        t = tool_for(MODS.get("spades"), TS, DBS, mode="bvbrc")
        self.assertEqual(t["hints"], {"gowe:Execution": {"executor": "bvbrc", "bvbrc_app_id": "ModularStep"}})
        self.assertNotIn("requirements", t)
        self.assertEqual(t["inputs"]["mode"]["type"][1]["type"], "enum")

    def test_optional_ports_and_param_types(self):
        t = tool_for(MODS.get("quast"), TS, DBS)
        self.assertEqual(t["inputs"]["contigs"]["modpipe:cardinality"], "many")
        self.assertEqual(t["inputs"]["reference"]["type"], ["null", "Any"])         # optional port
        for m in MODS.modules.values():
            t = tool_for(m, TS, DBS)
            names = set(t["inputs"])
            self.assertEqual(len(names), 1 + len(m.inputs) + len(m.params) + 3, m.id)   # no name collisions

    def test_export_all_validates_with_gowe(self):
        d = tempfile.mkdtemp()
        try:
            paths = export(MODS, TS, DBS, d)
            self.assertEqual(len(paths), len(MODS.modules))
            with open(paths[0]) as f:
                yaml.safe_load(f)
            if not os.access(GOWE_RUNNER, os.X_OK):
                self.skipTest("GoWe cwl-runner not found (set GOWE_DIR)")
            for p in paths:
                r = subprocess.run([GOWE_RUNNER, "validate", p], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{p}: {r.stdout}{r.stderr}")
        finally:
            shutil.rmtree(d)


class ShimTests(unittest.TestCase):
    def test_app_params_flatten(self):
        job = {"module": "fasttree", "model": "lg", "gamma": None,
               "alignment": {"class": "Directory", "location": "ws:///u@bvbrc/home/.j/alignment", "basename": "alignment"},
               "contigs": [{"class": "File", "location": "ws:///u@bvbrc/home/a.fna"}, "/u@bvbrc/home/b.fna"],
               "reads": {"paired_end_libs": [{"read1": {"class": "File", "location": "ws:///u@bvbrc/home/r1"},
                                              "read2": "/u@bvbrc/home/r2", "sample_id": None}]},
               "output_path": "/u@bvbrc/home", "output_file": "j"}
        p = app_params(job)
        self.assertNotIn("gamma", p)
        self.assertEqual(p["alignment"], "/u@bvbrc/home/.j/alignment")
        self.assertEqual(p["contigs"], ["/u@bvbrc/home/a.fna", "/u@bvbrc/home/b.fna"])
        self.assertEqual(p["reads"], {"paired_end_libs": [{"read1": "/u@bvbrc/home/r1", "read2": "/u@bvbrc/home/r2"}]})

    def test_cwl_outputs(self):
        res = {"result_folder": "/u@bvbrc/home/.j/", "values": {"tree": [{"folder": "/u@bvbrc/home/.j/tree"}]}}
        out = cwl_outputs(res, MODS.get("fasttree"))
        self.assertEqual(out["tree"], {"class": "Directory", "location": "ws:///u@bvbrc/home/.j/tree", "basename": "tree"})
        self.assertIsNone(out["log"])


if __name__ == "__main__":
    unittest.main()
