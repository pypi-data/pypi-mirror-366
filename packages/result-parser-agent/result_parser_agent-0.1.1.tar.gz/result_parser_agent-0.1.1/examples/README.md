# Examples

This directory contains examples demonstrating how to use the Results Parser Agent.

## Available Examples

### `test_hierarchical_agent.py`
Demonstrates the autonomous agent parsing hierarchical folder structures with multiple runs, iterations, and instances. This is the main example showing the agent's capabilities.

### `test_final_parsing.py`
Shows how to use the agent for parsing individual result files and extracting specific metrics.

## Configuration

### `configs/parser_config.yaml`
Example configuration file showing how to configure the agent with different LLM providers and parsing settings.

## Sample Data

### `sample_results/`
Contains sample result files for testing the agent.

## Usage

```bash
# Test hierarchical parsing
uv run examples/test_hierarchical_agent.py

# Test single file parsing
uv run examples/test_final_parsing.py
```

Make sure to set your `GOOGLE_API_KEY` environment variable before running the examples. 