#!/usr/bin/env python3
"""Check every quotation in src/mpegi_sd_validator/rules.json against the documents it cites.

The documents are not part of this repository (ISO/IEC 23090-14 is under copyright, the MPEG repository's README files
carry rights the BSD notice does not grant). Give the text of the specification and a clone of the MPEG repository:

    tools/verify_rules.py --spec-text MPEG-Scene-Description-2nd-Ed-04.2024.pdf.layout.txt --mpeg-repo path/to/Scene-Description

A quotation must be at least 25 characters and appear verbatim (whitespace and quotation-mark style aside)."""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "..", "src", "mpegi_sd_validator", "rules.json")


def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("­", "")
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec-text", required=True)
    ap.add_argument("--mpeg-repo", required=True)
    ap.add_argument("--openxr-text", help="text of the OpenXR specification (1.0), for the rules that cite it")
    a = ap.parse_args()
    spec = norm(open(a.spec_text, encoding="utf-8").read())
    bad = 0
    for r in json.load(open(RULES, encoding="utf-8"))["rules"]:
        quotes = [("spec", r.get("spec")), ("mpeg", r.get("mpeg")), ("openxr", r.get("ref"))] + [("spec", x) for x in r.get("spec_more", [])]
        for label, q in quotes:
            if not q:
                continue
            text = q["quote"]
            if len(text) < 25:
                print(f"{r['rule']} {label}: quotation shorter than 25 characters"); bad += 1; continue
            if label == "openxr" and not a.openxr_text:
                print(f"{r['rule']} openxr: not checked (no --openxr-text)"); continue
            hay = spec if label == "spec" else norm(open(a.openxr_text, encoding="utf-8", errors="ignore").read()) if label == "openxr" else norm(open(os.path.join(a.mpeg_repo, q["file"]), encoding="utf-8").read())
            if norm(text) not in hay:
                print(f"{r['rule']} {label}: quotation not found"); bad += 1
    print("all quotations found" if not bad else f"{bad} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
