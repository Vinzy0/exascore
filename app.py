"""
ExaScore - WEB INTERFACE
========================
Run it:  python app.py   (the browser opens by itself; Ctrl+C to stop)

A tiny local web server built into Python (nothing to install). The page in
web/ walks through the project step by step, and every number it shows comes
from running sequential.py and parallel.py for real on this computer.
"""

import json
import os
import threading
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from parallel import process_parallel
from sequential import process_sequential
from students import (ANSWER_KEY, FINAL_EXAM_WEIGHT, MIDTERM_WEIGHT, PROJECT_WEIGHT,
                      QUIZ_WEIGHT, THRESHOLD, generate_students, grade_student)

SIZES = [10_000, 100_000, 1_000_000]
CORES = os.cpu_count() or 1
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

students = []          # all 1,000,000 students, made once in the background
last_sequential = {}   # the last sequential run, so the parallel run can be checked against it


def make_students():
    global students
    # The first N of these are exactly generate_students(N), so one list serves every size
    students = generate_students(SIZES[-1])


preparing = threading.Thread(target=make_students, daemon=True)


def api(path, params):
    """Answer one /api/... request. Returns (status code, data)."""
    if path == "/api/info":
        student_id, name, quiz, project, midterm, answer_sheet = sample = generate_students(1)[0]
        _, _, final_score, grade = grade_student(sample)
        return 200, {
            "cores": CORES, "sizes": SIZES, "threshold": THRESHOLD, "key": ANSWER_KEY,
            "weights": {"quiz": QUIZ_WEIGHT, "project": PROJECT_WEIGHT,
                        "midterm": MIDTERM_WEIGHT, "final": FINAL_EXAM_WEIGHT},
            "sample": {"id": student_id, "name": name, "quiz": quiz, "project": project,
                       "midterm": midterm, "sheet": answer_sheet,
                       "score": final_score, "grade": grade},
        }

    if path == "/api/prepare":
        preparing.join()   # waits only if the students are still being made
        return 200, {"ready": True}

    if path not in ("/api/sequential", "/api/parallel"):
        return 404, {"error": "unknown address"}

    # Everything below runs a benchmark, so check the inputs first
    try:
        size = int(params.get("size", [""])[0])
        workers = int(params.get("workers", ["1"])[0])
    except ValueError:
        return 400, {"error": "size and workers must be numbers"}
    if size not in SIZES or not 1 <= workers <= CORES:
        return 400, {"error": f"size must be one of {SIZES} and workers 1 to {CORES}"}
    preparing.join()
    batch = students[:size]

    if path == "/api/sequential":
        start = time.perf_counter()
        ranked, count = process_sequential(batch)
        seconds = time.perf_counter() - start
        last_sequential.update(size=size, seconds=seconds, ranked=ranked, count=count)
        return 200, {"seconds": seconds, "count": count}

    # /api/parallel
    if last_sequential.get("size") != size:
        return 400, {"error": "run the sequential version first"}
    start = time.perf_counter()
    ranked, count = process_parallel(batch, workers)
    seconds = time.perf_counter() - start
    speedup = last_sequential["seconds"] / seconds
    return 200, {
        "seconds": seconds, "seq_seconds": last_sequential["seconds"],
        "speedup": speedup, "efficiency": speedup / workers, "count": count,
        "same": ranked == last_sequential["ranked"] and count == last_sequential["count"],
        "top": ranked[:10],
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if not url.path.startswith("/api/"):
            return super().do_GET()   # the page, the font
        status, data = api(url.path, parse_qs(url.query))
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass   # keep the terminal quiet


if __name__ == "__main__":   # required on Windows for multiprocessing
    preparing.start()
    # shortcut: one request at a time, so two benchmarks can never share the CPU and skew
    # the timings; fine for one presenter, switch to ThreadingHTTPServer for many viewers
    server = HTTPServer(("127.0.0.1", 0), Handler)   # port 0 = any free port
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"ExaScore is running at {url}  (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")
