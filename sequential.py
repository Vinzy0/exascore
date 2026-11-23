"""
ExaScore - SEQUENTIAL version
=============================
Processes student exam scores one student at a time, on ONE CPU core.

It does the 3 objectives from our paper:
  1. Grade every student (mark their 100-item answer sheet + compute final grade)
  2. Count how many students scored at or above a threshold (default 75)
  3. Sort (rank) the students from highest to lowest score

Run it:  python sequential.py
"""

import time

from students import THRESHOLD, generate_students, grade_student, print_top, rank_key


def process_sequential(students, threshold=THRESHOLD):
    """Do all 3 objectives one student at a time. Returns (ranked, count)."""
    # Objective 1: grade every student, one by one
    results = [grade_student(s) for s in students]

    # Objective 2: count students at or above the threshold
    count = 0
    for result in results:
        if result[2] >= threshold:
            count += 1

    # Objective 3: sort students from highest to lowest score
    ranked = sorted(results, key=rank_key)

    return ranked, count


if __name__ == "__main__":
    NUM_STUDENTS = 100_000

    print(f"Generating {NUM_STUDENTS:,} students...")
    students = generate_students(NUM_STUDENTS)

    start = time.perf_counter()
    ranked, count = process_sequential(students)
    elapsed = time.perf_counter() - start

    print(f"\nTop 10 students:")
    print_top(ranked)
    print(f"\nStudents scoring {THRESHOLD} or higher: {count:,} of {NUM_STUDENTS:,}")
    print(f"Sequential time: {elapsed:.3f} seconds")
