"""The graph editor (BV-BRC-Web p3/widget/modpipe) checks connections in the browser while the user draws them.
Its rule must match the server's: for every module output -> module input pair, TypeLogic.js and
TypeSystem.connection must agree. Also runs the editor's model tests (tests/modpipe/model_test.js) on the real
catalog and every template. Skipped when node or the BV-BRC-Web checkout (MODPIPE_WEB_DIR) is not available."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))
WEB = os.environ.get("MODPIPE_WEB_DIR", os.path.expanduser("~/bvbrc-dev/Deployment/BV-BRC-Web"))
TEST_JS = os.path.join(WEB, "tests", "modpipe", "model_test.js")


@unittest.skipUnless(shutil.which("node") and os.path.isfile(TEST_JS), "node or BV-BRC-Web checkout not available")
class CompatParity(unittest.TestCase):
    def test_editor_rules_match_server(self):
        from modpipe.api import Catalog
        cat = Catalog()
        ts = cat.ts
        pairs = []
        for m in cat.mods.modules.values():
            for op in m.outputs.values():
                derived = op.get("type_from") is not None
                for m2 in cat.mods.modules.values():
                    for ip in m2.inputs.values():
                        pairs.append({"src": op["type"], "dst": ip["type"], "derived": derived,
                                      "expect": ts.connection(op["type"], ip["type"], derived)})
        for t in ts.types:                       # pipeline inputs (concrete, not derived) into every port type
            for dst in {ip["type"] for m2 in cat.mods.modules.values() for ip in m2.inputs.values()}:
                pairs.append({"src": t, "dst": dst, "derived": False, "expect": ts.connection(t, dst)})
        templates = {r["template"]: cat.template_pipeline(r["template"])["pipeline"] for r in cat.templates()}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"catalog": cat.catalog(), "templates": templates, "pairs": pairs}, f)
        try:
            r = subprocess.run(["node", TEST_JS, f.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        finally:
            os.unlink(f.name)
        out = r.stdout.decode()
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("all passed", out)


if __name__ == "__main__":
    unittest.main()
