"""
ExaScore - STUDENTS and GRADING RULES
=====================================
Shared by sequential.py and parallel.py so both versions use the exact
same students and the exact same grading rules:

  - generate_students(): makes fake students with 100-item answer sheets
  - grade_student():     marks one answer sheet + computes the final grade
"""

import random

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
NUM_QUESTIONS = 100      # items in the final exam answer sheet
CHOICES = "ABCD"         # possible answers per item
THRESHOLD = 75           # passing score

# Grading weights (they add up to 100%)
QUIZ_WEIGHT = 0.20
PROJECT_WEIGHT = 0.20
MIDTERM_WEIGHT = 0.30
FINAL_EXAM_WEIGHT = 0.30

# The correct answers for the final exam. A fixed seed means the key is
# always the same, even inside the worker processes of parallel.py.
_key_rng = random.Random(2026)
ANSWER_KEY = "".join(_key_rng.choice(CHOICES) for _ in range(NUM_QUESTIONS))

# Philippine grading scale: (minimum score, grade)
GRADE_SCALE = [
    (97, "1.00"), (94, "1.25"), (91, "1.50"), (88, "1.75"), (85, "2.00"),
    (82, "2.25"), (79, "2.50"), (76, "2.75"), (75, "3.00"), (0, "5.00"),
]

FIRST_NAMES = ["Juan", "Maria", "Jose", "Ana", "Mark", "Angel", "John", "Kyla",
               "Paolo", "Bea", "Carlo", "Nicole", "Miguel", "Sofia", "Rafael", "Jasmine"]
LAST_NAMES = ["Dela Cruz", "Santos", "Reyes", "Garcia", "Mendoza", "Bautista",
              "Villanueva", "Ramos", "Aquino", "Castillo", "Torres", "Flores"]


# ---------------------------------------------------------------------------
# Fake data
# ---------------------------------------------------------------------------
def generate_students(count, seed=42):
    """Make `count` fake students. Same seed = same students every run.

    Each student is a tuple:
        (student_id, name, quiz, project, midterm, answer_sheet)
    """
    rng = random.Random(seed)
    students = []
    for student_id in range(1, count + 1):
        name = rng.choice(FIRST_NAMES) + " " + rng.choice(LAST_NAMES)
        skill = rng.uniform(0.5, 1.0)   # chance of answering an item correctly

        # Build the 100-item answer sheet: right answer if they "know" it, else a guess
        answer_sheet = "".join(
            correct if rng.random() < skill else rng.choice(CHOICES)
            for correct in ANSWER_KEY
        )

        quiz = rng.randint(60, 100)
        project = rng.randint(60, 100)
        midterm = rng.randint(50, 100)
        students.append((student_id, name, quiz, project, midterm, answer_sheet))
    return students


# ---------------------------------------------------------------------------
# Grading rules (used by BOTH versions)
# ---------------------------------------------------------------------------
def to_grade(score):
    """Convert a 0-100 score to the 1.00-5.00 grade."""
    for minimum, grade in GRADE_SCALE:
        if score >= minimum:
            return grade


def grade_student(student):
    """Mark one student's answer sheet and compute their weighted final score."""
    student_id, name, quiz, project, midterm, answer_sheet = student

    # Mark the answer sheet item by item
    correct = 0
    for given, right in zip(answer_sheet, ANSWER_KEY):
        if given == right:
            correct += 1
    final_exam = correct / NUM_QUESTIONS * 100

    final_score = (quiz * QUIZ_WEIGHT + project * PROJECT_WEIGHT
                   + midterm * MIDTERM_WEIGHT + final_exam * FINAL_EXAM_WEIGHT)
    final_score = round(final_score, 2)

    return (student_id, name, final_score, to_grade(final_score))


def rank_key(result):
    """Sort order: highest score first; same score -> lower student ID first."""
    student_id, name, final_score, grade = result
    return (-final_score, student_id)


def print_top(ranked, how_many=10):
    """Print the top students as a small table."""
    print(f"  {'Rank':<5} {'ID':<8} {'Name':<22} {'Score':>6}  Grade")
    for rank, (student_id, name, final_score, grade) in enumerate(ranked[:how_many], 1):
        print(f"  {rank:<5} {student_id:<8} {name:<22} {final_score:>6.2f}  {grade}")
