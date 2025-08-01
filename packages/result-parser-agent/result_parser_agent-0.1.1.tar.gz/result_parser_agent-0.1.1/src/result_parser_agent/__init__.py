"""Results Parser Agent - A deep agent for extracting metrics from result files."""

from .agent.parser_agent import ResultsParserAgent
from .config.settings import DEFAULT_CONFIG, ParserConfig
from .models.schema import (
    Instance,
    Iteration,
    ResultsInfo,
    ResultUpdate,
    Run,
    Statistics,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "ResultsParserAgent",
    "ParserConfig",
    "DEFAULT_CONFIG",
    "ResultUpdate",
    "ResultsInfo",
    "Run",
    "Iteration",
    "Instance",
    "Statistics",
]
