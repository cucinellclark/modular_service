"""Unit tests for lib/modpipe. Run:  python3 -m unittest discover -s tests/unit -v   (host or container)."""
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
from modpipe.template import Value, build_context, output_value, render_command  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402
from modpipe.util import parse_memory_gb, parse_runtime_s  # noqa: E402

TS = TypeSystem()
DBS = DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)


def load(name):
    with open(os.path.join(REPO, "pipelines", name)) as f:
        return json.load(f)


def validate(p, mods=MODS):
    return Validator(TS, mods, DBS).validate(p)


def errors_matching(iss, text):
    return [e for e in iss.errors if text in e]


class TestUtilAndTypes(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_memory_gb("8G"), 8)
        self.assertEqual(parse_memory_gb("512M"), 0.5)
        self.assertEqual(parse_runtime_s("1h30m"), 5400)
        with self.assertRaises(ValueError):
            parse_runtime_s("soon")

    def test_is_a_and_attrs(self):
        self.assertTrue(TS.is_a("reads.short.paired", "reads"))
        self.assertTrue(TS.is_a("table.tsv.amr", "table.tsv"))
        self.assertFalse(TS.is_a("reads.short", "reads.short.paired"))
        self.assertFalse(TS.is_a("sequences.dnax", "sequences.dna"))   # prefix must end at a dot
        self.assertEqual(TS.fixed_attributes("sequences.dna.contigs"), {"alphabet": "dna"})
        self.assertEqual(TS.parts("reads.short.paired"), ["r1", "r2"])
        self.assertEqual(TS.kind("index.bwa"), "prefix")


class TestModules(unittest.TestCase):
    def test_all_modules_lint_clean(self):
        self.assertTrue(MODS.load_issues.ok, MODS.load_issues.errors)
        self.assertGreaterEqual(len(MODS.modules), 5)
        for mid, m in MODS.modules.items():
            iss = MODS.lint(m)
            self.assertTrue(iss.ok, f"{mid}: {iss.errors}")

    def test_rendered_commands_exact(self):
        """Regression: one shell command per template; no lines glued together or split apart."""
        def render(mid, inputs, out_types={}):
            m = MODS.get(mid)
            outs = {o: output_value(op, out_types.get(o, op["type"]), TS) for o, op in m.outputs.items()}
            params = {p: s.get("default") for p, s in m.params.items()}
            return render_command(m, build_context(m, inputs, outs, params, 4, 8, {}))
        V = lambda t, **kw: Value(t, ts=TS, **kw)
        self.assertEqual(render("fastp", {"reads": V("reads.short.paired", parts={"r1": "/a/r1.fq", "r2": "/a/r2.fq"})},
                                {"trimmed_reads": "reads.short.paired"}),
                         "fastp -w 4 -i /a/r1.fq -I /a/r2.fq -o trimmed_1.fastq.gz -O trimmed_2.fastq.gz "
                         "--detect_adapter_for_pe -q 15 -l 50 -h fastp.html -j fastp.json")
        self.assertEqual(render("spades", {"reads": V("reads.short.paired", parts={"r1": "/a/r1.fq", "r2": "/a/r2.fq"}),
                                           "long_reads": V("reads.long.nanopore", path="/a/l.fq")}),
                         "spades.py --isolate -t 4 -m 8 -1 /a/r1.fq -2 /a/r2.fq --nanopore /a/l.fq -o out")
        self.assertEqual(render("quast", {"contigs": [V("sequences.dna.contigs", path="/a/c1.fa", label="S1"),
                                                      V("sequences.dna.contigs", path="/a/c2.fa", label="S2")],
                                          "reference": None, "features": None}),
                         "quast.py -t 4 -o quast --min-contig 500 -l S1,S2 /a/c1.fa /a/c2.fa")
        self.assertEqual(render("mafft", {"sequences": V("sequences.protein", path="/a/p.faa", attrs={"alphabet": "protein"})},
                                {"alignment": "alignment.msa.protein"}),
                         "mafft --auto --thread 4 --amino /a/p.faa > aligned.fasta")
        self.assertEqual(render("fasttree", {"alignment": V("alignment.msa.dna", path="/a/aln.fa", attrs={"alphabet": "dna"})}),
                         "FastTree -nt -log fasttree.log /a/aln.fa > tree.nwk")

    def test_fastp_render_paired_vs_single(self):
        m = MODS.get("fastp")
        params = {p: s.get("default") for p, s in m.params.items()}
        for t, expect, forbid in (("reads.short.paired", "-I in/r2", "--interleaved_in"),
                                  ("reads.short.single", "-o trimmed.fastq.gz", "-I "),
                                  ("reads.short.interleaved", "--interleaved_in", "-I ")):
            v = Value(t, parts={"r1": "in/r1", "r2": "in/r2"}, ts=TS) if t.endswith("paired") else Value(t, path="in/r", ts=TS)
            out_t = "reads.short.single" if t.endswith("single") else "reads.short.paired"
            outs = {o: output_value(op, out_t if o == "trimmed_reads" else op["type"], TS) for o, op in m.outputs.items()}
            cmd = render_command(m, build_context(m, {"reads": v}, outs, params, 4, 8, {}))
            self.assertIn(expect, cmd, t)
            self.assertNotIn(forbid, cmd, t)

    def _lint_modified(self, edit):
        d = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(REPO, "modules", "fastp.yaml"), d)
            with open(os.path.join(d, "fastp.yaml")) as f:
                txt = f.read()
            with open(os.path.join(d, "fastp.yaml"), "w") as f:
                f.write(edit(txt))
            mods = ModuleRegistry(TS, DBS, module_dir=d)
            return mods.lint(mods.get("fastp")).errors
        finally:
            shutil.rmtree(d)

    def test_lint_unknown_type(self):
        errs = self._lint_modified(lambda t: t.replace("type: reads.short\n    description: Paired",
                                                      "type: reads.nonsense\n    description: Paired"))
        self.assertTrue(any("unknown type reads.nonsense" in e for e in errs), errs)

    def test_lint_template_error(self):
        errs = self._lint_modified(lambda t: t.replace("{{ params.length_required }}", "{{ params.no_such_param }}"))
        self.assertTrue(any("no_such_param" in e for e in errs), errs)

    def test_lint_bad_param_default(self):
        errs = self._lint_modified(lambda t: t.replace("default: 15, min: 0, max: 60", "default: 99, min: 0, max: 60"))
        self.assertTrue(any("default: 99 > max 60" in e for e in errs), errs)


class TestPipelinesValid(unittest.TestCase):
    def test_examples_validate(self):
        for f in sorted(os.listdir(os.path.join(REPO, "pipelines"))):
            if f.endswith(".json"):
                iss, _ = validate(load(f))
                self.assertTrue(iss.ok, f"{f}: {iss.errors}")

    def test_scatter_gather_plan(self):
        iss, plan = validate(load("multi_sample_assembly.json"))
        self.assertTrue(iss.ok, iss.errors)
        self.assertEqual(plan["steps"]["trim"]["scatter"], "samples")
        self.assertEqual(plan["steps"]["assemble"]["scatter"], "samples")
        self.assertIsNone(plan["steps"]["qc"]["scatter"])          # gathered by cardinality: many
        self.assertEqual(plan["steps"]["trim"]["scatter_size"], 3)
        self.assertLessEqual(plan["resources"]["cpu"], 32)
        self.assertLessEqual(plan["resources"]["memory_gb"], 256)

    def test_type_from_map(self):
        p = load("align_and_tree.json")
        _, plan = validate(p)
        self.assertIn("alignment.msa.protein", plan["steps"]["align"]["outputs"]["alignment"])
        p["inputs"]["proteins"]["type"] = "sequences.dna.genes"
        p["steps"]["tree"]["params"]["model"] = "gtr"
        iss, plan = validate(p)
        self.assertTrue(iss.ok, iss.errors)
        self.assertIn("alignment.msa.dna", plan["steps"]["align"]["outputs"]["alignment"])

    def test_interleaved_becomes_paired(self):
        p = load("wgs_assembly_qc.json")
        p["inputs"]["reads"]["type"] = "reads.short.interleaved"
        p["inputs"]["reads"]["source"] = {"wsid": "/u@bvbrc/home/r.fq.gz"}
        iss, plan = validate(p)
        self.assertTrue(iss.ok, iss.errors)
        self.assertIn("reads.short.paired", plan["steps"]["trim"]["outputs"]["trimmed_reads"])


class TestPipelineErrors(unittest.TestCase):
    def setUp(self):
        self.wgs = load("wgs_assembly_qc.json")
        self.tree = load("align_and_tree.json")

    def assertError(self, p, text):
        iss, _ = validate(p)
        self.assertTrue(errors_matching(iss, text), f"expected error containing {text!r}; got {iss.errors}")

    def test_type_mismatch(self):
        p = self.tree
        p["steps"]["tree"]["in"]["alignment"] = "$inputs.proteins"
        self.assertError(p, "type mismatch")

    def test_converter_hint(self):
        p = self.tree
        p["inputs"]["proteins"] = {"type": "reads.short.single", "source": {"single_end_libs": [{"read": "/x.fq"}]}}
        self.assertError(p, "converter available: seqtk_seq_fasta")

    def test_missing_required_input(self):
        del self.wgs["steps"]["assemble"]["in"]["reads"]
        self.assertError(self.wgs, "required input of spades is not connected")

    def test_unknown_module_port_output(self):
        p = copy.deepcopy(self.wgs)
        p["steps"]["qc"]["module"] = "quastx"
        self.assertError(p, "unknown module")
        p = copy.deepcopy(self.wgs)
        p["steps"]["trim"]["in"]["readz"] = "$inputs.reads"
        self.assertError(p, "has no input 'readz'")
        p = copy.deepcopy(self.wgs)
        p["outputs"]["x"] = "assemble.contigz"
        self.assertError(p, "has no output 'contigz'")

    def test_cycle(self):
        p = self.tree
        p["steps"]["align"]["in"]["sequences"] = "tree.tree"
        self.assertError(p, "cycle")

    def test_bad_params(self):
        p = copy.deepcopy(self.wgs)
        p["steps"]["assemble"]["params"]["mode"] = "turbo"
        self.assertError(p, "not in")
        p = copy.deepcopy(self.wgs)
        p["steps"]["trim"]["params"] = {"qualified_quality_phred": 99}
        self.assertError(p, "> max")
        p = copy.deepcopy(self.wgs)
        p["steps"]["trim"]["params"] = {"bogus": 1}
        self.assertError(p, "no parameter 'bogus'")

    def test_template_constraints(self):
        p = copy.deepcopy(self.wgs)
        p["inputs"]["reads"] = {"type": "reads.short.single", "source": {"single_end_libs": [{"read": "/x.fq"}]}}
        p["steps"]["assemble"]["params"]["mode"] = "meta"
        self.assertError(p, "SPAdes --meta needs paired-end reads")
        p = self.tree
        p["steps"]["tree"]["params"]["model"] = "gtr"
        self.assertError(p, "FastTree -gtr is for DNA alignments")
        p = copy.deepcopy(self.wgs)
        p["inputs"]["gff"] = {"type": "annotation.gff", "source": {"wsid": "/x.gff"}}
        p["steps"]["qc"]["in"]["features"] = "$inputs.gff"
        del p["steps"]["qc"]["in"]["reference"]
        self.assertError(p, "require a reference")

    def test_two_collections(self):
        p = load("multi_sample_assembly.json")
        p["inputs"]["more"] = copy.deepcopy(p["inputs"]["samples"])
        p["inputs"]["long"] = {"type": "reads.long.nanopore", "collection": True, "source": {"files": ["/a.fq", "/b.fq"]}}
        p["steps"]["assemble"]["in"]["long_reads"] = "$inputs.long"
        self.assertError(p, "scatters over two collections")

    def test_list_into_single_port(self):
        p = self.tree
        p["steps"]["tree"]["in"]["alignment"] = ["align.alignment", "align.alignment"]
        self.assertError(p, "needs a cardinality: many port")

    def test_version_pin(self):
        self.wgs["steps"]["assemble"]["module_version"] = 2
        self.assertError(self.wgs, "pinned module_version 2")

    def test_abstract_and_bad_input(self):
        p = self.tree
        p["inputs"]["proteins"]["type"] = "sequences"
        self.assertError(p, "abstract")
        p["inputs"]["proteins"] = {"type": "sequences.protein", "source": {"ftp": "x"}}
        self.assertError(p, "unknown source keys")

    def test_expose(self):
        self.tree["template"]["expose"].append("tree.params.nope")
        self.assertError(self.tree, "has no parameter nope")


class TestTemplates(unittest.TestCase):
    def setUp(self):
        from modpipe.templates import TemplateError, instantiate
        self.inst, self.TE = instantiate, TemplateError
        self.inputs = {"reads": {"srr_ids": ["SRR1"]}, "reference": {"genome_ids": ["1206109.14"]}}

    def test_fill(self):
        p = self.inst("wgs_assembly_qc", self.inputs, {"assemble.params.mode": "careful"})
        self.assertEqual(p["steps"]["assemble"]["params"]["mode"], "careful")
        self.assertEqual(p["inputs"]["reads"]["source"], {"srr_ids": ["SRR1"]})
        self.assertNotIn("template", p)
        iss, _ = validate(p)
        self.assertTrue(iss.ok, iss.errors)

    def test_full_input_override(self):
        p = self.inst("multi_sample_assembly", {"samples": {"source": {"srr_ids": ["SRR1", "SRR2"]}, "collection": True}})
        self.assertEqual(p["inputs"]["samples"]["source"]["srr_ids"], ["SRR1", "SRR2"])

    def test_rejections(self):
        with self.assertRaises(self.TE):
            self.inst("wgs_assembly_qc", {"reads": {"srr_ids": ["SRR1"]}})               # missing reference
        with self.assertRaises(self.TE):
            self.inst("wgs_assembly_qc", {**self.inputs, "extra": {"files": ["/x"]}})     # unknown input
        with self.assertRaises(self.TE):
            self.inst("wgs_assembly_qc", self.inputs, {"assemble.params.kmers": "21"})    # not exposed
        with self.assertRaises(self.TE):
            self.inst("no_such_template", self.inputs)


class TestCuratedTemplates(unittest.TestCase):
    """Every curated template has fixture test inputs, instantiates, and validates."""

    def test_all_templates(self):
        from modpipe.templates import instantiate
        pdir, tdir = os.path.join(REPO, "pipelines"), os.path.join(REPO, "tests", "templates")
        names = sorted(f[:-5] for f in os.listdir(pdir) if f.endswith(".json"))
        self.assertGreaterEqual(len(names), 9)
        for n in names:
            with self.subTest(template=n):
                tp = os.path.join(tdir, f"{n}.json")   # _variant_*.json files are extra cases, not required
                self.assertTrue(os.path.exists(tp), f"missing tests/templates/{n}.json")
                with open(tp) as f:
                    t = json.load(f)
                with open(os.path.join(pdir, f"{n}.json")) as f:
                    self.assertIn("label", json.load(f).get("template", {}), "templates need a UI label")
                p = instantiate(n, t.get("inputs"), t.get("params"))
                iss, _ = validate(p)
                self.assertTrue(iss.ok, iss.errors)

    def test_links_copy_value(self):
        from modpipe.templates import instantiate
        p = instantiate("taxonomic_profile", {"samples": {"fixture": "sarscov2_samples"}},
                        {"classify.params.db": "kraken2_silva"})
        self.assertEqual(p["steps"]["abundance"]["params"]["db"], "kraken2_silva")


class TestDatabaseParams(unittest.TestCase):
    """A throwaway module with a database parameter, exercising registry ids, types and partition routing."""

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        with open(os.path.join(cls.dir, "kraken2.yaml"), "w") as f:
            f.write("""
schema: modpipe/module/v1
id: kraken2
version: 1
label: test kraken2
tool: {id: kraken2, binary: kraken2}
inputs: [{id: reads, type: reads.short}]
outputs: [{id: report, type: taxonomy.kraken.report, path: report.txt}]
parameters: [{id: db, type: database, db_type: database.kraken2, default: kraken2_silva}]
resources: {cpu: 4, memory: 8G, runtime: 1h}
command: "kraken2 --db {{ dbs.db | q }} --report {{ outputs.report }} {{ (inputs.reads.r1 if inputs.reads.paired else inputs.reads) | q }}"
""")
        cls.mods = ModuleRegistry(TS, DBS, module_dir=cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def pipe(self, db):
        return {"schema": "modpipe/pipeline/v1", "name": "t",
                "inputs": {"r": {"type": "reads.short.paired", "source": {"srr_ids": ["SRR1"]}}},
                "steps": {"k": {"module": "kraken2", "in": {"reads": "$inputs.r"}, "params": {"db": db}}},
                "outputs": {"rep": "k.report"}}

    def test_lint(self):
        iss = self.mods.lint(self.mods.get("kraken2"))
        self.assertTrue(iss.ok, iss.errors)

    def test_good_and_partition(self):
        iss, plan = validate(self.pipe("kraken2_brc"), self.mods)
        self.assertTrue(iss.ok, iss.errors)
        self.assertEqual(plan["resources"]["partition"], "kraken_db")
        self.assertEqual(plan["resources"]["memory_gb"], 150)

    def test_wrong_db_type_and_missing(self):
        iss, _ = validate(self.pipe("genomad_db_1.9"), self.mods)
        self.assertTrue(errors_matching(iss, "need database.kraken2"), iss.errors)
        iss, _ = validate(self.pipe("no_such_db"), self.mods)
        self.assertTrue(errors_matching(iss, "unknown database id"), iss.errors)


if __name__ == "__main__":
    unittest.main()
