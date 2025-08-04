#!/usr/bin/env python3
"""Main CLI entry point for the gflake tool."""

from os import cpu_count
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.tree import Tree

from .gflake_runner import GflakeRunner
from .menu_system import MenuSystem
from .test_discovery import GTestCase, GTestDiscovery

app = typer.Typer(
    name="gFlake",
    help="A CLI tool for deflaking gtest test cases with interactive menus and progress tracking.",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    binary_path: str = typer.Argument(
        ...,
        help="Path to the gtest binary to run tests from",
    ),
    test_name: Optional[str] = typer.Option(
        None,
        "--test-name",
        "-t",
        help="Full test name (e.g., 'SuiteName.TestCase') to run directly without menu",
    ),
    duration: float = typer.Option(
        5.0,
        "--duration",
        "-d",
        help="Duration to run tests in seconds",
    ),
    processes: int = typer.Option(
        cpu_count() // 2,
        "--processes",
        "-p",
        help="Number of parallel processes (default: half of CPU cores)",
    ),
):
    """Run the gFlake tool.

    This will discover tests from the binary. If a test name is provided, it will run
    that test directly. Otherwise, it will show interactive menus for test selection.
    All sessions include progress bars and detailed statistics.
    """
    try:
        # Validate binary path
        binary_path = Path(binary_path).resolve()
        if not binary_path.exists():
            console.print(
                f"❌ [bold red]Error:[/bold red] Binary not found: {binary_path}",
            )
            raise typer.Exit(1)

        if not binary_path.is_file():
            console.print(
                f"❌ [bold red]Error:[/bold red] Path is not a file: {binary_path}",
            )
            raise typer.Exit(1)

        console.print("[bold blue]gFlake Tool[/bold blue]")
        console.print(f"   Binary: [cyan]{binary_path}[/cyan]")
        console.print(f"   Target Duration: [yellow]{duration} seconds[/yellow]")
        console.print(f"   Processes: [green]{processes}[/green]")
        console.print()

        # Discover tests
        console.print("[bold]Discovering tests...[/bold]")
        discovery = GTestDiscovery(binary_path)
        suites = discovery.discover_tests()

        if not suites:
            console.print("❌ [bold red]No test suites found![/bold red]")
            console.print("   Make sure the binary supports --gtest_list_tests")
            raise typer.Exit(1)

        gflake_runner = GflakeRunner(binary_path, num_processes=processes)

        if test_name:
            selected_test = _find_test_by_name(test_name, suites)
            if selected_test is None:
                console.print(f"❌ [bold red]Test not found:[/bold red] {test_name}")
                console.print(f"   Use 'gflake discover {binary_path}' to see available tests")
                raise typer.Exit(1)
            console.print(f"[bold green]Running test:[/bold green] {selected_test.full_name}")
        else:
            menu_system = MenuSystem(binary_path, suites)
            selected_test = menu_system.select_test_case()

            if selected_test is None:
                console.print("👋 [yellow]Goodbye![/yellow]")
                raise typer.Exit(0)

        console.print()
        stats = gflake_runner.run_gflake_session(
            test_case=selected_test,
            duration_minutes=duration / 60.0,  # Convert seconds to minutes
        )

        # Exit with appropriate code based on flaky behavior detection
        if stats.failed_runs > 0:
            console.print("\n[bold red]Flaky behavior detected![/bold red]")
            raise typer.Exit(1)
        else:
            console.print("\n[bold green]No flaky behavior detected.[/bold green]")
            raise typer.Exit(0)

    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Interrupted by user. Goodbye![/yellow]")
        raise typer.Exit(1)
    except typer.Exit:
        # Propagate exit exceptions
        raise
    except Exception as e:
        console.print(f"\n❌ [bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def discover(
    binary_path: str = typer.Argument(
        ...,
        help="Path to the gtest binary to discover tests from",
    ),
):
    """Discover and list all available tests from a gtest binary."""
    try:
        # Validate binary path
        binary_path = Path(binary_path).resolve()
        if not binary_path.exists():
            console.print(
                f"❌ [bold red]Error:[/bold red] Binary not found: {binary_path}",
            )
            raise typer.Exit(1)

        console.print("[bold blue]Test Discovery[/bold blue]")
        console.print(f"   Binary: [cyan]{binary_path}[/cyan]")
        console.print()

        # Discover tests
        discovery = GTestDiscovery(binary_path)
        suites = discovery.discover_tests()

        if not suites:
            console.print("❌ [bold red]No test suites found![/bold red]")
            raise typer.Exit(1)

        # Display discovered tests
        _display_discovered_tests(suites)

        # Show summary
        total_tests = sum(len(suite.cases) for suite in suites.values())
        console.print("\n[bold]Discovery Summary:[/bold]")
        console.print(f"   Test Suites: [cyan]{len(suites)}[/cyan]")
        console.print(f"   Total Tests: [green]{total_tests}[/green]")

    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def _find_test_by_name(test_name: str, suites) -> Optional[GTestCase]:
    """Find a test case by its full name (SuiteName.TestName).

    Args:
        test_name: Full test name in format "SuiteName.TestName"
        suites: Dictionary of test suites from discovery

    Returns:
        GTestCase if found, None otherwise
    """
    for suite in suites.values():
        for case in suite.cases:
            if case.full_name == test_name:
                return case
    return None


def _display_discovered_tests(suites):
    """Display the discovered test suites and cases in a tree format."""

    # Create the main tree
    tree = Tree("[bold blue]Discovered Tests[/bold blue]")

    for suite_name, suite in suites.items():
        # Add suite as a branch
        suite_branch = tree.add(
            f"📁 [cyan]{suite_name}[/cyan] ({len(suite.cases)} tests)",
        )

        # Add each test case
        for case in suite.cases:
            test_name = case.name
            test_info = []

            if case.is_parameterized:
                test_info.append("[dim]parameterized[/dim]")
            if case.is_typed:
                test_info.append("[dim]typed[/dim]")

            if test_info:
                test_display = f"🧩 {test_name} ({', '.join(test_info)})"
            else:
                test_display = f"🧩 {test_name}"

            suite_branch.add(test_display)

    console.print(tree)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
