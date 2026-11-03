#!/usr/bin/env python3
"""List inputs (SRA accessions, workspace paths) referenced by BV-BRC QA test jobs.

    python3 -I tools/extract_qa_inputs.py [/vol/patric3/QA/applications] > reference/qa_test_inputs.tsv

Columns: app, test file, kind (SRA|WS), parameter, value.
"""
import glob, json, os, re, sys

ACC = re.compile(r"^[SED]RR\d+$")
WS = re.compile(r"\.(f(ast)?q|fa(sta)?|fna|faa|ffn|gb[kf]?|genbank|gz|bam|vcf|tsv|csv|nwk|aln|gto|txt|json)$|/home/", re.I)


def walk(x, k, out):
    if isinstance(x, dict):
        for kk, v in x.items():
            walk(v, kk, out)
    elif isinstance(x, list):
        for v in x:
            walk(v, k, out)
    elif isinstance(x, str):
        if ACC.match(x):
            out.add(("SRA", k, x))
        elif x.startswith("/") and k != "output_path" and WS.search(x):
            out.add(("WS", k, x))


def main(root):
    print("app\ttest\tkind\tparam\tvalue")
    for f in sorted(glob.glob(os.path.join(root, "App-*/tests/*.json"))):
        app = os.path.basename(os.path.dirname(os.path.dirname(f)))[4:]
        try:
            d = json.load(open(f))
        except Exception:
            continue
        out = set()
        walk(d, None, out)
        for kind, k, v in sorted(out, key=lambda t: (t[0], str(t[1]), t[2])):
            print(f"{app}\t{os.path.basename(f)}\t{kind}\t{k}\t{v}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/vol/patric3/QA/applications")
