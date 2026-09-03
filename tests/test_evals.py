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
