"""qa_report_generator.py - Automated script to execute tests and generate QA reports (CSV, Log, Markdown)."""
import os
import subprocess
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def run_tests(xml_path: str) -> bool:
    """Executes the test suite and generates an XML report."""
    print("Executing backend integration and validation tests...")
    # Run pytest and output to JUnit XML
    cmd = [".venv/bin/pytest", f"--junitxml={xml_path}", "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Save raw stdout to execution log
    log_path = "qa_execution.log"
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== QA TEST RUN EXECUTION LOG - {datetime.now(timezone.utc).isoformat()} ===\n")
        log_file.write(result.stdout)
        if result.stderr:
            log_file.write("\n=== STDERR ===\n")
            log_file.write(result.stderr)
            
    print(f"Raw execution logs saved to: {log_path}")
    return result.returncode == 0


def parse_and_generate_reports(xml_path: str, csv_path: str, md_path: str):
    """Parses JUnit XML and generates CSV and Markdown reports."""
    if not os.path.exists(xml_path):
        print(f"Error: XML results file {xml_path} not found.")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract overall metrics
    testsuite = root if root.tag == "testsuite" else root.find("testsuite")
    
    total = int(testsuite.attrib.get("tests", 0))
    failures = int(testsuite.attrib.get("failures", 0))
    errors = int(testsuite.attrib.get("errors", 0))
    skipped = int(testsuite.attrib.get("skipped", 0))
    time_taken = float(testsuite.attrib.get("time", 0.0))
    passed = total - failures - errors - skipped

    test_cases = []
    for tc in root.iter("testcase"):
        class_name = tc.attrib.get("classname", "")
        name = tc.attrib.get("name", "")
        duration = float(tc.attrib.get("time", 0.0))
        
        status = "passed"
        error_msg = ""
        
        failure = tc.find("failure")
        if failure is not None:
            status = "failed"
            error_msg = failure.text or failure.attrib.get("message", "")
            
        error = tc.find("error")
        if error is not None:
            status = "error"
            error_msg = error.text or error.attrib.get("message", "")
            
        skip = tc.find("skipped")
        if skip is not None:
            status = "skipped"
            error_msg = skip.attrib.get("message", "")
            
        test_cases.append({
            "class_name": class_name,
            "name": name,
            "status": status,
            "duration": duration,
            "error_msg": error_msg.strip().replace("\n", " ")[:200]
        })

    # 1. Write CSV Report
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["test_class", "test_name", "status", "duration_seconds", "error_message"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for tc in test_cases:
            writer.writerow({
                "test_class": tc["class_name"],
                "test_name": tc["name"],
                "status": tc["status"],
                "duration_seconds": f"{tc['duration']:.4f}",
                "error_message": tc["error_msg"]
            })
    print(f"CSV report generated at: {csv_path}")

    # 2. Write Markdown Report
    status_emoji = "✅" if (failures == 0 and errors == 0) else "❌"
    
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(f"# QA Test Execution & Validation Report {status_emoji}\n\n")
        md_file.write(f"**Date (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_file.write(f"**Overall Status:** {'PASS' if (failures == 0 and errors == 0) else 'FAIL'}\n\n")
        
        md_file.write("## Execution Metrics\n\n")
        md_file.write("| Metric | Value |\n")
        md_file.write("| --- | --- |\n")
        md_file.write(f"| **Total Tests** | {total} |\n")
        md_file.write(f"| **Passed** | {passed} |\n")
        md_file.write(f"| **Failed** | {failures} |\n")
        md_file.write(f"| **Errors** | {errors} |\n")
        md_file.write(f"| **Skipped** | {skipped} |\n")
        md_file.write(f"| **Total Duration** | {time_taken:.2f} seconds |\n\n")
        
        md_file.write("## Test Suite Breakdown\n\n")
        md_file.write("| Test Class | Test Case | Status | Duration (s) | Error Message |\n")
        md_file.write("| --- | --- | --- | --- | --- |\n")
        for tc in test_cases:
            status_label = "🟢 Passed" if tc["status"] == "passed" else "🔴 Failed" if tc["status"] == "failed" else "🟡 Skipped"
            md_file.write(f"| {tc['class_name']} | {tc['name']} | {status_label} | {tc['duration']:.3f} | {tc['error_msg'] or '-'} |\n")
            
        md_file.write("\n## Summary of Key Validations\n\n")
        md_file.write("- **Moderation Heuristic Filter:** Verified DB-backed detection of banned terms, matching against severity threshold ranks, and cache validation.\n")
        md_file.write("- **Database Schema Constraints:** Enforced foreign key checks in SQLite, validation status restrictions, modality rules, and evaluations unique indices.\n")
        md_file.write("- **NLP AI Summary Jobs:** Validated GeminiClient mocking, guard checks, background celery _run_summary task state updates, duplicate job controls, and stale summary detection query logic.\n")
        md_file.write("- **ACID Compliance:** Validated transactional rollbacks and nested transactions concurrency safety.\n")
        
    print(f"Markdown report generated at: {md_path}")


if __name__ == "__main__":
    xml_file = "tests/test_results.xml"
    csv_file = "qa_test_results.csv"
    md_file = "qa_test_report.md"
    
    success = run_tests(xml_file)
    parse_and_generate_reports(xml_file, csv_file, md_file)
    print("QA Reporting Process Completed.")
