"""Runner tests that need no bioinformatics tools: throwaway modules built from shell utilities.

Covers materialization (scatter/gather, dependencies, output paths), automatic decompression, the local
executor, output collection with workspace types, provenance, failure handling, and Snakefile generation.
"""
import gzip
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe.executors import SnakemakeExecutor  # noqa: E402
from modpipe.materialize import Materializer  # noqa: E402
from modpipe.pipeline import Validator  # noqa: E402
from modpipe.registry import DatabaseRegistry, ModuleRegistry  # noqa: E402
from modpipe.run import RunError, run_pipeline, wstype_for  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402
from modpipe.util import read_json, read_yaml, repo_path  # noqa: E402

TS, DBS = TypeSystem(), DatabaseRegistry()

MODULES = {
    # per-sample: "assemble" = concatenate both read files into a FASTA-ish file
    "fake_assemble": """
schema: modpipe/module/v1
id: fake_assemble
version: 1
label: fake assembler
tool: {id: none, binary: cat}
inputs: [{id: reads, type: reads.short}]
outputs:
  - {id: contigs, type: sequences.dna.contigs, path: contigs.fasta}
  - {id: note, type: report.text, path: note.txt, when: "params.note"}
parameters: [{id: note, type: bool, default: false}]
resources: {cpu: 1, memory: 1G, runtime: 5m}
command: |
  {% if inputs.reads.paired %}cat {{ inputs.reads.r1 | q }} {{ inputs.reads.r2 | q }}{% else %}cat {{ inputs.reads | q }}{% endif %}
  > {{ outputs.contigs }} {% if params.note %}&& echo note > {{ outputs.note }}{% endif %}
""",
    # gather: count lines over all assemblies
    "fake_qc": """
schema: modpipe/module/v1
id: fake_qc
version: 1
label: fake qc
tool: {id: none, binary: wc}
inputs: [{id: contigs, type: sequences.dna.contigs, cardinality: many}]
outputs: [{id: metrics, type: table.tsv.assembly_metrics, path: metrics.tsv}]
resources: {cpu: 1, memory: 1G, runtime: 5m}
command: "wc -l {% for c in inputs.contigs %}{{ c | q }} {% endfor %}> {{ outputs.metrics }}"
""",
    # needs uncompressed input: the engine must gunzip for it
    "fake_plain": """
schema: modpipe/module/v1
id: fake_plain
version: 1
label: needs plain text
tool: {id: none, binary: head}
inputs: [{id: seqs, type: sequences.dna, requires: {compression: none}}]
outputs: [{id: out, type: sequences.dna.contigs, path: first.fa}]
resources: {cpu: 1, memory: 1G, runtime: 5m}
command: "head -c 4 {{ inputs.seqs | q }} | grep -q '>' && cp {{ inputs.seqs | q }} {{ outputs.out }}"
""",
    "fake_fail": """
schema: modpipe/module/v1
id: fake_fail
version: 1
label: always fails
tool: {id: none, binary: false}
inputs: [{id: x, type: sequences.dna}]
outputs: [{id: out, type: report.text, path: never.txt}]
resources: {cpu: 1, memory: 1G, runtime: 5m}
command: "echo boom >&2 && false"
""",
}


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        md = os.path.join(cls.tmp, "modules")
        os.makedirs(md)
        for mid, txt in MODULES.items():
            with open(os.path.join(md, f"{mid}.yaml"), "w") as f:
                f.write(txt)
        cls.mods = ModuleRegistry(TS, DBS, module_dir=md)
        d = os.path.join(cls.tmp, "data")
        os.makedirs(d)
        cls.files = {}
        for s in ("A", "B", "C"):
            for r in (1, 2):
                p = os.path.join(d, f"{s}_{r}.fq")
                with open(p, "w") as f:
                    f.write(f"@{s}{r}\nACGT\n+\nIIII\n")
                cls.files[(s, r)] = p
        cls.gz = os.path.join(d, "g.fa.gz")
        with gzip.open(cls.gz, "wt") as f:
            f.write(">g\nACGTACGT\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def pipeline(self, note=False):
        libs = [{"sample_id": s, "read1": self.files[(s, 1)], "read2": self.files[(s, 2)]} for s in "ABC"]
        return {"schema": "modpipe/pipeline/v1", "name": "fake",
                "inputs": {"samples": {"type": "reads.short.paired", "collection": True, "source": {"paired_end_libs": libs}}},
                "steps": {"asm": {"module": "fake_assemble", "in": {"reads": "$inputs.samples"}, "params": {"note": note}},
                          "qc": {"module": "fake_qc", "in": {"contigs": "asm.contigs"}}},
                "outputs": {"contigs": "asm.contigs", "metrics": "qc.metrics"}}

    def test_lint_fakes(self):
        for mid in MODULES:
            iss = self.mods.lint(self.mods.get(mid))
            self.assertTrue(iss.ok, f"{mid}: {iss.errors}")

    def test_materialize_scatter_gather(self):
        p = self.pipeline()
        iss, plan = Validator(TS, self.mods, DBS).validate(p)
        self.assertTrue(iss.ok, iss.errors)
        rd = os.path.join(self.tmp, "mat")
        m = Materializer(TS, self.mods, DBS, p, plan, rd, cores=4, mem_gb=4)
        m.stage_inputs()
        jobs = m.build_jobs()
        self.assertEqual(sorted(jobs), ["asm__A", "asm__B", "asm__C", "qc"])
        self.assertEqual(jobs["qc"].deps, {"asm__A", "asm__B", "asm__C"})
        self.assertIn(self.files[("B", 2)], jobs["asm__B"].command)
        self.assertNotIn(self.files[("A", 1)], jobs["asm__B"].command)
        for s in "ABC":
            self.assertIn(os.path.join(rd, "steps", "asm", s, "contigs.fasta"), jobs["qc"].command)
        self.assertIsNone(m.values["asm.note"][1]["A"])          # `when: params.note` is false
        self.assertEqual([v.label for v in m.values["asm.contigs"][1].values()], ["A", "B", "C"])
        self.assertEqual(m.values["qc.metrics"][1].label, "qc.metrics")

    def test_local_run_end_to_end(self):
        rd = os.path.join(self.tmp, "run_local")
        rec = run_pipeline(TS, self.mods, DBS, self.pipeline(note=True), rd, executor="local", cores=2, mem_gb=4)
        self.assertEqual(rec["status"], "ok")
        self.assertTrue(all(j["status"] == "ok" for j in rec["jobs"]))
        with open(os.path.join(rd, "steps", "asm", "B", "contigs.fasta")) as f:
            self.assertEqual(f.read(), "@B1\nACGT\n+\nIIII\n@B2\nACGT\n+\nIIII\n")
        with open(os.path.join(rd, "outputs", "metrics", "metrics.tsv")) as f:
            self.assertIn("24 total", f.read())                   # 3 samples x 8 lines
        man = read_json(os.path.join(rd, "outputs", "manifest.json"))
        self.assertEqual({(x["output"], x["sample"]) for x in man},
                         {("contigs", "A"), ("contigs", "B"), ("contigs", "C"), ("metrics", None)})
        self.assertEqual({x["wstype"] for x in man if x["output"] == "contigs"}, {"contigs"})
        self.assertEqual([x["wstype"] for x in man if x["output"] == "metrics"], ["tsv"])
        prov = read_json(os.path.join(rd, "pipeline_run.json"))
        self.assertEqual(prov["status"], "ok")
        self.assertEqual(len(prov["jobs"]), 4)
        # resume: nothing re-runs, markers untouched
        mt = os.path.getmtime(os.path.join(rd, "steps", "qc", ".modpipe", "done"))
        run_pipeline(TS, self.mods, DBS, self.pipeline(note=True), rd, executor="local", cores=2, mem_gb=4, resume=True)
        self.assertEqual(mt, os.path.getmtime(os.path.join(rd, "steps", "qc", ".modpipe", "done")))

    def test_keep_intermediates(self):
        rd = os.path.join(self.tmp, "run_keep")
        p = self.pipeline()
        p["outputs"] = {"metrics": "qc.metrics"}
        run_pipeline(TS, self.mods, DBS, p, rd, executor="local", cores=2, mem_gb=4, keep_intermediates=True)
        man = read_json(os.path.join(rd, "outputs", "manifest.json"))
        names = {x["output"] for x in man}
        self.assertEqual(names, {"metrics", "steps/asm/contigs"})
        self.assertTrue(os.path.exists(os.path.join(rd, "outputs", "steps", "asm", "contigs", "A", "contigs.fasta")))

    def test_auto_decompress(self):
        p = {"schema": "modpipe/pipeline/v1", "name": "gz",
             "inputs": {"g": {"type": "sequences.dna", "source": {"files": [self.gz]}}},
             "steps": {"s": {"module": "fake_plain", "in": {"seqs": "$inputs.g"}}},
             "outputs": {"o": "s.out"}}
        rd = os.path.join(self.tmp, "run_gz")
        rec = run_pipeline(TS, self.mods, DBS, p, rd, executor="local", cores=1, mem_gb=1)
        self.assertEqual(rec["status"], "ok")
        with open(os.path.join(rd, "steps", "s", "first.fa")) as f:
            self.assertEqual(f.read(), ">g\nACGTACGT\n")

    def test_failure_reported_and_downstream_skipped(self):
        p = {"schema": "modpipe/pipeline/v1", "name": "fail",
             "inputs": {"g": {"type": "sequences.dna", "source": {"files": [self.gz]}}},
             "steps": {"bad": {"module": "fake_fail", "in": {"x": "$inputs.g"}}},
             "outputs": {"o": "bad.out"}}
        rd = os.path.join(self.tmp, "run_fail")
        with self.assertRaises(RunError):
            run_pipeline(TS, self.mods, DBS, p, rd, executor="local", cores=1, mem_gb=1)
        prov = read_json(os.path.join(rd, "pipeline_run.json"))
        self.assertEqual(prov["status"], "failed")
        with open(os.path.join(rd, "steps", "bad", ".modpipe", "stderr.txt")) as f:
            self.assertIn("boom", f.read())

    def test_staging_errors(self):
        p = self.pipeline()
        p["inputs"]["samples"]["source"]["paired_end_libs"][0]["read1"] = "/nope/missing.fq"
        with self.assertRaises(RunError) as cm:
            run_pipeline(TS, self.mods, DBS, p, os.path.join(self.tmp, "run_missing"), executor="local", cores=1, mem_gb=1)
        self.assertIn("input file not found", str(cm.exception))
        p = self.pipeline()
        del p["inputs"]["samples"]["collection"]
        with self.assertRaises(RunError) as cm:
            run_pipeline(TS, self.mods, DBS, p, os.path.join(self.tmp, "run_nocoll"), executor="local", cores=1, mem_gb=1)
        self.assertIn("non-collection input", str(cm.exception))

    def test_short_tmpdir(self):
        """Regression: TMPDIR must be short (AF_UNIX socket paths), not inside the deep job directory."""
        p = self.pipeline()
        rd = os.path.join(self.tmp, "x" * 60, "tmpcheck")
        run_pipeline(TS, self.mods, DBS, p, rd, executor="local", cores=1, mem_gb=1, dry_run=True)
        with open(os.path.join(rd, "steps", "asm", "A", ".modpipe", "job.sh")) as f:
            js = f.read()
        self.assertIn('mktemp -d "$_tbase/mp.XXXXXX"', js)
        self.assertNotIn(".modpipe/tmp", js)

    def test_snakefile(self):
        p = self.pipeline()
        rd = os.path.join(self.tmp, "smk")
        run_pipeline(TS, self.mods, DBS, p, rd, executor="snakemake", cores=2, mem_gb=4, dry_run=True)
        with open(os.path.join(rd, ".modpipe", "Snakefile")) as f:
            sf = f.read()
        self.assertEqual(sf.count("\nrule j"), 4)
        self.assertIn("'steps/asm/A/.modpipe/done',", sf)
        qc_rule = sf[sf.index("rule j3_qc:"):]
        for s in "ABC":
            self.assertIn(f"'steps/asm/{s}/.modpipe/done'", qc_rule)


class WsTypeTests(unittest.TestCase):
    def test_wstype_for(self):
        wst = read_yaml(repo_path("types", "wstypes.yaml"))
        self.assertEqual(wstype_for(TS, wst, "sequences.dna.contigs"), "contigs")
        self.assertEqual(wstype_for(TS, wst, "table.tsv.amr"), "tsv")
        self.assertEqual(wstype_for(TS, wst, "reads.short.paired", part="r1"), "reads")
        self.assertEqual(wstype_for(TS, wst, "alignment.reads.bam", part="index", fmt_path="a/aligned.bam.bai"), "bai")
        self.assertEqual(wstype_for(TS, wst, "variants.vcf", part="index", fmt_path="a/calls.vcf.gz.csi"), "csi")
        self.assertEqual(wstype_for(TS, wst, "variants.vcf", part="index", fmt_path="a/calls.vcf.gz.tbi"), "tbi")
        self.assertEqual(wstype_for(TS, wst, "variants.vcf", part="vcf", fmt_path="a/calls.vcf.gz"), "vcf")
        self.assertEqual(wstype_for(TS, wst, "report.image", fmt_path="x/report.pdf"), "pdf")
        self.assertEqual(wstype_for(TS, wst, "alignment.msa.protein"), "aligned_protein_fasta")


if __name__ == "__main__":
    unittest.main()
