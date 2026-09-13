#!/usr/bin/env python3
"""CLI smoke tests: every command must run end to end without API keys.

This file used to live in examples/ and had three defects, none of which CI
could see (CI only collected tests/):

1. an absolute `cwd` from another machine, so every subprocess call raised
   NotADirectoryError on this one;
2. it invoked `python splitmind/cli.py`, which cannot work: the module belongs
   to a package, so running it by path fails with
   `ModuleNotFoundError: No module named 'splitmind'`;
3. it asserted nothing - it only printed, so it could not fail.
"""

import shlex
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

COMMANDS = [
    'run "总结人工智能的主要应用领域"',
    'analyze "张三的电话是13812345678，邮箱是zhangsan@test.com"',
    "demo",
    'preview "分析人工智能的发展趋势和应用场景"',
    'redact "张三的电话是13812345678，邮箱是zhangsan@test.com"',
]


def run_cli_command(command: str):
    """Run a CLI command from the repo root; return (code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "splitmind.cli", *shlex.split(command)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout, result.stderr


@pytest.mark.parametrize("command", COMMANDS)
def test_cli_command_succeeds(command):
    code, stdout, stderr = run_cli_command(command)

    assert code == 0, f"`{command}` exited {code}\nstdout:\n{stdout}\nstderr:\n{stderr}"
    assert stdout.strip(), f"`{command}` produced no output"


def test_redact_command_masks_the_phone_number():
    """The redacted payload must carry a placeholder, not the raw value."""
    code, stdout, _ = run_cli_command('redact "电话 13812345678"')

    assert code == 0
    assert "[REDACTED_PHONE_1]" in stdout


def test_unknown_command_fails_loudly():
    code, _, stderr = run_cli_command("definitely-not-a-command")

    assert code != 0
