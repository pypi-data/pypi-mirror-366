#!/usr/bin/env python3
"""
Smoke test script for tokker CLI tool.

This script performs basic functionality tests to ensure
that both tiktoken and HuggingFace models work correctly
after installation.
"""

import subprocess
import json
import tempfile
import os
from typing import List


def run_command(cmd: List[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        # Use local module instead of global tok command
        if cmd[0] == "tok":
            cmd = ["python", "-m", "tokker.cli.tokenize"] + cmd[1:]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def test_models_list():
    """Test the --models command."""
    # Test models list
    exit_code, stdout, stderr = run_command(["tok", "--models"])
    assert exit_code == 0, f"Models list failed: {stderr}"
    assert "--- OpenAI ---" in stdout, "Models output missing OpenAI section"
    assert "--- HuggingFace ---" in stdout, "Models output missing HuggingFace section"
    assert "cl100k_base" in stdout, "Models output missing expected model"


def test_tiktoken_model():
    """Test tiktoken model functionality."""
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world", "--model", "cl100k_base"
    ])

    assert exit_code == 0, f"Tiktoken tokenization failed: {stderr}"

    result = json.loads(stdout)
    expected_fields = ["token_strings", "token_ids", "token_count", "model", "provider"]

    for field in expected_fields:
        assert field in result, f"Missing field '{field}' in tiktoken result"

    assert result["provider"] == "OpenAI", f"Expected provider 'OpenAI', got '{result['provider']}'"
    assert result["model"] == "cl100k_base", f"Expected model 'cl100k_base', got '{result['model']}'"
    assert result["token_count"] == len(result["token_strings"]), "Token count mismatch"


def test_huggingface_model():
    """Test HuggingFace model functionality."""
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world", "--model", "gpt2"
    ])

    assert exit_code == 0, f"HuggingFace tokenization failed: {stderr}"

    result = json.loads(stdout)
    expected_fields = ["token_strings", "token_ids", "token_count", "model", "provider"]

    for field in expected_fields:
        assert field in result, f"Missing field '{field}' in HuggingFace result"

    assert result["provider"] == "HuggingFace", f"Expected provider 'HuggingFace', got '{result['provider']}'"
    assert result["model"] == "gpt2", f"Expected model 'gpt2', got '{result['model']}'"
    assert result["token_count"] == len(result["token_strings"]), "Token count mismatch"


def test_output_formats():
    """Test different output formats."""
    # Test plain format
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world", "--model", "cl100k_base", "--output", "plain"
    ])

    assert exit_code == 0, f"Plain format failed: {stderr}"
    assert "⎮" in stdout, "Plain format missing delimiter"

    # Test count format
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world", "--model", "cl100k_base", "--output", "count"
    ])

    assert exit_code == 0, f"Count format failed: {stderr}"

    result = json.loads(stdout)
    assert "token_count" in result, "Count format missing token_count"


def test_stdin_input():
    """Test stdin input functionality."""
    # Create a temporary file with test content
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Hello from stdin")
        temp_file = f.name

    try:
        # Test stdin input using shell pipe
        exit_code, stdout, stderr = run_command([
            "sh", "-c", f"cat {temp_file} | python -m tokker.cli.tokenize --model cl100k_base"
        ])

        assert exit_code == 0, f"Stdin input failed: {stderr}"

        result = json.loads(stdout)
        assert "token_count" in result, "Stdin result missing token_count"

    finally:
        os.unlink(temp_file)


def test_model_default():
    """Test model default functionality."""
    # Set default model
    exit_code, stdout, stderr = run_command([
        "tok", "--model-default", "cl100k_base"
    ])

    assert exit_code == 0, f"Setting default model failed: {stderr}"
    assert "✓ Default model set to: cl100k_base" in stdout, "Default model confirmation missing"

    # Test using default model (no --model specified)
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world"
    ])

    assert exit_code == 0, f"Using default model failed: {stderr}"

    result = json.loads(stdout)
    assert result["model"] == "cl100k_base", f"Default model not used, got '{result['model']}'"


def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid model
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world", "--model", "nonexistent-model"
    ])

    assert exit_code != 0, "Invalid model should have failed"
    assert "Error:" in stderr, "Error message not found in stderr"

    # Test invalid model for default
    exit_code, stdout, stderr = run_command([
        "tok", "--model-default", "nonexistent-model"
    ])

    assert exit_code != 0, "Invalid default model should have failed"


def test_history_functionality():
    """Test history and history-clear functionality."""
    # Clear any existing history first
    exit_code, stdout, stderr = run_command([
        "tok", "--history-clear"
    ])
    # Don't assert on exit code as history might be empty

    # Use a model to create history
    exit_code, stdout, stderr = run_command([
        "tok", "Hello world", "--model", "cl100k_base"
    ])
    assert exit_code == 0, f"Model usage for history failed: {stderr}"

    # Check that history shows the model
    exit_code, stdout, stderr = run_command([
        "tok", "--history"
    ])
    assert exit_code == 0, f"History command failed: {stderr}"
    assert "cl100k_base" in stdout, "History missing expected model"
    assert "Model History" in stdout, "History output missing header"

    # Test history clear with confirmation (simulate 'y' response)
    import subprocess
    try:
        proc = subprocess.Popen(
            ["python", "-m", "tokker.cli.tokenize", "--history-clear"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = proc.communicate(input="y\n", timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            assert False, "History clear command timed out"
        assert proc.returncode == 0, f"History clear failed: {stderr}"
        assert "✓ Model history cleared" in stdout, "History clear confirmation missing"
    except Exception as e:
        assert False, f"History clear test failed: {e}"

    # Verify history is empty
    exit_code, stdout, stderr = run_command([
        "tok", "--history"
    ])
    assert exit_code == 0, f"History check after clear failed: {stderr}"
    assert "Your history is empty" in stdout, "History not cleared properly"


def main():
    """Run all smoke tests."""
    print("=== Tokker Smoke Test Suite ===\n")

    tests = [
        ("Models List", test_models_list),
        ("Tiktoken Model", test_tiktoken_model),
        ("HuggingFace Model", test_huggingface_model),
        ("Output Formats", test_output_formats),
        ("Stdin Input", test_stdin_input),
        ("Model Default", test_model_default),
        ("Error Handling", test_error_handling),
        ("History Functionality", test_history_functionality),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"Running: {name}...")
        try:
            test_func()
            print(f"✓ {name} PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {name} FAILED: {e}")

    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("All smoke tests passed!")
        return 0
    else:
        print("Some smoke tests failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
