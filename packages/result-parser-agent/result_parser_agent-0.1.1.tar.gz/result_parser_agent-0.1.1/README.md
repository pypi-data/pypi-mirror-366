# 🎯 Results Parser Agent

A powerful, intelligent agent for extracting metrics from raw result files using LangGraph and AI-powered parsing. The agent automatically analyzes unstructured result files and extracts specific metrics into structured JSON output with high accuracy.

## 🚀 Features

- **🤖 AI-Powered Parsing**: Uses advanced LLMs (Google Gemini, OpenAI, Anthropic, Groq, Ollama) for intelligent metric extraction
- **📁 Flexible Input**: Process single files or entire directories of result files
- **🎯 Pattern Recognition**: Automatically detects and adapts to different file formats and structures
- **⚙️ Rich Configuration**: YAML/JSON configuration with environment variable support
- **📊 Structured Output**: Direct output in Pydantic schemas for easy integration
- **🛠️ Professional CLI**: Feature-rich command-line interface with comprehensive options
- **🔧 Python API**: Easy integration into existing Python applications
- **🔄 Error Recovery**: Robust error handling and retry mechanisms

## 📦 Installation

### Quick Install (Recommended)

```bash
pip install result-parser-agent
```

### Development Install

```bash
# Clone the repository
git clone https://github.com/yourusername/result-parser-agent.git
cd result-parser-agent

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv pip install -e .

# Or install with pip
pip install -e .
```

## 🎯 Quick Start

### 1. Set up your API key

```bash
# For Google Gemini (default)
export GOOGLE_API_KEY="your-google-api-key-here"

# For OpenAI
export OPENAI_API_KEY="your-openai-api-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# For Groq
export GROQ_API_KEY="your-groq-api-key-here"
```

### 2. Use the CLI

```bash
# Parse a directory of result files
result-parser --dir ./benchmark_results --metrics "RPS,latency,throughput" --output results.json

# Parse a single file
result-parser --file ./specific_result.txt --metrics "accuracy,precision"

# Verbose output with debug info
result-parser --dir ./results --metrics "RPS" --verbose

# Custom output file
result-parser --file ./results.txt --metrics "throughput,latency" --output my_results.json
```

### 3. Use the Python API

```python
from result_parser_agent import ResultsParserAgent, DEFAULT_CONFIG
import os

# Set your API key
os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"

# Initialize agent
agent = ResultsParserAgent(DEFAULT_CONFIG)

# Parse results (file or directory)
result_update = await agent.parse_results(
    input_path="./benchmark_results",  # or "./results.txt"
    metrics=["RPS", "latency", "throughput"]
)

# Output structured data
print(result_update.json(indent=2))
```

## 📋 Configuration

### Configuration File Example

```yaml
# config.yaml
agent:
  # LLM configuration
  llm:
    provider: "google"                  # google, openai, anthropic, groq, ollama
    model: "gemini-2.0-flash"          # Model to use
    api_key: null                       # Set to null to use environment variable
    temperature: 0.1                    # Temperature for LLM responses
    max_tokens: 4000                    # Maximum tokens for responses
  
  # Agent behavior
  max_retries: 3
  chunk_size: 2000
  timeout: 300

parsing:
  # Metrics to extract from result files
  metrics:
    - "RPS"
    - "latency"
    - "throughput"
    - "accuracy"
    - "precision"
    - "recall"
    - "f1_score"
  
  # Parsing options
  case_sensitive: false
  fuzzy_match: true
  min_confidence: 0.7

output:
  format: "json"
  pretty_print: true
  include_metadata: true

logging:
  level: "INFO"
  format: "{time} | {level} | {message}"
  file: null
```

### Environment Variables

You can also configure the agent using environment variables:

```bash
# API Keys
export GOOGLE_API_KEY="your-google-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
export GROQ_API_KEY="your-groq-api-key-here"

# Configuration
export PARSER_AGENT__LLM__PROVIDER="google"
export PARSER_AGENT__LLM__MODEL="gemini-2.0-flash"
export PARSER_PARSING__METRICS='["RPS", "latency", "throughput"]'
export PARSER_OUTPUT__FORMAT="json"
```

## 🛠️ CLI Reference

### Command Options

```bash
result-parser [OPTIONS]

Options:
  -d, --dir TEXT              Directory containing result files to parse (use --dir OR --file)
  -f, --file TEXT             Single result file to parse (use --dir OR --file)
  -m, --metrics TEXT          Comma-separated list of metrics to extract (required, e.g., 'RPS,latency,throughput')
  -o, --output PATH           Output JSON file path (default: results.json)
  -v, --verbose               Enable verbose logging
  --log-level TEXT            Logging level [default: INFO]
  --pretty-print              Pretty print JSON output [default: True]
  --no-pretty-print           Disable pretty printing
  --help                      Show this message and exit
```

### Usage Examples

```bash
# Parse all files in a directory
result-parser --dir ./benchmark_results --metrics "RPS,latency" --output results.json

# Parse a single file
result-parser --file ./specific_result.txt --metrics "accuracy,precision"

# Verbose output for debugging
result-parser --dir ./results --metrics "RPS" --verbose

# Custom output file
result-parser --file ./results.txt --metrics "throughput,latency" --output my_results.json

# Compact JSON output
result-parser --dir ./results --metrics "accuracy" --no-pretty-print
```