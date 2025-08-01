#!/usr/bin/env python3
"""
Debug test of the autonomous agent with MariaDB TPC-H benchmark data.
"""

import asyncio
import json
import os

from dotenv import load_dotenv

# Import the agent
from result_parser_agent import DEFAULT_CONFIG, ResultsParserAgent


async def test_mariadb_tpch_debug():
    """Test the autonomous agent with MariaDB TPC-H benchmark data in debug mode."""

    load_dotenv()

    print("🔍 MariaDB TPC-H Debug Test - Autonomous Agent with Database Benchmark")
    print("=" * 80)

    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set. Please set it first:")
        print("   export GOOGLE_API_KEY='your-google-api-key-here'")
        return

    # TPC-H specific metrics
    test_metrics = ["Power@Size", "Throughput@Size", "QphH@Size"]

    print(f"📊 Target metrics: {test_metrics}")
    print("📁 Input directory: test_mariadb_tpch/")
    print(
        "📂 Structure: run1/iteration1/, run1/iteration2/, run2/iteration1/, run2/iteration2/"
    )
    print("🗄️  Database: MariaDB 10.11.5")
    print("📈 Benchmark: TPC-H")
    print("🔍 DEBUG MODE: ENABLED")
    print()

    try:
        # Create config with debug enabled
        config = DEFAULT_CONFIG.model_copy(deep=True)
        config.agent.debug = True  # Enable debug mode

        # Create agent with debug config
        agent = ResultsParserAgent(config)
        print("✅ Agent created successfully with debug mode enabled")

        # Let the agent handle everything autonomously
        print("🔄 Starting autonomous parsing of MariaDB TPC-H benchmark data...")
        print("   (Debug mode will show intermediate steps and tool executions)")
        print()

        result_update = await agent.parse_results(
            input_path="test_mariadb_tpch/", metrics=test_metrics
        )

        print("✅ Autonomous parsing completed!")
        print()

        # Display results
        print("📋 Extracted Results:")
        print("-" * 50)

        result_json = result_update.model_dump()
        print(json.dumps(result_json, indent=2))

        # Save to JSON file
        output_file = "mariadb_tpch_debug_results.json"
        with open(output_file, "w") as f:
            json.dump(result_json, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        # Show summary
        print()
        print("📈 Summary:")
        print("-" * 50)
        if result_update.resultInfo:
            for result_info in result_update.resultInfo:
                print(f"System: {result_info.sutName}")
                print(f"Platform: {result_info.platformProfilerID}")
                print(f"Runs: {len(result_info.runs)}")

                for run in result_info.runs:
                    print(f"  Run {run.runIndex}:")
                    print(f"    Iterations: {len(run.iterations)}")

                    for iteration in run.iterations:
                        print(f"      Iteration {iteration.iterationIndex}:")
                        print(f"        Instances: {len(iteration.instances)}")

                        for instance in iteration.instances:
                            print(f"          Instance {instance.instanceIndex}:")
                            for stat in instance.statistics:
                                print(
                                    f"            {stat.metricName}: {stat.metricValue}"
                                )
        else:
            print("❌ No results found")

        print("\n🔍 Debug Analysis:")
        print("-" * 50)
        print("The debug logs above should show:")
        print("  - Tool executions (scan_input, execute_command, etc.)")
        print("  - Terminal command outputs")
        print("  - Agent reasoning and decisions")
        print("  - Message exchanges between agent and LLM")
        print("  - Any errors or issues during execution")

        print("\n💡 Debug mode helped identify the extraction process!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mariadb_tpch_debug())
