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
| `app.py` | Opens the step-by-step web interface and runs the real benchmarks behind it |
| `web/` | The interface page, its font and the mascot images |
| `test_app.py` | Quick check that the interface's server rejects bad input and that parallel matches sequential |

## How the parallel version works
1. Split **S** students into **C** chunks (S/C students each, C = number of CPU cores)
2. Each worker grades its chunk, keeps a `local_count` of students at or above 75, and sorts its own chunk
3. The main process adds every `local_count` into `global_count` and merges the sorted chunks into one ranking

## Run it
Needs Python 3.8+ and nothing else to install.

```
python app.py          # step-by-step interface in your browser (Ctrl+C to stop)
python sequential.py   # ~5 seconds, 100,000 students
python parallel.py     # ~1 minute, demo + benchmark up to 1,000,000 students
python test_app.py     # quick check that everything works
```

`python app.py` opens a page where Exa, the mascot, walks you through the project:
grading one exam, why one core isn't enough, picking the batch size and number of
workers, predicting the winner, then a real sequential vs parallel race with time,
speedup and efficiency charts. It builds the 1,000,000 test students in the
background when it starts (about a minute), so give it a moment before the first run.

## How to run it on your PC (step by step)

**1. Install Python** (skip this if you already have Python 3.8 or newer)
- Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest version.
- **Windows:** on the first screen of the installer, tick **"Add python.exe to PATH"**, then click **Install Now**.
- **Mac:** open the downloaded file and click through the installer.

**2. Download ExaScore**
- On this GitHub page, click the green **Code** button, then **Download ZIP**.
- Unzip it (Windows: right-click the file → **Extract All**). You get a folder called `exascore-main`.

**3. Open a terminal inside that folder**
- **Windows:** open the `exascore-main` folder, click the address bar at the top, type `cmd` and press **Enter**.
- **Mac:** open the **Terminal** app, type `cd ` (with a space after it), drag the `exascore-main` folder
  into the Terminal window and press **Enter**.

**4. Start ExaScore**
- Type this and press **Enter** (on Mac, type `python3` instead of `python`):
  ```
  python app.py
  ```
- Your browser opens the ExaScore page by itself. If it doesn't, copy the link the terminal prints
  (it looks like `http://127.0.0.1:12345`) into your browser.

**5. Use it**
- Click through the steps with Exa. Press **Enter** to continue, or **1–4** to pick an answer.
- Wait about a minute after starting before you reach the race, while the 1,000,000 students are made.
  If you get there early, it waits for them by itself.
- Close other heavy apps (games, video calls) before the race. They use the same CPU and slow the times down.

**6. Stop it**
- Click the terminal window and press **Ctrl+C**, or just close the terminal.

**If something goes wrong**
- *"python is not recognized"* (Windows): Python isn't on PATH. Try `py app.py` instead, or reinstall
  Python with **"Add python.exe to PATH"** ticked.
- *The page says it needs Python running:* you opened `index.html` directly. Close it and start
  ExaScore with `python app.py` instead.
- *The race seems stuck on "Getting the exams ready":* the students are still being made. Give it a minute.

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
