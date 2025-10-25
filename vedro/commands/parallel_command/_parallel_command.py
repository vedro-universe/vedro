import asyncio
import json
import os
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type

from vedro import Config

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("ParallelCommand",)


class ParallelCommand(Command):
    """
    Implements parallel test execution across multiple worker processes.

    This command orchestrates parallel test execution by:
    - Creating multiple worker processes
    - Distributing scenarios using the --slice argument
    - Collecting and aggregating JSON output from workers
    - Displaying rich output in real-time
    - Generating final aggregated report
    """

    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser) -> None:
        """
        Initialize the ParallelCommand.

        :param config: The Vedro configuration class.
        :param arg_parser: Command-line argument parser.
        """
        super().__init__(config, arg_parser)
        self._scenario_results: List[Dict[str, Any]] = []
        self._final_report: Dict[str, Any] = {}

    async def run(self) -> None:
        """
        Execute the 'parallel' command lifecycle.

        Performs the following steps:
        1. Parses command-line arguments (including --workers)
        2. Discovers the number of scenarios
        3. Adjusts worker count if needed (can't exceed scenario count)
        4. Creates worker processes with --slice arguments
        5. Collects JSON output from each worker
        6. Displays rich_output in real-time
        7. Aggregates final report and sets exit code
        """
        # Display experimental feature warning
        print("⚠️ Warning: 'vedro parallel' is an experimental feature", file=sys.stderr)

        args, unknown_args = await self._parse_args()

        # Validate workers count
        if args.workers < 1:
            print("Error: --workers must be at least 1", file=sys.stderr)
            sys.exit(1)

        # Validate that user didn't pass slice-related arguments
        # These are managed by the parallel command itself
        forbidden_args = ["--slice", "--slicer-index", "--slicer-total"]
        for arg in unknown_args:
            # Check for exact match (e.g., --slice)
            if arg in forbidden_args:
                print(f"Error: '{arg}' cannot be used with 'vedro parallel'", file=sys.stderr)
                print(f"       The parallel command manages scenario distribution automatically",
                      file=sys.stderr)
                sys.exit(1)
            # Check for = syntax (e.g., --slice=1/2)
            for forbidden in forbidden_args:
                if arg.startswith(f"{forbidden}="):
                    print(f"Error: '{forbidden}' cannot be used with 'vedro parallel'", file=sys.stderr)
                    print(f"       The parallel command manages scenario distribution automatically",
                          file=sys.stderr)
                    sys.exit(1)

        # Build original arguments (all unknown args + forced reporters)
        original_args = self._build_original_args(unknown_args)

        # Discover how many scenarios exist
        scenario_count = await self._discover_scenario_count(original_args)

        # Adjust worker count if it exceeds scenario count
        actual_workers = min(args.workers, scenario_count) if scenario_count > 0 else args.workers

        if actual_workers < args.workers and scenario_count > 0:
            print(f"Note: Reducing workers from {args.workers} to {actual_workers} "
                  f"(only {scenario_count} scenario(s) to run)", file=sys.stderr)

        # Create and run worker processes
        workers = []
        for worker_index in range(1, actual_workers + 1):
            worker = self._create_worker_task(worker_index, actual_workers, original_args)
            workers.append(worker)

        # Run all workers concurrently and collect outputs
        try:
            await asyncio.gather(*workers)
        except KeyboardInterrupt:
            print("\nInterrupted by user", file=sys.stderr)
            sys.exit(130)

        # Display final summary if we have a report
        if self._final_report:
            self._display_final_summary()

        # Set exit code based on test results
        if self._final_report.get("failed", 0) > 0:
            sys.exit(1)
        elif self._final_report.get("interrupted"):
            sys.exit(130)

    async def _parse_args(self) -> Tuple[Namespace, List[str]]:
        """
        Parse command-line arguments for parallel execution.

        Uses parse_known_args to capture --workers while preserving
        all other arguments to forward to worker processes.

        :return: Tuple of (parsed args, unknown args to forward).
        """
        # Get CPU count, default to 2 if unavailable
        cpu_count = os.cpu_count() or 2

        self._arg_parser.add_argument(
            "--workers", "-w",
            type=int,
            default=cpu_count,
            help=f"Number of parallel workers (default: {cpu_count} - number of CPUs)"
        )

        # Use parse_known_args to capture --workers and preserve everything else
        args, unknown_args = self._arg_parser.parse_known_args()
        return args, unknown_args

    def _build_original_args(self, unknown_args: List[str]) -> List[str]:
        """
        Build the list of original arguments to forward to workers.

        Takes all unknown arguments and adds forced JSON reporters.

        :param unknown_args: All arguments not recognized by parallel command parser.
        :return: List of arguments to pass to worker processes.
        """
        # Start with all unknown arguments (everything except --workers/-w)
        original_args = unknown_args.copy()

        # Force JSON reporters for workers (required for output parsing)
        # Workers must use json and json-rich reporters
        original_args.extend(["-r", "json", "json-rich"])

        return original_args

    async def _discover_scenario_count(self, original_args: List[str]) -> int:
        """
        Discover the number of scenarios that will be run.

        Runs vedro with --dry-run to count scenarios without executing them.

        :param original_args: Arguments to pass to vedro run.
        :return: Number of scenarios that will be scheduled.
        """
        # Build command for dry run discovery
        cmd = [
            sys.executable, "-m", "vedro", "run",
            *original_args,
            "--dry-run"
        ]

        # Run the discovery process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL  # Suppress stderr during discovery
        )

        scenario_count = 0

        # Parse JSON output to count scenarios
        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                try:
                    event = json.loads(line.decode().strip())
                    if event.get("event") == "startup":
                        # The startup event contains the total scenario count
                        scenarios = event.get("scenarios", {})
                        scenario_count = scenarios.get("scheduled", 0)
                        break  # We have the count, no need to continue
                except json.JSONDecodeError:
                    continue

        await process.wait()
        return scenario_count

    def _create_worker_task(self, worker_index: int, total_workers: int,
                           original_args: List[str]) -> asyncio.Task:
        """
        Create an asyncio task for a worker process.

        :param worker_index: 1-based index of the worker.
        :param total_workers: Total number of workers.
        :param original_args: Arguments to pass to the worker.
        :return: Asyncio task that runs the worker.
        """
        return asyncio.create_task(
            self._run_worker(worker_index, total_workers, original_args)
        )

    async def _run_worker(self, worker_index: int, total_workers: int,
                         original_args: List[str]) -> None:
        """
        Run a single worker process and collect its output.

        :param worker_index: 1-based index of the worker.
        :param total_workers: Total number of workers.
        :param original_args: Arguments to pass to the worker.
        """
        # Build command for worker
        cmd = [
            sys.executable, "-m", "vedro", "run",
            *original_args,
            "--slice", f"{worker_index}/{total_workers}"
        ]

        # Start the worker process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Collect output from worker
        if process.stdout:
            await self._collect_worker_output(worker_index, process.stdout)

        # Wait for process to complete
        await process.wait()

        # Collect stderr if any
        if process.stderr:
            stderr = await process.stderr.read()
            if stderr:
                # Display stderr from worker (errors, warnings)
                print(stderr.decode(), end="", file=sys.stderr)

    async def _collect_worker_output(self, worker_id: int,
                                    stdout: asyncio.StreamReader) -> None:
        """
        Read and process JSON events from worker stdout.

        Extracts rich_output from scenario_reported and cleanup events
        and displays them to the console. Also tracks scenario results
        for final aggregation.

        :param worker_id: ID of the worker process.
        :param stdout: Stream reader for worker's stdout.
        """
        while True:
            line = await stdout.readline()
            if not line:
                break

            try:
                event = json.loads(line.decode().strip())
                await self._process_event(event)
            except json.JSONDecodeError:
                # Non-JSON output (shouldn't happen with JSON reporter)
                # Display it anyway in case of errors
                print(line.decode(), end="")

    async def _process_event(self, event: Dict[str, Any]) -> None:
        """
        Process a JSON event from a worker.

        Handles different event types:
        - scenario_reported: Extract rich_output and track results
        - cleanup: Extract final report and rich_output

        :param event: JSON event dictionary from worker.
        """
        event_type = event.get("event")

        if event_type == "scenario_reported":
            # Track scenario result for aggregation
            self._scenario_results.append(event)

            # Display rich_output if available
            rich_output = event.get("rich_output", "")
            if rich_output:
                print(rich_output, end="")

        elif event_type == "cleanup":
            # Aggregate final report
            self._aggregate_report(event.get("report", {}))

            # Display final rich_output from this worker
            rich_output = event.get("rich_output", "")
            if rich_output:
                print(rich_output, end="")

    def _aggregate_report(self, report: Dict[str, Any]) -> None:
        """
        Aggregate report data from a worker into the final report.

        Combines statistics from multiple workers into a single
        aggregated report.

        :param report: Report dictionary from a worker's cleanup event.
        """
        if not self._final_report:
            # Initialize final report with first worker's data
            self._final_report = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "elapsed": 0,
                "interrupted": None
            }

        # Aggregate statistics
        self._final_report["total"] += report.get("total", 0)
        self._final_report["passed"] += report.get("passed", 0)
        self._final_report["failed"] += report.get("failed", 0)
        self._final_report["skipped"] += report.get("skipped", 0)
        self._final_report["elapsed"] = max(
            self._final_report["elapsed"],
            report.get("elapsed", 0)
        )

        # Track interruption status
        if report.get("interrupted"):
            self._final_report["interrupted"] = report["interrupted"]

    def _display_final_summary(self) -> None:
        """
        Display the final aggregated test summary.

        Shows overall statistics from all workers combined.
        """
        report = self._final_report

        # Display summary line
        print()
        print("=" * 70)
        print("PARALLEL EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Total scenarios: {report['total']}")
        print(f"  Passed: {report['passed']}")
        print(f"  Failed: {report['failed']}")
        print(f"  Skipped: {report['skipped']}")
        print(f"Elapsed time: {report['elapsed']:.2f}s")

        if report.get("interrupted"):
            print(f"Status: INTERRUPTED")
        elif report["failed"] > 0:
            print(f"Status: FAILED")
        else:
            print(f"Status: PASSED")
        print("=" * 70)
