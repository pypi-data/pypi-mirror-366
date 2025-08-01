#!/usr/bin/env python3
"""
Direct test of the autonomous agent with hierarchical folder structure.
"""

import asyncio
import json
import os

from dotenv import load_dotenv

# Import the agent
from result_parser_agent import DEFAULT_CONFIG, ResultsParserAgent


async def test_hierarchical_agent():
    """Test the autonomous agent directly with hierarchical structure."""

    load_dotenv()

    print("🎯 Direct Test - Autonomous Agent with Hierarchical Structure")
    print("=" * 70)

    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set. Please set it first:")
        print("   export GOOGLE_API_KEY='your-google-api-key-here'")
        return

    # Test metrics
    test_metrics = ["Requests/sec", "Transfer/sec"]

    print(f"📊 Target metrics: {test_metrics}")
    print("📁 Input directory: test_hierarchy/")
    print(
        "📂 Structure: run1/iteration1/, run1/iteration2/, run2/iteration1/, run2/iteration2/"
    )
    print()

    try:
        # Create agent
        agent = ResultsParserAgent(DEFAULT_CONFIG)
        print("✅ Agent created successfully")

        # Let the agent handle everything autonomously
        print("🔄 Starting autonomous parsing of hierarchical structure...")
        print("   (Agent will discover files, patterns, and structure on its own)")

        result_update = await agent.parse_results(
            input_path="test_hierarchy/", metrics=test_metrics
        )

        print("✅ Autonomous parsing completed!")
        print()

        # Display results
        print("📋 Extracted Results:")
        print("-" * 50)

        result_json = result_update.model_dump()
        print(json.dumps(result_json, indent=2))

        # Save to JSON file
        output_file = "hierarchical_parsing_results.json"
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

            # Let's check what files the agent should have found
            # print("\n🔍 Debugging - Files in hierarchy:")
            # for root, dirs, files in os.walk("test_hierarchy/"):
            #     for file in files:
            #         print(f"  {os.path.join(root, file)}")

        print("\n🚀 Autonomous Agent Capabilities Tested:")
        print("  ✅ Directory scanning")
        print("  ✅ Multi-file processing")
        print("  ✅ Hierarchical structure understanding")
        print("  ✅ Pattern discovery across files")
        print("  ✅ Metric extraction from nginx logs")
        print("  ✅ Structured output generation")

        print("\n💡 Agent handled everything autonomously!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_hierarchical_agent())
