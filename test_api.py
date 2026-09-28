#!/usr/bin/env python3
"""
Automated API Test Suite — DocuMind AI
Tests all endpoints of the PDF Chatbot application.

Usage: python test_api.py
Make sure the app is running first: python app.py
"""

import requests
import sys
import json
import os

BASE_URL = "http://localhost:5000"

# ─── Colors ───────────────────────────────────────────────
G = '\033[92m'  # green
R = '\033[91m'  # red
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
E = '\033[0m'   # end

def ok(msg):  print(f"  {G}✓ PASS{E}  {msg}")
def fail(msg): print(f"  {R}✗ FAIL{E}  {msg}")
def info(msg): print(f"  {B}ℹ INFO{E}  {msg}")
def warn(msg): print(f"  {Y}⚠ WARN{E}  {msg}")

results = []

def test(name, fn):
    print(f"\n{Y}▶ {name}{E}")
    try:
        passed, detail = fn()
        if passed:
            ok(detail)
            results.append((name, True))
        else:
            fail(detail)
            results.append((name, False))
    except Exception as e:
        fail(f"Exception: {e}")
        results.append((name, False))


# ─── Tests ────────────────────────────────────────────────

def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    d = r.json()
    assert r.status_code == 200
    assert d['status'] == 'healthy'
    return True, f"Service healthy · model: {d.get('model','N/A')}"

def test_documents_empty_or_loaded():
    r = requests.get(f"{BASE_URL}/api/documents", timeout=5)
    d = r.json()
    assert r.status_code == 200
    assert d['success'] is True
    return True, f"{d['count']} document(s) currently in knowledge base"

def test_upload_no_file():
    r = requests.post(f"{BASE_URL}/api/upload", timeout=5)
    d = r.json()
    assert r.status_code == 400
    assert d['success'] is False
    return True, "Correctly rejected: no file provided"

def test_upload_wrong_type():
    files = {'file': ('test.txt', b'Hello world', 'text/plain')}
    r = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=5)
    d = r.json()
    assert r.status_code == 400
    assert d['success'] is False
    return True, "Correctly rejected: non-PDF file"

def test_chat_no_question():
    r = requests.post(
        f"{BASE_URL}/api/chat",
        json={},
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    d = r.json()
    assert r.status_code == 400
    assert d['success'] is False
    return True, "Correctly rejected: no question provided"

def test_upload_pdf():
    """Upload a real PDF if available, otherwise create a minimal one"""
    # Look for any PDF in current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

    if pdf_files:
        pdf_path = pdf_files[0]
        info(f"Using existing PDF: {pdf_path}")
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            r = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
    else:
        # Create a minimal valid PDF in memory
        warn("No PDF found. Creating minimal test PDF...")
        # Minimal valid PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 44 >> stream
BT /F1 12 Tf 100 700 Td (AppLab Test Document) Tj ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
0000000370 00000 n
trailer << /Size 6 /Root 1 0 R >>
startxref 441
%%EOF"""
        files = {'file': ('test_applab.pdf', pdf_content, 'application/pdf')}
        r = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)

    d = r.json()
    if r.status_code == 200 and d['success']:
        return True, f"Uploaded: {d['filename']} · {d.get('pages','?')} page(s)"
    else:
        return False, f"Upload failed: {d.get('error','unknown')}"

def test_chat_with_document():
    """Test chat — requires at least one document uploaded"""
    # First check if documents exist
    r = requests.get(f"{BASE_URL}/api/documents", timeout=5)
    if r.json()['count'] == 0:
        warn("No documents loaded — skipping chat test")
        return True, "Skipped (no documents loaded)"

    r = requests.post(
        f"{BASE_URL}/api/chat",
        json={"question": "What is this document about?"},
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    d = r.json()
    if r.status_code == 200 and d['success']:
        answer_preview = d['answer'][:80] + '...' if len(d['answer']) > 80 else d['answer']
        return True, f"Got answer · confidence: {d.get('confidence','?')} · model: {d.get('model','?')}"
    else:
        return False, f"Chat failed: {d.get('error','unknown')}"

def test_health_documents_count():
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    d = r.json()
    assert d['status'] == 'healthy'
    return True, f"Health OK · {d.get('documents_loaded', 0)} doc(s) in memory"


# ─── Run all tests ─────────────────────────────────────────

if __name__ == '__main__':
    print(f"\n{B}{'='*55}")
    print(f"  DocuMind AI — API Test Suite")
    print(f"  Target: {BASE_URL}")
    print(f"{'='*55}{E}")

    # Check server is running first
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=3)
    except Exception:
        print(f"\n{R}✗ ERROR: Cannot connect to {BASE_URL}{E}")
        print(f"{Y}  Make sure the app is running: python app.py{E}\n")
        sys.exit(1)

    test("Health Check",                test_health)
    test("Documents Endpoint",          test_documents_empty_or_loaded)
    test("Upload — No File",            test_upload_no_file)
    test("Upload — Wrong File Type",    test_upload_wrong_type)
    test("Chat — No Question",          test_chat_no_question)
    test("Upload — PDF Document",       test_upload_pdf)
    test("Chat — Ask Question",         test_chat_with_document)
    test("Health — Documents Count",    test_health_documents_count)

    # ─── Summary ────────────────────────────────────────────
    passed = sum(1 for _, r in results if r)
    total  = len(results)
    print(f"\n{B}{'='*55}{E}")
    print(f"  Results: {G}{passed}{E}/{total} tests passed")

    for name, r in results:
        status = f"{G}PASS{E}" if r else f"{R}FAIL{E}"
        print(f"  [{status}] {name}")

    if passed == total:
        print(f"\n{G}  ✨ All tests passed! App is working correctly.{E}\n")
        sys.exit(0)
    else:
        print(f"\n{Y}  ⚠ {total-passed} test(s) failed.{E}\n")
        sys.exit(1)
