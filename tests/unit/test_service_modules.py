"""Service modules (a whole BV-BRC app as one step, e.g. genome annotation): lint, validation, refusals, compile,
and the helper steps compile inserts (value-file, wait-genome) with the Workspace / data API stubbed."""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe import gowe_helper as gh  # noqa: E402
from modpipe.compile import STRIP_WS, CompileError, compile_pipeline  # noqa: E402
from modpipe.cwl import export  # noqa: E402
from modpipe.pipeline import Validator  # noqa: E402
from modpipe.registry import DatabaseRegistry, Module, ModuleRegistry  # noqa: E402
from modpipe.run import RunError, run_pipeline  # noqa: E402
from modpipe.step import step_pipeline  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402

TS = TypeSystem()
DBS = DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)
CONTIGS = "/u@bvbrc/home/c.fasta"
ANNOT = {"module": "genome_annotation", "params": {"scientific_name": "Escherichia coli test", "taxonomy_id": 562}}


def pipeline(upstream=False, genome_id=True, proteins_to="cdhit"):
    if upstream:
        inputs = {"reads": {"type": "reads.short.paired", "source": {"srr_ids": ["SRR2838702"]}}}
        steps = {"assemble": {"module": "spades", "in": {"reads": "$inputs.reads"}},
                 "annotate": dict(ANNOT, **{"in": {"contigs": "assemble.contigs"}})}
    else:
        inputs = {"contigs": {"type": "sequences.dna.contigs", "source": {"wsids": [CONTIGS]}}}
        steps = {"annotate": dict(ANNOT, **{"in": {"contigs": "$inputs.contigs"}})}
    outputs = {"genome": "annotate.genome"}
    if proteins_to:
        steps["cluster"] = {"module": proteins_to, "in": {"sequences": "annotate.proteins"}}
        outputs["clusters"] = "cluster.clusters"
    if genome_id:
        outputs["genome_id"] = "annotate.genome_id"
    return {"schema": "modpipe/pipeline/v1", "name": "t", "inputs": inputs, "steps": steps, "outputs": outputs}


class LintAndValidate(unittest.TestCase):
    def test_module_lints(self):
        iss = MODS.lint(MODS.get("genome_annotation"))
        self.assertEqual(iss.errors, [])

    def test_lint_rules(self):
        d = copy.deepcopy(MODS.get("genome_annotation").d)
        d["command"] = "echo hi"
        d["outputs"][0]["parts"] = {"a": "x"}
        d["outputs"][-1]["path"] = "x"
        d["service"]["bogus"] = 1
        errs = MODS.lint(Module(d, MODS.get("genome_annotation").path)).errors
        for want in ("no `command`", "single files", "has no path", "unknown key 'bogus'"):
            self.assertTrue(any(want in e for e in errs), (want, errs))
        plain = copy.deepcopy(MODS.get("mafft").d)
        plain["outputs"][0]["indexed_genome"] = True
        errs = MODS.lint(Module(plain, MODS.get("mafft").path)).errors
        self.assertTrue(any("only for service modules" in e for e in errs), errs)

    def test_validates_and_refuses_collections(self):
        iss, plan = Validator(TS, MODS, DBS).validate(pipeline())
        self.assertTrue(iss.ok, iss.errors)
        self.assertEqual(plan["steps"]["annotate"]["output_types"]["genome_id"]["type"], "bvbrc.genome_id")
        p = pipeline(upstream=True)
        p["inputs"]["reads"].update(collection=True, source={"srr_ids": ["SRR2838702", "SRR2838703"]})
        iss, _ = Validator(TS, MODS, DBS).validate(p)
        self.assertTrue(any("sample collection" in e for e in iss.errors), iss.errors)

    def test_local_runner_and_modularstep_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RunError) as c:
                run_pipeline(TS, MODS, DBS, pipeline(), d, dry_run=True)
            self.assertIn("only run through GoWe", str(c.exception))
        p, iss = step_pipeline({"module": "genome_annotation", "contigs": CONTIGS, "output_path": "/u@bvbrc/home",
                                "output_file": "j"}, TS, MODS)
        self.assertIsNone(p)
        self.assertTrue(any("service module" in e for e in iss.errors), iss.errors)


class Compile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.tools = os.path.join(cls.tmp, "tools")
        export(MODS, TS, DBS, cls.tools, image="/img/x.sif", modpipe_home="/release")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def compile(self, p):
        return compile_pipeline(p, TS, MODS, DBS, tools_dir=self.tools)

    def test_file_input_and_wait_step(self):
        wf, job, info = self.compile(pipeline())
        st = wf["steps"]
        self.assertEqual(st["annotate"]["run"], "tools/genome_annotation.cwl")
        self.assertEqual(st["annotate"]["in"]["contigs"], "contigs__file")     # one workspace file: its path
        self.assertEqual(job["contigs__file"], CONTIGS)
        self.assertNotIn("genome_id", st["annotate"]["out"])
        self.assertEqual(st["cluster"]["in"]["sequences"], {"source": "annotate/proteins", "valueFrom": STRIP_WS})
        self.assertEqual(st["annotate_indexed"]["run"], "tools/helper_wait_genome.cwl")
        self.assertEqual(st["annotate_indexed"]["in"]["gto"], {"source": "annotate/genome", "valueFrom": STRIP_WS})
        self.assertEqual(wf["outputs"]["genome_id"]["outputSource"], "annotate_indexed/genome_id")
        self.assertEqual(wf["outputs"]["genome"]["type"], "File?")
        self.assertEqual(set(wf["requirements"]), {"InlineJavascriptRequirement", "StepInputExpressionRequirement"})
        self.assertEqual([s for s, _ in info["gowe_steps"]], ["annotate", "cluster", "annotate_indexed"])

    def test_no_wait_without_genome_id_and_upstream_folder(self):
        wf, _, info = self.compile(pipeline(upstream=True, genome_id=False, proteins_to=None))
        self.assertNotIn("annotate_indexed", wf["steps"])                    # nothing uses genome_id: no wait
        self.assertEqual(wf["steps"]["annotate_contigs_file"],
                         {"run": "tools/helper_value_file.cwl", "in": {"value": "assemble/contigs"}, "out": ["path"]})
        self.assertEqual(wf["steps"]["annotate"]["in"]["contigs"], "annotate_contigs_file/path")
        self.assertEqual(dict(info["gowe_steps"])["annotate_contigs_file"], "helper_value_file")

    def test_refusals(self):
        p = pipeline()
        p["inputs"]["contigs"]["source"] = {"genome_ids": ["562.1"]}
        with self.assertRaises(CompileError) as c:
            self.compile(p)
        self.assertTrue(any("one workspace file" in e for e in c.exception.errors), c.exception.errors)
        os.rename(os.path.join(self.tools, "helper_wait_genome.cwl"), os.path.join(self.tmp, "x.cwl"))
        try:
            with self.assertRaises(CompileError) as c:
                self.compile(pipeline())
            self.assertTrue(any("helper_wait_genome" in e for e in c.exception.errors), c.exception.errors)
        finally:
            os.rename(os.path.join(self.tmp, "x.cwl"), os.path.join(self.tools, "helper_wait_genome.cwl"))


class Helpers(unittest.TestCase):
    def setUp(self):
        self.saved = (gh.ws_meta, gh.ws_children, gh._data_api)

    def tearDown(self):
        gh.ws_meta, gh.ws_children, gh._data_api = self.saved

    def test_value_file(self):
        ws = {"/u@b/home/r/.a/contigs": ("folder", {}, {}),
              "/u@b/home/r/.a/contigs/S1": ("folder", {"modpipe_type": "sequences.dna.contigs",
                                                       "modpipe_files": json.dumps({"_": "contigs.fasta"})}, {}),
              "/u@b/home/r/.b/bam": ("folder", {"modpipe_files": json.dumps({"bam": "a.bam", "index": "a.bai"}),
                                                "modpipe_type": "alignment.reads.bam"}, {}),
              "/u@b/home/r/.c/two": ("folder", {}, {}),
              "/u@b/home/f.gto": ("genome", {}, {})}
        kids = {"/u@b/home/r/.a/contigs": [("/u@b/home/r/.a/contigs/S1", "folder")],
                "/u@b/home/r/.c/two": [("/u@b/home/r/.c/two/A", "folder"), ("/u@b/home/r/.c/two/B", "folder")]}
        gh.ws_meta = lambda p, t: ws.get(p)
        gh.ws_children = lambda p, t: kids.get(p, [])
        self.assertEqual(gh.value_file("/u@b/home/r/.a/contigs", "t"), "/u@b/home/r/.a/contigs/S1/contigs.fasta")
        self.assertEqual(gh.value_file({"class": "File", "location": "ws:///u@b/home/f.gto"}, "t"), "/u@b/home/f.gto")
        for bad, msg in (("/u@b/home/r/.b/bam", "parts"), ("/u@b/home/r/.c/two", "2 items"), ("/u@b/home/no", "does not exist")):
            with self.assertRaises(gh.HelperError) as c:
                gh.value_file(bad, "t")
            self.assertIn(msg, str(c.exception))

    def test_wait_genome(self):
        gh.ws_meta = lambda p, t: ("genome", {}, {"genome_id": "562.9"}) if p.endswith(".genome") else ("folder", {}, {})
        polls = []

        def api(q, token, count=False):
            polls.append((q.split("/")[0], count))
            n = len([x for x in polls if x[0] == "genome"])
            if q.startswith("genome/"):
                return [] if n == 1 else [{"genome_id": "562.9", "patric_cds": 300}]
            return 10 if n == 2 else 352

        gh._data_api = api
        clock = [0]
        gid = gh.wait_genome("ws:///u@b/home/.a/a.genome", "t", timeout=1000, interval=30,
                             sleep=lambda s: clock.__setitem__(0, clock[0] + s), now=lambda: clock[0])
        self.assertEqual(gid, "562.9")
        self.assertEqual(clock[0], 60)                   # missing -> features incomplete -> done
        polls.clear()
        gh._data_api = lambda q, token, count=False: []  # never indexed
        clock[0] = 0
        with self.assertRaises(gh.HelperError) as c:
            gh.wait_genome("/u@b/home/.a/a.genome", "t", timeout=90, interval=30,
                           sleep=lambda s: clock.__setitem__(0, clock[0] + s), now=lambda: clock[0])
        self.assertIn("not indexed after 90s", str(c.exception))
        gh.ws_meta = lambda p, t: ("genome", {}, {})
        with self.assertRaises(gh.HelperError):
            gh.wait_genome("/u@b/home/x.genome", "t")

    def test_main_needs_token_and_writes_output(self):
        with tempfile.TemporaryDirectory() as d:
            job = os.path.join(d, "job.json")
            with open(job, "w") as f:
                json.dump({"value": "/u@b/home/f.gto"}, f)
            env = {k: os.environ.pop(k) for k in ("P3_AUTH_TOKEN", "KB_AUTH_TOKEN", "BVBRC_TOKEN") if k in os.environ}
            try:
                self.assertEqual(gh.main("value-file", job, d), 1)
                os.environ["BVBRC_TOKEN"] = "un=x|sig=y"
                gh.ws_meta = lambda p, t: ("genome", {}, {})
                self.assertEqual(gh.main("value-file", job, d), 0)
                with open(os.path.join(d, "cwl.output.json")) as f:
                    self.assertEqual(json.load(f), {"path": "/u@b/home/f.gto"})
            finally:
                os.environ.pop("BVBRC_TOKEN", None)
                os.environ.update(env)


if __name__ == "__main__":
    unittest.main()
