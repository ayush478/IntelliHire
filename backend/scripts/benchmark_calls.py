"""Measure paid Gemini calls on a fixed workload against a running backend.

Run the backend with ONE uvicorn worker (the call counter is per process),
Gemini + MongoDB configured, and a FRESH database (resumes/JDs already stored
would skip their parses and skew the count):

    python backend/scripts/benchmark_calls.py --base http://localhost:8000 \
        --resumes ./sample_resumes --jd-url https://... --jd-url https://... --reruns 1

Workload: upload every resume, create each JD, rank all resumes against every
JD, then repeat the ranking --reruns more times. Prints the calls the backend
actually made (GET /api/v1/usage) next to a no-cache baseline in which every
ranking re-parses the JD and re-parses + re-detects every resume.
"""
import argparse
import pathlib
import sys

import requests

EXTS = {".pdf", ".docx", ".txt"}


def doc_id(d: dict) -> str:
    return d.get("_id") or d.get("id")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--resumes", required=True, help="folder of .pdf/.docx/.txt resumes")
    ap.add_argument("--jd-url", action="append", required=True, help="job description URL (repeatable)")
    ap.add_argument("--reruns", type=int, default=1, help="extra rankings after the first")
    a = ap.parse_args()
    api = f"{a.base.rstrip('/')}/api/v1"

    files = sorted(p for p in pathlib.Path(a.resumes).iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"no {sorted(EXTS)} files in {a.resumes}")

    requests.post(f"{api}/usage/reset", timeout=10).raise_for_status()

    up = requests.post(f"{api}/resumes/upload/batch",
                       files=[("files", (p.name, p.read_bytes())) for p in files], timeout=600)
    up.raise_for_status()
    resume_ids = [doc_id(r) for r in up.json()]

    jd_ids = []
    for url in a.jd_url:
        r = requests.post(f"{api}/job-descriptions", json={"url": url}, timeout=120)
        r.raise_for_status()
        jd_ids.append(doc_id(r.json()))

    runs = 1 + a.reruns
    for _ in range(runs):
        for jd in jd_ids:
            r = requests.post(f"{api}/scores/batch-score",
                              json={"jd_id": jd, "resume_ids": resume_ids, "weights": None}, timeout=1200)
            r.raise_for_status()

    measured = requests.get(f"{api}/usage", timeout=10).json()
    R, J = len(resume_ids), len(jd_ids)
    baseline = runs * J + runs * J * R * 2  # JD parse per run + (parse + detect) per resume per JD per run
    total = sum(measured.values())

    print(f"workload: {R} resumes x {J} JDs x {runs} runs ({len(files) - R} files skipped as unreadable)")
    for kind in sorted(measured):
        print(f"  {kind:22} {measured[kind]}")
    print(f"measured paid calls:  {total}")
    print(f"no-cache baseline:    {baseline}")
    if baseline:
        print(f"saved:                {100 * (baseline - total) / baseline:.0f}%")


if __name__ == "__main__":
    main()
