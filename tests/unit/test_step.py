"""App-ModularStep: flat params -> one-step pipeline (lib/modpipe/step.py) and the `parts` input source."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe.pipeline import Validator  # noqa: E402
from modpipe.registry import DatabaseRegistry, ModuleRegistry  # noqa: E402
from modpipe.step import build, is_ws_path, step_pipeline  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402

TS = TypeSystem()
DBS = DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)
BASE = {"output_path": "/u@bvbrc/home/x", "output_file": "j"}
FOLDER = "/u@bvbrc/home/x/.j1/trimmed_reads/S1"
PAIRED_META = {FOLDER: {"type": "folder", "meta": {
    "modpipe_type": "reads.short.paired", "modpipe_attrs": json.dumps({"compression": "gzip"}),
    "modpipe_files": json.dumps({"r1": "trimmed_1.fastq.gz", "r2": "trimmed_2.fastq.gz"}), "modpipe_sample": "S1"}}}
BAM = "/u@bvbrc/home/x/.j2/alignment"
BAM_META = {BAM: {"type": "folder", "meta": {
    "modpipe_type": "alignment.reads.bam", "modpipe_attrs": json.dumps({"sorted": "coordinate"}),
    "modpipe_files": json.dumps({"bam": "aligned.bam", "index": "aligned.bam.bai"})}}}


def errors(params, meta=None):
    p, iss = build(dict(BASE, **params), TS, MODS, DBS, meta)
    return p, iss.errors


class StepTests(unittest.TestCase):
    def test_paired_source_object(self):
        p, errs = errors({"module": "fastp", "length_required": 40, "reads": {"paired_end_libs": [
            {"read1": "/u@bvbrc/home/r1.fq.gz", "read2": "/u@bvbrc/home/r2.fq.gz", "sample_id": "S1"}]}})
        self.assertEqual(errs, [])
        self.assertEqual(p["inputs"]["reads"]["type"], "reads.short.paired")
        self.assertTrue(p["inputs"]["reads"]["collection"])          # sample id kept -> <output>/S1/
        self.assertEqual(p["steps"]["fastp"]["params"], {"length_required": 40})
        self.assertEqual(set(p["outputs"]), set(MODS.get("fastp").outputs))

    def test_sra_accession_is_a_sample(self):
        p, errs = errors({"module": "fastp", "reads": {"srr_ids": ["SRR2838702"]}})
        self.assertEqual(errs, [])
        self.assertTrue(p["inputs"]["reads"]["collection"])          # -> trimmed_reads/SRR2838702/

    def test_output_folder_carries_type_parts_sample(self):
        p, errs = errors({"module": "spades", "reads": FOLDER}, PAIRED_META)
        self.assertEqual(errs, [])
        d = p["inputs"]["reads"]
        self.assertEqual(d["type"], "reads.short.paired")
        self.assertEqual(d["attributes"], {"compression": "gzip"})
        self.assertEqual(d["source"]["paired_end_libs"], [{"read1": FOLDER + "/trimmed_1.fastq.gz",
                                                           "read2": FOLDER + "/trimmed_2.fastq.gz", "sample_id": "S1"}])

    def test_multi_part_folder_becomes_parts(self):
        p, errs = errors({"module": "samtools_coverage", "alignment": BAM}, BAM_META)
        self.assertEqual(errs, [])
        self.assertEqual(p["inputs"]["alignment"]["source"],
                         {"parts": [{"bam": BAM + "/aligned.bam", "index": BAM + "/aligned.bam.bai"}]})
        self.assertNotIn("depth", p["outputs"])                      # switched off by its when: rule, not an error

    def test_type_from_workspace_type_or_input_types(self):
        meta = {"/u@bvbrc/home/p.faa": {"type": "feature_protein_fasta", "meta": {}}}
        p, errs = errors({"module": "mafft", "sequences": "/u@bvbrc/home/p.faa"}, meta)
        self.assertEqual(errs, [])
        self.assertEqual(p["inputs"]["sequences"]["type"], "sequences.protein")
        _, errs = errors({"module": "mafft", "sequences": {"feature_group": "/u@bvbrc/home/Feature Groups/g"}})
        self.assertTrue(any("input_types.sequences" in e for e in errs), errs)
        p, errs = errors({"module": "mafft", "sequences": {"feature_group": "/u@bvbrc/home/Feature Groups/g"},
                          "input_types": {"sequences": "sequences.protein"}})
        self.assertEqual(errs, [])

    def test_list_of_files_gathers(self):
        paths = [f"/u@bvbrc/home/c{i}.fna" for i in (1, 2)]
        meta = {x: {"type": "contigs", "meta": {}} for x in paths}
        p, errs = errors({"module": "quast", "contigs": paths}, meta)
        self.assertEqual(errs, [])
        self.assertEqual(p["inputs"]["contigs"]["source"], {"wsids": paths})
        self.assertTrue(p["inputs"]["contigs"]["collection"])

    def test_refusals(self):
        _, errs = errors({"module": "nope"})
        self.assertEqual(errs, ["module: unknown module 'nope'"])
        _, errs = errors({"module": "spades", "reads": FOLDER, "bogus": 1}, PAIRED_META)
        self.assertTrue(any(e.startswith("bogus:") for e in errs), errs)
        _, errs = errors({"module": "spades"})
        self.assertTrue(any("required input reads" in e for e in errs), errs)
        _, errs = errors({"module": "spades", "reads": "/u@bvbrc/home/x/somefolder"},
                         {"/u@bvbrc/home/x/somefolder": {"type": "folder", "meta": {}}})
        self.assertTrue(any("not a modpipe output folder" in e for e in errs), errs)
        part = "/u@bvbrc/home/x/.j2/alignment/aligned.bam"
        _, errs = errors({"module": "samtools_coverage", "alignment": part},
                         {part: {"type": "bam", "meta": {"modpipe_type": "alignment.reads.bam", "modpipe_part": "bam"}}})
        self.assertTrue(any("give its folder" in e for e in errs), errs)
        _, errs = errors({"module": "mafft", "sequences": "/u@bvbrc/home/p.faa", "input_types": {"nope": "x"}})
        self.assertTrue(any(e.startswith("input_types.nope") for e in errs), errs)

    def test_ws_path(self):
        self.assertTrue(is_ws_path("/u@bvbrc/home/a"))
        self.assertFalse(is_ws_path("/tmp/a"))
        self.assertFalse(is_ws_path("relative"))
        self.assertFalse(is_ws_path("/u@bvbrc"))

    def test_framework_and_private_keys_ignored(self):
        p, iss = step_pipeline(dict(BASE, module="mafft", sequences="/u@bvbrc/home/p.faa", _gowe_task="t1",
                                    input_types={"sequences": "sequences.protein"}), TS, MODS)
        self.assertTrue(iss.ok, iss.errors)

    def test_parts_source_validation(self):
        def check(src, t="alignment.reads.bam"):
            p = {"schema": "modpipe/pipeline/v1", "name": "x",
                 "inputs": {"a": {"type": t, "source": src}},
                 "steps": {"c": {"module": "samtools_coverage", "in": {"alignment": "$inputs.a"}}},
                 "outputs": {"cov": "c.coverage"}}
            iss, _ = Validator(TS, MODS, DBS).validate(p)
            return [e for e in iss.errors if e.startswith("inputs.a")]
        self.assertEqual(check({"parts": {"bam": "/x/a.bam", "index": "/x/a.bam.bai"}}), [])
        self.assertEqual(check({"parts": [{"bam": "/x/a.bam"}]}), [])                  # index is optional
        self.assertTrue(check({"parts": [{"index": "/x/a.bam.bai"}]}))                  # bam is required
        self.assertTrue(check({"parts": [{"bam": "/x/a.bam", "index": "/x/i", "bogus": "/x/b"}]}))
        self.assertTrue(check({"parts": [{"bam": "/x/a.bam", "index": "", }]}))
        self.assertTrue(check({"parts": [{"bam": "/x/a.bam", "index": "/x/i", "sample_id": "bad id"}]}))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            pf, mf, out = (os.path.join(d, n) for n in ("p.json", "m.json", "out.json"))
            with open(pf, "w") as f:
                json.dump(dict(BASE, module="samtools_coverage", alignment=BAM), f)
            with open(mf, "w") as f:
                json.dump(BAM_META, f)
            r = subprocess.run([os.path.join(REPO, "bin", "modpipe"), "step-pipeline", pf, "--ws-meta", mf, "--out", out],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            with open(out) as f:
                self.assertEqual(json.load(f)["steps"]["samtools_coverage"]["module"], "samtools_coverage")
            with open(pf, "w") as f:
                json.dump(dict(BASE, module="samtools_coverage"), f)
            r = subprocess.run([os.path.join(REPO, "bin", "modpipe"), "step-pipeline", pf], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(json.loads(r.stdout)["ok"])


class PartsStagingTests(unittest.TestCase):
    def test_materializer_stages_parts_items(self):
        from modpipe.materialize import Materializer
        with tempfile.TemporaryDirectory() as d:
            for s in ("A", "B"):
                os.makedirs(os.path.join(d, s))
                for n in ("x.bam", "x.bam.bai"):
                    open(os.path.join(d, s, n), "w").close()
            p = {"schema": "modpipe/pipeline/v1", "name": "x",
                 "inputs": {"a": {"type": "alignment.reads.bam", "collection": True, "attributes": {"sorted": "coordinate"},
                                  "source": {"parts": [{"bam": f"{d}/{s}/x.bam", "index": f"{d}/{s}/x.bam.bai", "sample_id": s}
                                                       for s in ("A", "B")]}}},
                 "steps": {"c": {"module": "samtools_coverage", "in": {"alignment": "$inputs.a"}}},
                 "outputs": {"cov": "c.coverage"}}
            v = Validator(TS, MODS, DBS)
            iss, plan = v.validate(p)
            self.assertTrue(iss.ok, iss.errors)
            m = Materializer(TS, MODS, DBS, p, plan, os.path.join(d, "run"), 2, 4)
            m.stage_inputs()
            kind, coll = m.values["$inputs.a"]
            self.assertEqual(kind, "coll")
            self.assertEqual(list(coll), ["A", "B"])
            self.assertEqual(coll["B"].bam, f"{d}/B/x.bam")
            self.assertEqual(coll["B"].index, f"{d}/B/x.bam.bai")


if __name__ == "__main__":
    unittest.main()
