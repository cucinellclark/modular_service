"""Automatic converter insertion, optional template steps (incl. bypass), feature_ids and database_file sources."""
import copy
import json
import os
import sys
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe.pipeline import Validator, auto_convert  # noqa: E402
from modpipe.registry import DatabaseRegistry, ModuleRegistry  # noqa: E402
from modpipe.templates import TemplateError, instantiate  # noqa: E402
from modpipe.types import TypeSystem  # noqa: E402

TS, DBS = TypeSystem(), DatabaseRegistry()
MODS = ModuleRegistry(TS, DBS)
V = Validator(TS, MODS, DBS)


def P(inputs, steps, outputs):
    return {"schema": "modpipe/pipeline/v1", "name": "t", "inputs": inputs, "steps": steps, "outputs": outputs}


class TestAutoConvert(unittest.TestCase):
    def test_type_converter_inserted(self):
        # reads fed to MAFFT (needs sequences): seqtk_seq_fasta is inserted
        p = P({"r": {"type": "reads.short.single", "source": {"srr_ids": ["SRR1"]}}},
              {"aln": {"module": "mafft", "in": {"sequences": "$inputs.r"}}}, {"a": "aln.alignment"})
        iss, _ = V.validate(p)
        self.assertFalse(iss.ok)                                     # plain validation: type mismatch
        p2, iss2, plan = auto_convert(V, p)
        self.assertTrue(iss2.ok, iss2.errors)
        auto = [s for s, st in p2["steps"].items() if st.get("auto")]
        self.assertEqual([p2["steps"][s]["module"] for s in auto], ["seqtk_seq_fasta"])
        self.assertEqual(p2["steps"]["aln"]["in"]["sequences"], f"{auto[0]}.sequences")
        self.assertTrue(any("inserted converter" in w for w in iss2.warnings))
        self.assertIn("alignment.msa.dna", plan["steps"]["aln"]["outputs"]["alignment"])

    def test_attribute_converter_inserted(self):
        # an unsorted BAM into FreeBayes (needs sorted+indexed): samtools_sort_index is inserted
        p = P({"bam": {"type": "alignment.reads.bam", "source": {"files": ["/x.bam"]}, "attributes": {"sorted": "none"}},
               "ref": {"type": "sequences.dna.contigs", "source": {"genome_ids": ["1206109.14"]}}},
              {"call": {"module": "freebayes", "in": {"alignment": "$inputs.bam", "reference": "$inputs.ref"}}},
              {"v": "call.variants"})
        p2, iss, _ = auto_convert(V, p)
        self.assertTrue(iss.ok, iss.errors)
        self.assertIn("samtools_sort_index", [st["module"] for st in p2["steps"].values() if st.get("auto")])

    def test_sam_to_bam(self):
        p = P({"sam": {"type": "alignment.reads.sam", "source": {"files": ["/x.sam"]}},
               "ref": {"type": "sequences.dna.contigs", "source": {"genome_ids": ["1206109.14"]}}},
              {"call": {"module": "bcftools_call", "in": {"alignment": "$inputs.sam", "reference": "$inputs.ref"}}},
              {"v": "call.variants"})
        p2, iss, _ = auto_convert(V, p)
        self.assertTrue(iss.ok, iss.errors)

    def test_unfixable_stays_error(self):
        p = P({"t": {"type": "tree.newick", "source": {"files": ["/t.nwk"]}}},
              {"aln": {"module": "mafft", "in": {"sequences": "$inputs.t"}}}, {"a": "aln.alignment"})
        _, iss, _ = auto_convert(V, p)
        self.assertTrue(any("type mismatch" in e for e in iss.errors))

    def test_shared_converter_reused(self):
        p = P({"r": {"type": "reads.short.single", "source": {"srr_ids": ["SRR1"]}}},
              {"a1": {"module": "mafft", "in": {"sequences": "$inputs.r"}},
               "a2": {"module": "cdhit", "in": {"sequences": "$inputs.r"}}}, {"a": "a1.alignment", "c": "a2.clusters"})
        p2, iss, _ = auto_convert(V, p)
        self.assertTrue(iss.ok, iss.errors)
        self.assertEqual(sum(1 for st in p2["steps"].values() if st.get("auto")), 1)


class TestOptionalSteps(unittest.TestCase):
    INPUTS = {"reads": {"fixture": "portiera_pe"}}

    def test_defaults_keep_all(self):
        p = instantiate("isolate_assembly_characterization", self.INPUTS)
        self.assertTrue({"genes", "amr", "typing"} <= set(p["steps"]))

    def test_disable_drops_step_and_outputs(self):
        p = instantiate("isolate_assembly_characterization", self.INPUTS, {"amr.enabled": False, "typing.enabled": False})
        self.assertNotIn("amr", p["steps"])
        self.assertNotIn("amr_genes", p["outputs"])
        self.assertNotIn("mlst", p["outputs"])
        iss, _ = V.validate(p)
        self.assertTrue(iss.ok, iss.errors)

    def test_disable_drops_list_entries(self):
        p = instantiate("multi_sample_assembly", {"samples": {"fixture": "bfragilis_samples"}}, {"summary.enabled": False})
        self.assertNotIn("summary", p["steps"])
        iss, _ = V.validate(p)
        self.assertTrue(iss.ok, iss.errors)

    def test_bypass(self):
        p = instantiate("sars2_wastewater", {"samples": {"source": {"fixture": "sarscov2_samples"}, "collection": True},
                                             "reference": {"fixture": "sarscov2_genome"}}, {"primertrim.enabled": False})
        self.assertEqual(p["steps"]["variants"]["in"]["alignment"], "map.alignment")
        self.assertNotIn("primertrim.params.primers", json.dumps(p))
        iss, _ = V.validate(p)
        self.assertTrue(iss.ok, iss.errors)

    def test_not_optional(self):
        with self.assertRaises(TemplateError):
            instantiate("isolate_assembly_characterization", self.INPUTS, {"assemble.enabled": False})

    def test_required_dependency_error(self):
        with open(os.path.join(REPO, "pipelines", "isolate_assembly_characterization.json")) as f:
            t = json.load(f)
        t["template"]["optional"]["assemble"] = {"label": "x", "default": True}
        with self.assertRaises(TemplateError) as cm:
            instantiate(t, self.INPUTS, {"assemble.enabled": False})
        self.assertIn("disabled optional step", str(cm.exception))


class TestSources(unittest.TestCase):
    def base(self, src, t="sequences.protein"):
        return P({"q": {"type": t, "source": src}}, {"aln": {"module": "mafft", "in": {"sequences": "$inputs.q"}}},
                 {"a": "aln.alignment"})

    def test_feature_ids(self):
        iss, _ = V.validate(self.base({"feature_ids": ["fig|1206109.14.peg.1", "fig|1206109.14.peg.2"]}))
        self.assertTrue(iss.ok, iss.errors)
        iss, _ = V.validate(self.base({"feature_ids": ["fig|1206109.14.peg.1;id"]}))
        self.assertTrue(any("bad feature id" in e for e in iss.errors))

    def test_database_file(self):
        iss, _ = V.validate(self.base({"database_file": "artic_v4.1:reference"}, "sequences.dna.contigs"))
        self.assertTrue(iss.ok, iss.errors)
        iss, _ = V.validate(self.base({"database_file": "artic_v4.1:nope"}, "sequences.dna.contigs"))
        self.assertTrue(any("has no file" in e for e in iss.errors))
        iss, _ = V.validate(self.base({"database_file": "nodb:reference"}, "sequences.dna.contigs"))
        self.assertTrue(any("unknown database" in e for e in iss.errors))


if __name__ == "__main__":
    unittest.main()
