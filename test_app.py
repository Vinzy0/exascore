"""
Quick check that app.py rejects bad input and that parallel matches sequential.
Run it:  python test_app.py
"""

import app

if __name__ == "__main__":   # required on Windows for multiprocessing
    app.SIZES[:] = [10_000]   # small batch so the check takes a few seconds
    app.preparing.start()
    workers = str(app.CORES)

    assert app.api("/api/sequential", {"size": ["5"]})[0] == 400, "a size that isn't offered must be rejected"
    assert app.api("/api/parallel", {"size": ["10000"], "workers": ["0"]})[0] == 400, "0 workers must be rejected"
    assert app.api("/api/parallel", {"size": ["10000"], "workers": [workers]})[0] == 400, "parallel needs a sequential run first"
    assert app.api("/api/sequential", {"size": ["10000"]})[0] == 200

    status, result = app.api("/api/parallel", {"size": ["10000"], "workers": [workers]})
    assert status == 200 and result["same"], "parallel must give exactly the same results as sequential"
    print("All checks passed.")
