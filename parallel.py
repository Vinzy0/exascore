"""
ExaScore - PARALLEL version
===========================
Does the same 3 objectives as sequential.py, but splits the students across
all CPU cores using multiprocessing.Pool (SIMD-style: the SAME grading
instructions run on DIFFERENT chunks of student data at the same time).

  1. Split S students into C chunks (S/C students each, C = number of cores)
  2. Each worker grades its chunk, keeps a local_count of students at or
     above the threshold, and sorts its own chunk
  3. The main process adds the local_counts into global_count and merges
     the sorted chunks into one ranking (divide and conquer)

Then it compares sequential vs parallel: execution time, speedup, efficiency.

Run it:  python parallel.py
"""

import heapq
import os
import time
from multiprocessing import Pool

from sequential import process_sequential
from students import THRESHOLD, generate_students, print_top, rank_key


# ---------------------------------------------------------------------------
# What each worker process does with its chunk
# ---------------------------------------------------------------------------
def process_chunk(job):
    chunk, threshold = job

    # Each worker runs the SAME sequential algorithm on its own chunk:
    # grade every student, count those at or above the threshold
    # (local_count, this chunk only), and sort the chunk.
    results, local_count = process_sequential(chunk, threshold)

    return results, local_count


# ---------------------------------------------------------------------------
# Parallel processing
# ---------------------------------------------------------------------------
def process_parallel(students, workers, threshold=THRESHOLD):
    """Do all 3 objectives using `workers` processes. Returns (ranked, count)."""
    # Split S students into C chunks of about S/C each
    chunk_size = -(-len(students) // workers)   # divide, rounding up
    chunks = [students[i:i + chunk_size] for i in range(0, len(students), chunk_size)]
    jobs = [(chunk, threshold) for chunk in chunks]

    # Send one chunk to each worker; they all run at the same time
    with Pool(workers) as pool:
        outputs = pool.map(process_chunk, jobs)

    # Objective 2: add every worker's local_count into the global_count
    global_count = 0
    for results, local_count in outputs:
        global_count += local_count

    # Objective 3 (part 2): merge the already-sorted chunks into one ranking
    sorted_chunks = [results for results, local_count in outputs]
    ranked = list(heapq.merge(*sorted_chunks, key=rank_key))

    return ranked, global_count


# ---------------------------------------------------------------------------
# Demo + benchmark
# ---------------------------------------------------------------------------
if __name__ == "__main__":   # required on Windows for multiprocessing
    WORKERS = os.cpu_count()
    SIZES = [10_000, 100_000, 1_000_000]

    print(f"Generating {SIZES[-1]:,} students (takes a little while)...")
    all_students = generate_students(SIZES[-1])

    # ---- Part 1: demo on 1,000 students ----
    demo_students = all_students[:1_000]
    ranked, count = process_parallel(demo_students, WORKERS)
    print(f"\n=== DEMO: {len(demo_students):,} students, {WORKERS} workers ===")
    print("Top 10 students:")
    print_top(ranked)
    print(f"Students scoring {THRESHOLD} or higher: {count:,} of {len(demo_students):,}")

    # ---- Part 2: sequential vs parallel benchmark ----
    print(f"\n=== BENCHMARK: sequential (1 core) vs parallel ({WORKERS} workers) ===")
    print(f"{'Students':>10} | {'Sequential':>11} | {'Parallel':>9} | {'Speedup':>7} | "
          f"{'Efficiency':>10} | Same results?")
    print("-" * 75)

    for size in SIZES:
        students = all_students[:size]

        start = time.perf_counter()
        seq_ranked, seq_count = process_sequential(students)
        seq_time = time.perf_counter() - start

        start = time.perf_counter()
        par_ranked, par_count = process_parallel(students, WORKERS)
        par_time = time.perf_counter() - start

        speedup = seq_time / par_time          # how many times faster
        efficiency = speedup / WORKERS         # how well each core was used (1.0 = perfect)
        same = "Yes" if (seq_ranked == par_ranked and seq_count == par_count) else "NO!"

        print(f"{size:>10,} | {seq_time:>10.3f}s | {par_time:>8.3f}s | {speedup:>6.2f}x | "
              f"{efficiency:>9.1%} | {same}")

    print("\nSpeedup = sequential time / parallel time")
    print("Efficiency = speedup / number of workers")
