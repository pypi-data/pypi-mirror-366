"""Main entry point for deepctl."""

import sys

import click
from deepctl_core import (
    Config,
    TimingContext,
    enable_timing,
    print_timing_summary,
    setup_output,
)
from rich.console import Console
from rich.traceback import install

# Install rich traceback for better error messages
install(show_locals=True)
console = Console()


def preprocess_hyphenated_commands(args: list[str]) -> list[str]:
    """Convert hyphenated commands to nested commands.

    This function looks for commands in the format 'group-subcommand' and
    converts them to the nested format Click expects (e.g., 'group
    subcommand').

    Args:
        args: Command line arguments

    Returns:
        Modified arguments with hyphenated commands converted to nested format
    """
    if not args:
        return args

    # Get all registered commands to know which are groups
    from importlib import metadata

    group_commands = set()

    # Discover group commands from entry points
    try:
        entry_points = metadata.entry_points()
        for entry_point in entry_points.select(group="deepctl.commands"):
            # We'll need to check if it's a group, but for now we'll use a
            # heuristic
            subcommand_group = f"deepctl.subcommands.{entry_point.name}"
            try:
                subcommand_eps = list(
                    entry_points.select(group=subcommand_group)
                )
                if subcommand_eps:
                    group_commands.add(entry_point.name)
            except Exception:
                pass
    except Exception:
        pass

    # Process arguments
    new_args = []
    i = 0

    while i < len(args):
        arg = args[i]

        # Skip if it's an option (starts with -)
        if arg.startswith("-"):
            new_args.append(arg)
            i += 1
            # If it's an option with a value, include the next arg too
            if i < len(args) and not args[i].startswith("-"):
                new_args.append(args[i])
                i += 1
            continue

        # Check if this could be a hyphenated command
        if "-" in arg and not arg.startswith("-"):
            parts = arg.split("-", 1)
            if len(parts) == 2:
                group_name, subcommand = parts

                # If the first part is a known group command, convert it
                if group_name in group_commands:
                    new_args.extend([group_name, subcommand])
                    i += 1
                    continue

        # Otherwise, keep the argument as-is
        new_args.append(arg)
        i += 1

    return new_args


# Create CLI group
@click.group(name="deepctl")
@click.version_option(version="0.1.0", prog_name="deepctl")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--profile",
    "-p",
    help="Configuration profile to use",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "yaml", "table", "csv"], case_sensitive=False),
    help="Output format",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-essential output",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--timing",
    is_flag=True,
    help="Show performance timing information",
)
@click.option(
    "--timing-detailed",
    is_flag=True,
    help="Show detailed performance timing information",
)
@click.pass_context
def cli(
    ctx: click.Context,
    config: str | None,
    profile: str | None,
    output: str | None,
    quiet: bool,
    verbose: bool,
    timing: bool,
    timing_detailed: bool,
) -> None:
    """deepctl - Official Deepgram CLI for speech recognition and audio
    intelligence."""

    # Enable timing if requested
    if timing or timing_detailed:
        enable_timing()

    with TimingContext("cli_initialization"):
        # Initialize configuration
        ctx.ensure_object(dict)
        ctx.obj["config"] = Config(config_path=config, profile=profile)
        ctx.obj["timing"] = timing or timing_detailed
        ctx.obj["timing_detailed"] = timing_detailed

        # Setup output formatting
        setup_output(
            format_type=output
            or ctx.obj["config"].get("output.format", "json"),
            quiet=quiet,
            verbose=verbose,
        )


# Load commands from entry points
def load_commands() -> None:
    """Load commands from package entry points."""
    # Use the plugin manager to load all commands
    from deepctl_core import PluginManager

    with TimingContext("plugin_loading"):
        plugin_manager = PluginManager()
        plugin_manager.load_plugins(cli)


# Load commands when module is imported
load_commands()


def main() -> None:
    """Main entry point for the CLI."""
    try:
        # Check if timing was requested and enable it early
        args = sys.argv[1:]  # Skip the program name
        timing_requested = "--timing" in args or "--timing-detailed" in args
        detailed_timing = "--timing-detailed" in args

        if timing_requested:
            enable_timing()

        with TimingContext("total_execution"):
            with TimingContext("argument_preprocessing"):
                # Preprocess arguments to handle hyphenated commands
                processed_args = preprocess_hyphenated_commands(args)

            with TimingContext("cli_execution"):
                # Call CLI with processed arguments
                try:
                    cli(args=processed_args, standalone_mode=False)
                except SystemExit:
                    # Click calls sys.exit() even in non-standalone mode sometimes
                    pass

        # Print timing summary if timing was enabled
        if timing_requested:
            print_timing_summary(detailed_timing)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


if __name__ == "__main__":
    main()
