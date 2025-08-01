"""Command-line interface for the Results Parser Agent."""

import asyncio
import json
import sys
from pathlib import Path

import typer
from loguru import logger

from .agent.parser_agent import ResultsParserAgent
from .config.settings import DEFAULT_CONFIG
from .models.schema import ResultUpdate


def setup_logging(verbose: bool, log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    # Remove default handler
    logger.remove()

    # Add console handler
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    if verbose:
        log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)


def validate_input_path(input_path: str) -> Path:
    """Validate and return input path."""
    path = Path(input_path)
    if not path.exists():
        raise typer.BadParameter(f"Input path does not exist: {input_path}")
    return path


def validate_metrics(metrics: list[str]) -> list[str]:
    """Validate metrics list."""
    if not metrics:
        raise typer.BadParameter("At least one metric must be specified")
    return [metric.strip() for metric in metrics]


def save_output(
    result_update: ResultUpdate, output_path: str, pretty_print: bool = True
) -> None:
    """Save results to output file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        if pretty_print:
            json.dump(result_update.model_dump(), f, indent=2)
        else:
            json.dump(result_update.model_dump(), f)

    logger.info(f"Results saved to: {output_file}")


app = typer.Typer(
    name="result-parser",
    help="Results Parser Agent - Extract metrics from raw result files",
    add_completion=False,
)


@app.command()
def main(
    input_dir: str | None = typer.Option(
        None, "--dir", "-d", help="Directory containing result files to parse"
    ),
    input_file: str | None = typer.Option(
        None, "--file", "-f", help="Single result file to parse"
    ),
    metrics: str = typer.Option(
        ...,
        "--metrics",
        "-m",
        help="Comma-separated list of metrics to extract (required, e.g., 'RPS,latency,throughput')",
    ),
    output: str = typer.Option(
        "results.json",
        "--output",
        "-o",
        help="Output JSON file path (default: results.json)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Logging level", case_sensitive=False
    ),
    pretty_print: bool = typer.Option(
        True, "--pretty-print", help="Pretty print JSON output (default: True)"
    ),
    no_pretty_print: bool = typer.Option(
        False, "--no-pretty-print", help="Disable pretty printing"
    ),
) -> None:
    """
    Results Parser Agent - Extract metrics from raw result files.

    This tool intelligently parses result files and extracts specified metrics
    into structured JSON output. It supports various file formats and can handle
    large, unstructured result files.

    Examples:

        # Parse all files in a directory
        result-parser --dir ./benchmark_results --metrics "RPS,latency" --output results.json

        # Parse a single file
        result-parser --file ./specific_result.txt --metrics "accuracy,precision"

        # Verbose output
        result-parser --dir ./results --metrics "RPS" --verbose

        # Custom output file
        result-parser --file ./results.txt --metrics "throughput,latency" --output my_results.json
    """
    try:
        # Setup logging
        setup_logging(verbose, log_level)

        # Validate input - must provide exactly one of --dir or --file
        if not input_dir and not input_file:
            raise typer.BadParameter("Either --dir or --file must be specified")

        if input_dir and input_file:
            raise typer.BadParameter(
                "Cannot specify both --dir and --file. Use either --dir for directory or --file for single file."
            )

        # Validate metrics
        metrics_list = validate_metrics([m.strip() for m in metrics.split(",")])

        # Handle pretty print flag
        if no_pretty_print:
            pretty_print = False

        # Determine input path
        input_path = input_file if input_file else input_dir
        if input_path is None:
            raise typer.BadParameter("Input path cannot be None")
        validate_input_path(input_path)

        # Create config with CLI metrics
        config_obj = DEFAULT_CONFIG
        config_obj.parsing.metrics = metrics_list

        logger.info(
            f"Starting parsing with {len(metrics_list)} metrics: {', '.join(metrics_list)}"
        )
        logger.info(f"Input path: {input_path}")
        logger.info(f"Output file: {output}")

        # Run the agent
        async def run_agent() -> ResultUpdate:
            agent = ResultsParserAgent(config_obj)
            result_update = await agent.parse_results(
                input_path=input_path, metrics=metrics_list
            )
            return result_update

        # Execute async function
        result_update = asyncio.run(run_agent())

        # Save results to file
        save_output(result_update, output, pretty_print)

        logger.info("Parsing completed successfully")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
