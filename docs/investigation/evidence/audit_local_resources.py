"""Read-only Phase 1 audit. Prints metadata/counts; never imports Firebase SDKs.

Run with Python -B; requires the old builder's PyMuPDF and openpyxl libraries.
Redirect stdout to a file in the NEW repository if a saved report is wanted.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re

import fitz
import openpyxl
import csv


def fingerprint(path):
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def audit(root):
    registry = read_json(root / "database/builder/exam_registry.json")["exams"]
    files = sorted((root / "database/firebase_import").glob("questions_*.json"))
    questions = [q for file in files for q in read_json(file)]
    by_exam = collections.defaultdict(list)
    for q in questions:
        by_exam[q["exam_id"]].append(q)
    exams = []
    for exam in registry:
        rows = by_exam[exam["exam_id"]]
        expected = set(range(exam["question_start"], exam["question_end"] + 1))
        answer_pdf = fitz.open(root / exam["source_answers_pdf"])
        answer_text = answer_pdf[-1].get_text() if exam["exam_id"] == "FE_B_SAMPLE" else "\n".join(p.get_text() for p in answer_pdf)
        pairs = re.findall(r"(?:Q\s*)?(\d+)\s*\n?\s*([a-i])\s*\)?(?=\s|$)", answer_text)
        answers = {int(n): a for n, a in pairs if int(n) in expected}
        answer_pdf.close()
        workbook = openpyxl.load_workbook(root / exam["mapping_xlsx"], read_only=True, data_only=True)
        sheet = workbook.worksheets[0]
        values = list(sheet.values)
        mapping = {"sheets": workbook.sheetnames, "rows": len(values) - 1, "headers": list(values[0])}
        workbook.close()
        with (root / exam["manifest_path"]).open(encoding="utf-8-sig", newline="") as handle:
            manifest = list(csv.DictReader(handle))
        exams.append({
            "exam_id": exam["exam_id"], "paper": exam["paper"], "format": exam["format"],
            "expected": exam["question_count"], "rows": len(rows),
            "missing_numbers": sorted(expected - {r["question_no"] for r in rows}),
            "duplicate_numbers": [k for k, v in collections.Counter(r["question_no"] for r in rows).items() if v > 1],
            "answer_pdf_parsed_count": len(answers),
            "answer_pdf_mismatches": [r["question_id"] for r in rows if answers.get(r["question_no"]) != r["correct_answer"]],
            "invalid_answer_options": [r["question_id"] for r in rows if r["correct_answer"] not in r.get("answer_options", list("abcd"))],
            "published_true": sum(r.get("is_published") is True for r in rows),
            "image_review_status": dict(collections.Counter(r.get("image_review_status", "absent") for r in rows)),
            "populated_fields": {k: sum(bool(r.get(k)) for r in rows) for k in ["chapter", "section", "topic", "notes", "confidence", "free_video_url", "explanation", "question_text", "source_pdf", "source_page_start", "source_page_end"]},
            "mapping_path": exam["mapping_xlsx"], "mapping": mapping,
            "question_pdf": exam["source_questions_pdf"], "answer_pdf": exam["source_answers_pdf"],
            "crop_manifest": exam["manifest_path"], "crop_rows": len(manifest),
            "crop_review_status": dict(collections.Counter(r.get("review_status") for r in manifest)),
            "crop_methods": dict(collections.Counter(r.get("crop_method") for r in manifest)),
            "missing_images": [r["question_id"] for r in rows if not (root / r["question_image_path"]).is_file()],
        })
    books = []
    for name in ["FE Vol 1.pdf", "FE Vol 2.pdf"]:
        path = root / "database/raw" / name
        pdf = fitz.open(path)
        books.append({"path": path.relative_to(root).as_posix(), **fingerprint(path),
                      "pages": len(pdf), "pages_with_text": sum(bool(p.get_text().strip()) for p in pdf),
                      "text_characters": sum(len(p.get_text()) for p in pdf), "bookmarks": pdf.get_toc(),
                      "annotations": dict(collections.Counter(a.type[1] for p in pdf for a in (p.annots() or [])))})
        pdf.close()
    a_rows = [q for q in questions if q["subject"] == "A"]
    images = list((root / "database/builder/output_images").rglob("*.webp"))
    return {"audit_date": "2026-10-21", "source_root": str(root),
            "scope": "Local files only; no Firebase, live-site, deployment, or sign-in requests.",
            "total_questions": len(questions), "subject_a": len(a_rows),
            "subject_b": sum(q["subject"] == "B" for q in questions),
            "sample_questions": len(by_exam["FE_B_SAMPLE"]),
            "duplicate_question_ids": [k for k, v in collections.Counter(q["question_id"] for q in questions).items() if v > 1],
            "json_files": [{"path": f.relative_to(root).as_posix(), **fingerprint(f), "rows": len(read_json(f)), "fields": sorted({k for q in read_json(f) for k in q})} for f in files],
            "exams": exams, "books": books,
            "chapter_counts": dict(sorted(collections.Counter(q["chapter"] for q in a_rows).items())),
            "mapping_confidence": dict(collections.Counter(q["confidence"] for q in a_rows)),
            "subject_b_sections": dict(collections.Counter(q["section"] for q in questions if q["subject"] == "B")),
            "images": {"files": len(images), "bytes": sum(f.stat().st_size for f in images)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("D:/ITPEC Old Questions"))
    args = parser.parse_args()
    print(json.dumps(audit(args.source), ensure_ascii=True, indent=2))
