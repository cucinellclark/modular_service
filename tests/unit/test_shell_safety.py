"""Shell-injection hardening: hostile-value lint, parameter patterns, identifier validation, and a real run with a
malicious input file name."""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe.pipeline import Validator  # noqa: E402
from modpipe.registry import DatabaseRegistry, ModuleRegistry  # noqa: E402
from modpipe.run import run_pipeline  # noqa: E402
from modpipe.template import lint_shell_safety  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402
from modpipe.util import read_json  # noqa: E402

TS, DBS = TypeSystem(), DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)

BASE = """
schema: modpipe/module/v1
id: {id}
version: 1
label: test
tool: {{id: none, binary: cat}}
inputs: [{{id: seqs, type: sequences.dna}}]
outputs: [{{id: out, type: sequences.dna.contigs, path: out.fa}}]
parameters: [{{id: tag, type: string, default: "x"}}]
resources: {{cpu: 1, memory: 1G, runtime: 5m}}
command: {cmd}
"""


def module_dir(cmds):
    d = tempfile.mkdtemp()
    for mid, cmd in cmds.items():
        with open(os.path.join(d, f"{mid}.yaml"), "w") as f:
            f.write(BASE.format(id=mid, cmd=json.dumps(cmd)))
    return d


class TestHostileLint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = module_dir({
            "safe": "cat {{ inputs.seqs | q }} > {{ outputs.out }} && echo {{ params.tag | q }} >> {{ outputs.out }}",
            "unquoted_param": "cat {{ inputs.seqs | q }} > {{ outputs.out }} && echo {{ params.tag }}",
            "dquoted_param": "cat {{ inputs.seqs | q }} > {{ outputs.out }} && echo \"{{ params.tag }}\"",
            "unquoted_input": "cat {{ inputs.seqs }} > {{ outputs.out }}",
            "squoted_input": "cat '{{ inputs.seqs }}' > {{ outputs.out }}",
        })
        cls.mods = ModuleRegistry(TS, DBS, module_dir=cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def test_safe_passes(self):
        self.assertEqual(lint_shell_safety(self.mods.get("safe"), TS, DBS), [])

    def test_unsafe_caught(self):
        for mid in ("unquoted_param", "dquoted_param", "unquoted_input", "squoted_input"):
            with self.subTest(module=mid):
                errs = lint_shell_safety(self.mods.get(mid), TS, DBS)
                self.assertTrue(errs, f"{mid} should fail the shell-safety lint")
                self.assertFalse(self.mods.lint(self.mods.get(mid)).ok)

    def test_all_real_modules_safe(self):
        for mid, m in MODS.modules.items():
            with self.subTest(module=mid):
                self.assertEqual(lint_shell_safety(m, TS, DBS), [])
                for p in m.params.values():
                    if p["type"] == "string":
                        self.assertIn("pattern", p, f"{mid}.{p['id']}: string params need a pattern")


def load(name):
    with open(os.path.join(REPO, "pipelines", name)) as f:
        return json.load(f)


class TestValidationHardening(unittest.TestCase):
    def errors(self, p):
        iss, _ = Validator(TS, MODS, DBS).validate(p)
        return iss.errors

    def assertRejected(self, p, text):
        errs = self.errors(p)
        self.assertTrue(any(text in e for e in errs), f"expected {text!r} in {errs}")

    def test_param_patterns(self):
        p = load("wgs_assembly_qc.json")
        p["steps"]["assemble"]["params"]["kmers"] = "21,33; rm -rf ~"
        self.assertRejected(p, "does not match the allowed pattern")
        p = load("long_read_assembly.json")
        p["steps"]["assemble"].setdefault("params", {})["genome_size"] = "5m$(id)"
        self.assertRejected(p, "does not match the allowed pattern")
        p = load("protein_phylogeny.json")
        p["steps"]["tree"]["params"]["model"] = "LG+G\nrm -rf ~"
        self.assertRejected(p, "control characters")
        p = load("protein_phylogeny.json")
        p["steps"]["tree"]["params"]["model"] = "GTR+F+I+G4"
        self.assertEqual(self.errors(p), [])

    def test_identifiers(self):
        p = load("align_and_tree.json")
        p["steps"]["al'ign"] = p["steps"].pop("align")
        p["steps"]["tree"]["in"]["alignment"] = "al'ign.alignment"
        p["outputs"]["alignment"] = "al'ign.alignment"
        self.assertRejected(p, "step ids must match")
        p = load("align_and_tree.json")
        p["outputs"]["../escape"] = "tree.tree"
        self.assertRejected(p, "output names must match")
        p = load("align_and_tree.json")
        p["inputs"]["pro teins"] = p["inputs"].pop("proteins")
        self.assertRejected(p, "input names must match")

    def test_source_ids(self):
        p = load("wgs_assembly_qc.json")
        p["inputs"]["reference"]["source"]["genome_ids"] = ["1206109.14;id"]
        self.assertRejected(p, "bad genome id")
        p = load("multi_sample_assembly.json")
        p["inputs"]["samples"]["source"]["paired_end_libs"][0]["sample_id"] = "S1$(id)"
        self.assertRejected(p, "bad sample_id")
        p = load("wgs_assembly_qc.json")
        p["inputs"]["reads"]["source"] = {"srr_ids": ["SRR123;id"]}
        self.assertRejected(p, "bad SRA run accession")


class TestMaliciousFileName(unittest.TestCase):
    """A real local run: an input file named with shell metacharacters must be treated as data."""

    def test_run(self):
        tmp = tempfile.mkdtemp()
        try:
            mdir = module_dir({"safe": "cat {{ inputs.seqs | q }} > {{ outputs.out }} && echo {{ params.tag | q }} >> {{ outputs.out }}"})
            mods = ModuleRegistry(TS, DBS, module_dir=mdir)
            evil = os.path.join(tmp, "r 1;touch PWNED;$(touch PWNED2)`touch PWNED3`.fa")
            with open(evil, "w") as f:
                f.write(">x\nACGT\n")
            p = {"schema": "modpipe/pipeline/v1", "name": "evil",
                 "inputs": {"seqs": {"type": "sequences.dna", "source": {"files": [evil]}}},
                 "steps": {"s": {"module": "safe", "in": {"seqs": "$inputs.seqs"}, "params": {"tag": "a b;$(touch PWNED4)"}}},
                 "outputs": {"o": "s.out"}}
            rd = os.path.join(tmp, "run")
            rec = run_pipeline(TS, mods, DBS, p, rd, executor="local", cores=1, mem_gb=1)
            self.assertEqual(rec["status"], "ok")
            with open(os.path.join(rd, "steps", "s", "out.fa")) as f:
                self.assertEqual(f.read(), ">x\nACGT\na b;$(touch PWNED4)\n")
            for root, _, files in os.walk(tmp):
                self.assertFalse([f for f in files if f.startswith("PWNED")], f"command injection in {root}")
            self.assertEqual(read_json(os.path.join(rd, "pipeline_run.json"))["status"], "ok")
            shutil.rmtree(mdir)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
