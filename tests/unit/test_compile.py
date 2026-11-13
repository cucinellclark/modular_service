"""modpipe compile: pipeline -> GoWe CWL workflow over the per-module tools."""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe.compile import CompileError, compile_pipeline, write  # noqa: E402
from modpipe.cwl import export  # noqa: E402
from modpipe.registry import DatabaseRegistry, ModuleRegistry  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402

TS = TypeSystem()
DBS = DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)
GOWE_RUNNER = os.path.expanduser(os.environ.get("GOWE_DIR", "~/bvbrc-dev/Copilot/Agents/GoWe")) + "/bin/cwl-runner"


def load(name):
    with open(os.path.join(REPO, "tests", "gowe", name)) as f:
        return json.load(f)


class CompileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.tools = os.path.join(cls.tmp, "tools")
        export(MODS, TS, DBS, cls.tools, image="/img/x.sif", modpipe_home="/release")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def compile(self, p, tools=None):
        return compile_pipeline(p, TS, MODS, DBS, tools_dir=tools or self.tools)

    def test_chain_shape(self):
        wf, job, info = self.compile(load("gowe_align_tree.json"))
        self.assertEqual(info["order"], ["align", "tree"])
        self.assertEqual(wf["class"], "Workflow")
        align, tree = wf["steps"]["align"], wf["steps"]["tree"]
        self.assertEqual(align["run"], "tools/mafft.cwl")
        self.assertEqual(align["in"]["sequences"], "proteins")                 # pipeline input -> workflow input
        self.assertEqual(align["in"]["strategy"], {"default": "auto"})          # step param -> fixed step input
        self.assertEqual(tree["in"]["alignment"], "align/alignment")            # step ref -> upstream port folder
        self.assertEqual(tree["in"]["output_file"], {"default": "tree"})       # <run folder>/.tree/
        self.assertEqual(tree["in"]["output_path"], "output_path")
        self.assertEqual(set(align["out"]), set(MODS.get("mafft").outputs))
        self.assertEqual(wf["outputs"]["tree"], {"type": "string?", "outputSource": "tree/tree",
                                                 "doc": wf["outputs"]["tree"]["doc"]})
        self.assertEqual(wf["inputs"]["proteins"]["type"], "Any")
        self.assertEqual(job["proteins"], {"type": "sequences.protein", "source": {
            "feature_group": "/clark.cucinell@patricbrc.org/home/Feature Groups/rpoB_feature_group_20"}})
        self.assertNotIn("requirements", wf)                                    # no expressions needed
        self.assertNotIn("run_name", wf["inputs"])
        self.assertEqual(info["tools_dir"], os.path.realpath(self.tools))

    def test_list_port_merges_sources(self):
        wf, job, _ = self.compile(load("gowe_reads_qc.json"))
        rep = wf["steps"]["summary"]["in"]["reports"]
        self.assertEqual(rep, {"source": ["map/flagstat", "cov/stats"], "linkMerge": "merge_flattened",
                               "pickValue": "all_non_null"})
        self.assertEqual(wf["steps"]["summary"]["in"]["tables"]["source"], ["cov/coverage"])
        self.assertEqual(wf["requirements"], {"MultipleInputFeatureRequirement": {}})
        self.assertEqual(job["reads"]["source"], {"srr_ids": ["SRR2838702"]})

    def test_refusals(self):
        p = load("gowe_reads_qc.json")
        mixed = copy.deepcopy(p)
        mixed["steps"]["summary"]["in"]["reports"] = ["trim.report_json", "cov.stats"]
        with self.assertRaises(CompileError) as c:
            self.compile(mixed)
        self.assertTrue(any("different types" in e for e in c.exception.errors), c.exception.errors)

        fx = copy.deepcopy(p)
        fx["inputs"]["reads"]["source"] = {"fixture": "bfragilis_samples"}
        with self.assertRaises(CompileError) as c:
            self.compile(fx)
        self.assertTrue(any("fixture" in e for e in c.exception.errors), c.exception.errors)

        bad = copy.deepcopy(p)
        bad["steps"]["cov"]["module"] = "nope"
        with self.assertRaises(CompileError):
            self.compile(bad)                                                    # invalid pipeline: validator errors

        partial = os.path.join(self.tmp, "partial")
        os.makedirs(partial, exist_ok=True)
        shutil.copy(os.path.join(self.tools, "mafft.cwl"), partial)
        with open(os.path.join(self.tools, "fasttree.cwl")) as f:
            t = yaml.safe_load(f)
        t["modpipe:module_version"] = "0.0.1"
        with open(os.path.join(partial, "fasttree.cwl"), "w") as f:
            yaml.safe_dump(t, f)
        with self.assertRaises(CompileError) as c:
            self.compile(load("gowe_align_tree.json"), tools=partial)
        self.assertTrue(any("module version 0.0.1" in e for e in c.exception.errors), c.exception.errors)
        os.remove(os.path.join(partial, "fasttree.cwl"))
        with self.assertRaises(CompileError) as c:
            self.compile(load("gowe_align_tree.json"), tools=partial)
        self.assertTrue(any("no released tool" in e for e in c.exception.errors), c.exception.errors)

    def test_write_and_validate_with_gowe(self):
        wf, job, info = self.compile(load("gowe_reads_qc.json"))
        out = os.path.join(self.tmp, "out")
        path = write(out, wf, job, info["tools_dir"], "modpipe-test")
        self.assertEqual(os.readlink(os.path.join(out, "tools")), info["tools_dir"])
        write(out, wf, job, info["tools_dir"], "modpipe-test")                 # rewrite replaces the link
        with open(os.path.join(out, "job.json")) as f:
            self.assertIn("reads", json.load(f))
        if not os.access(GOWE_RUNNER, os.X_OK):
            self.skipTest("GoWe cwl-runner not found (set GOWE_DIR)")
        r = subprocess.run([GOWE_RUNNER, "validate", path], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_cli(self):
        out = os.path.join(self.tmp, "cli")
        r = subprocess.run([os.path.join(REPO, "bin", "modpipe"), "compile", os.path.join(REPO, "tests", "gowe", "gowe_align_tree.json"),
                            "--out", out, "--tools", self.tools, "--output-path", "/u@bvbrc/home/x", "--run-name", "t1"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(os.path.join(out, "job.json")) as f:
            job = json.load(f)
        self.assertEqual(job["output_path"], "/u@bvbrc/home/x/t1")              # the run folder
        self.assertNotIn("run_name", job)
        self.assertTrue(os.path.exists(os.path.join(out, "modpipe-gowe-test-align-and-tree.cwl")))
        r = subprocess.run([os.path.join(REPO, "bin", "modpipe"), "compile", os.path.join(REPO, "tests", "gowe", "gowe_align_tree.json"),
                            "--out", out, "--tools", self.tools, "--output-path", "/tmp/x"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not a workspace path", r.stderr)


if __name__ == "__main__":
    unittest.main()
