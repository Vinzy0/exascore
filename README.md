# ExaScore: A Student Examination Score Processing System

A Parallel Processing final project. It grades large batches of student exams
**sequentially** (1 CPU core) and in **parallel** (all cores, using Python's
`multiprocessing`), then compares how fast each one is.

## What it does
1. **Grades every student**: marks their 100-item answer sheet against the answer key, then computes the weighted final score (Quiz 20%, Project 20%, Midterm 30%, Final Exam 30%) and the 1.00–5.00 grade
2. **Counts** how many students scored 75 or higher
3. **Ranks** the students from highest to lowest score

## Files
| File | What it does |
|---|---|
| `students.py` | Makes the fake students and holds the grading rules (shared by both versions) |
| `sequential.py` | Grades students one at a time on 1 core |
| `parallel.py` | Splits students across all cores, then compares sequential vs parallel |

## How the parallel version works
1. Split **S** students into **C** chunks (S/C students each, C = number of CPU cores)
2. Each worker grades its chunk, keeps a `local_count` of students at or above 75, and sorts its own chunk
3. The main process adds every `local_count` into `global_count` and merges the sorted chunks into one ranking

## Run it
Needs Python 3.8+ and nothing else to install.

```
python sequential.py   # ~5 seconds, 100,000 students
python parallel.py     # ~1 minute, demo + benchmark up to 1,000,000 students
```

## Results (12-core PC)
| Students | Sequential | Parallel | Speedup | Efficiency |
|---|---|---|---|---|
| 10,000 | 0.125s | 0.449s | 0.28x | 2.3% |
| 100,000 | 1.177s | 0.868s | 1.36x | 11.3% |
| 1,000,000 | 11.613s | 5.082s | 2.28x | 19.0% |

- **Speedup** = sequential time ÷ parallel time (how many times faster)
- **Efficiency** = speedup ÷ number of cores (how well each core was used; 100% = perfect)

On small batches, parallel is slower because starting the worker processes
costs more than the grading itself. On big batches, parallel wins. Efficiency
stays below 100% because sending data to the workers and merging the results
at the end still run on one core (Amdahl's law).
