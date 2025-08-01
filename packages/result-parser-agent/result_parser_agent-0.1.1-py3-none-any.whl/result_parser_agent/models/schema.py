"""Pydantic models for structured output schema."""

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    """Statistics model for individual metrics."""

    metricName: str = Field(..., description="Name of the metric")
    metricValue: float | int | str = Field(..., description="Value of the metric")


class Instance(BaseModel):
    """Instance model containing statistics."""

    instanceIndex: str = Field(..., description="Index of the instance")
    statistics: list[Statistics] = Field(
        ..., description="List of statistics for this instance"
    )


class Iteration(BaseModel):
    """Iteration model containing instances."""

    iterationIndex: int = Field(..., description="Index of the iteration")
    instances: list[Instance] = Field(
        ..., description="List of instances for this iteration"
    )


class Run(BaseModel):
    """Run model containing iterations."""

    runIndex: str = Field(..., description="Index of the run")
    runID: str = Field(..., description="ID of the run")
    iterations: list[Iteration] = Field(
        ..., description="List of iterations for this run"
    )


class ResultsInfo(BaseModel):
    """Results info model containing runs."""

    sutName: str = Field(..., description="Name of the system under test")
    platformProfilerID: str = Field(..., description="Platform profiler ID")
    runs: list[Run] = Field(..., description="List of runs")


class ResultUpdate(BaseModel):
    """Result update model containing benchmark execution info."""

    benchmarkExecutionID: str = Field(..., description="Benchmark execution ID")
    resultInfo: list[ResultsInfo] = Field(..., description="List of results info")
