"""Structural checks for the Harbor eval tasks in evals/tasks/."""

import os
import stat

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_DIR = os.path.join(ROOT, "evals", "tasks")

REQUIRED_FILES = [
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
]

EXECUTABLE_FILES = ["solution/solve.sh", "tests/test.sh"]


def _task_dirs():
    return sorted(
        d for d in os.listdir(TASKS_DIR) if os.path.isdir(os.path.join(TASKS_DIR, d))
    )


def test_eval_tasks_exist():
    assert _task_dirs(), "evals/tasks/ should contain at least one task"


@pytest.mark.parametrize("task", _task_dirs())
def test_task_has_required_files(task):
    for rel in REQUIRED_FILES:
        path = os.path.join(TASKS_DIR, task, rel)
        assert os.path.isfile(path), f"{task}: missing {rel}"


@pytest.mark.parametrize("task", _task_dirs())
def test_scripts_are_executable(task):
    for rel in EXECUTABLE_FILES:
        path = os.path.join(TASKS_DIR, task, rel)
        mode = os.stat(path).st_mode
        assert mode & stat.S_IXUSR, f"{task}: {rel} not executable"


@pytest.mark.parametrize("task", _task_dirs())
def test_no_injected_skill_dir_committed(task):
    # run.sh injects skills/typst as environment/skill for the with-skill
    # variant; it must never be committed.
    assert not os.path.exists(os.path.join(TASKS_DIR, task, "environment", "skill"))


@pytest.mark.parametrize("task", _task_dirs())
def test_dockerfile_matches_canonical(task):
    # Harbor tasks must be self-contained, so each task carries a copy of
    # evals/Dockerfile.base. run.sh re-syncs before every run; this test keeps
    # the committed copies from drifting.
    with open(os.path.join(ROOT, "evals", "Dockerfile.base"), "rb") as f:
        canonical = f.read()
    body = canonical[canonical.index(b"FROM ") :]
    with open(os.path.join(TASKS_DIR, task, "environment", "Dockerfile"), "rb") as f:
        assert f.read() == body, f"{task}: Dockerfile out of sync with Dockerfile.base"
