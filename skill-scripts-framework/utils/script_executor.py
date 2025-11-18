#!/usr/bin/env python3
"""
Script Executor Utility

Helper utility for executing scripts from Claude Code skills with proper
error handling, output parsing, and logging.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


class ScriptExecutor:
    """Executes skill scripts and handles their output."""

    def __init__(self, skill_root: Path):
        """
        Initialize the executor.

        Args:
            skill_root: Root directory of the skill
        """
        self.skill_root = Path(skill_root)
        self.scripts_dir = self.skill_root / "scripts"

    def execute_python(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300
    ) -> Tuple[int, str, str]:
        """
        Execute a Python script.

        Args:
            script_path: Path to script relative to scripts/ directory
            args: Command line arguments
            env: Environment variables
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        full_path = self.scripts_dir / script_path
        if not full_path.exists():
            raise FileNotFoundError(f"Script not found: {full_path}")

        cmd = ["python3", str(full_path)]
        if args:
            cmd.extend(args)

        return self._run_command(cmd, env, timeout)

    def execute_bash(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300
    ) -> Tuple[int, str, str]:
        """
        Execute a Bash script.

        Args:
            script_path: Path to script relative to scripts/ directory
            args: Command line arguments
            env: Environment variables
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        full_path = self.scripts_dir / script_path
        if not full_path.exists():
            raise FileNotFoundError(f"Script not found: {full_path}")

        cmd = ["bash", str(full_path)]
        if args:
            cmd.extend(args)

        return self._run_command(cmd, env, timeout)

    def execute_and_parse_json(
        self,
        script_type: str,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute script and parse JSON output.

        Args:
            script_type: "python" or "bash"
            script_path: Path to script relative to scripts/ directory
            args: Command line arguments
            env: Environment variables
            timeout: Execution timeout in seconds

        Returns:
            Parsed JSON output

        Raises:
            json.JSONDecodeError: If output is not valid JSON
            RuntimeError: If script exits with non-zero code
        """
        if script_type == "python":
            exit_code, stdout, stderr = self.execute_python(script_path, args, env, timeout)
        elif script_type == "bash":
            exit_code, stdout, stderr = self.execute_bash(script_path, args, env, timeout)
        else:
            raise ValueError(f"Unknown script type: {script_type}")

        if exit_code != 0:
            # Try to parse error from stderr
            try:
                error_data = json.loads(stderr)
                raise RuntimeError(f"Script failed: {error_data.get('message', stderr)}")
            except json.JSONDecodeError:
                raise RuntimeError(f"Script failed with exit code {exit_code}: {stderr}")

        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Script output is not valid JSON: {e.msg}",
                stdout,
                e.pos
            )

    def _run_command(
        self,
        cmd: List[str],
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300
    ) -> Tuple[int, str, str]:
        """
        Run a command and capture output.

        Args:
            cmd: Command and arguments
            env: Environment variables
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=self.skill_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 124, "", f"Script execution timed out after {timeout} seconds"
        except Exception as e:
            return 1, "", str(e)


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Execute skill scripts")
    parser.add_argument("skill_root", help="Root directory of the skill")
    parser.add_argument("script_type", choices=["python", "bash"], help="Script type")
    parser.add_argument("script_path", help="Path to script relative to scripts/")
    parser.add_argument("args", nargs="*", help="Script arguments")
    parser.add_argument("--json", action="store_true", help="Parse output as JSON")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")

    args = parser.parse_args()

    executor = ScriptExecutor(args.skill_root)

    try:
        if args.json:
            result = executor.execute_and_parse_json(
                args.script_type,
                args.script_path,
                args.args,
                timeout=args.timeout
            )
            print(json.dumps(result, indent=2))
        else:
            if args.script_type == "python":
                exit_code, stdout, stderr = executor.execute_python(
                    args.script_path,
                    args.args,
                    timeout=args.timeout
                )
            else:
                exit_code, stdout, stderr = executor.execute_bash(
                    args.script_path,
                    args.args,
                    timeout=args.timeout
                )

            print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(exit_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
