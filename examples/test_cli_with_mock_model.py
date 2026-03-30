#!/usr/bin/env python3
"""
Test script for CLI tool with mock local model.
"""

import subprocess
import sys


def run_cli_command(command):
    """Run a CLI command and return the output."""
    result = subprocess.run(
        [sys.executable, "splitmind/cli.py"] + command.split(),
        capture_output=True,
        text=True,
        cwd=r"d:\trae1\3\splitmind"
    )
    return result.returncode, result.stdout, result.stderr


def test_run_command():
    """Test the run command."""
    print("Testing run command...")
    code, stdout, stderr = run_cli_command('run "总结人工智能的主要应用领域"')
    print(f"Return code: {code}")
    print(f"Output:\n{stdout}")
    if stderr:
        print(f"Error:\n{stderr}")
    print()


def test_analyze_command():
    """Test the analyze command."""
    print("Testing analyze command...")
    code, stdout, stderr = run_cli_command('analyze "张三的电话是13812345678，邮箱是zhangsan@test.com"')
    print(f"Return code: {code}")
    print(f"Output:\n{stdout}")
    if stderr:
        print(f"Error:\n{stderr}")
    print()


def test_demo_command():
    """Test the demo command."""
    print("Testing demo command...")
    code, stdout, stderr = run_cli_command('demo')
    print(f"Return code: {code}")
    # Only print first 500 characters of output
    print(f"Output (first 500 chars):\n{stdout[:500]}...")
    if stderr:
        print(f"Error:\n{stderr}")
    print()


def test_preview_command():
    """Test the preview command."""
    print("Testing preview command...")
    code, stdout, stderr = run_cli_command('preview "分析人工智能的发展趋势和应用场景"')
    print(f"Return code: {code}")
    print(f"Output:\n{stdout}")
    if stderr:
        print(f"Error:\n{stderr}")
    print()


def test_redact_command():
    """Test the redact command."""
    print("Testing redact command...")
    code, stdout, stderr = run_cli_command('redact "张三的电话是13812345678，邮箱是zhangsan@test.com"')
    print(f"Return code: {code}")
    print(f"Output:\n{stdout}")
    if stderr:
        print(f"Error:\n{stderr}")
    print()


def main():
    print("=== SplitMind CLI Test ===")
    print("Testing CLI commands with mock local model")
    print()
    
    test_run_command()
    test_analyze_command()
    test_demo_command()
    test_preview_command()
    test_redact_command()
    
    print("=== CLI Test Complete ===")


if __name__ == "__main__":
    main()
