"""Autonomous parsing agent for extracting metrics from result files."""

from typing import Annotated, Any, TypedDict

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from loguru import logger

from ..config.settings import ParserConfig
from ..models.schema import ResultUpdate
from ..prompts.agent_prompts import get_initial_message, get_system_prompt
from ..tools.langchain_tools import create_tools


# State definition for LangGraph
class AgentState(TypedDict):
    """State for the parsing agent."""

    messages: Annotated[list[BaseMessage], "The messages in the conversation"]
    remaining_steps: Annotated[int, "Number of remaining steps"]
    todos: Annotated[list[str], "List of tasks to complete"]
    files: Annotated[dict[str, Any], "Discovered files and their info"]
    parsing_progress: Annotated[dict[str, Any], "Progress tracking for each file"]
    extracted_data: Annotated[dict[str, Any], "Extracted metrics data"]
    raw_context: Annotated[dict[str, str], "Filepath to raw context mapping"]
    errors: Annotated[list[str], "List of errors encountered"]
    config: Annotated[Any, "Configuration object"]
    context: Annotated[dict[str, Any], "Context information"]


class ResultsParserAgent:
    """Autonomous deep agent for parsing results and extracting metrics."""

    def __init__(self, config: ParserConfig):
        self.config = config
        self.model = self._create_llm_model()
        self.agent = self._create_agent()

    def _create_llm_model(self) -> LanguageModelLike:
        """Create the appropriate LLM model based on configuration."""
        llm_config = self.config.get_llm_config()

        if llm_config["provider"] == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
            )
        elif llm_config["provider"] == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
            )
        elif llm_config["provider"] == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
            )
        elif llm_config["provider"] == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=llm_config["model"], temperature=float(llm_config["temperature"])
            )
        elif llm_config["provider"] == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
                max_output_tokens=(
                    int(llm_config["max_tokens"]) if llm_config["max_tokens"] else None
                ),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_config['provider']}")

    def _create_agent(self) -> Any:
        """Create the LangGraph agent with standard react agent."""
        # Create tools
        tools = create_tools(None)

        # Use the standard react agent with a simpler approach
        from langgraph.prebuilt import create_react_agent

        agent = create_react_agent(
            self.model,
            tools,
            debug=self.config.agent.debug,  # Enable debug mode if configured
        )
        return agent

    def _get_system_prompt(self) -> str:
        """Get the system prompt with autonomous workflow instructions."""
        return get_system_prompt(self.config.parsing.metrics)

    def _capture_raw_context(self, final_state: dict[str, Any]) -> str:
        """Capture raw context from terminal command outputs in the state."""
        context_parts = []

        # Add messages from the conversation
        if "messages" in final_state:
            context_parts.append("AGENT CONVERSATION:")
            for i, msg in enumerate(final_state["messages"]):
                if hasattr(msg, "content"):
                    # Look for the final agent response that contains extracted data
                    if (
                        i == len(final_state["messages"]) - 1
                        and "```json" in msg.content
                    ):
                        context_parts.append("  FINAL AGENT EXTRACTION:")
                        context_parts.append(f"  {msg.content}")
                    else:
                        context_parts.append(f"  Message {i}: {msg.content[:200]}...")
            context_parts.append("")

        # Add terminal command outputs
        context_parts.append("TERMINAL COMMAND OUTPUTS:")
        if "messages" in final_state:
            for msg in final_state["messages"]:
                if (
                    hasattr(msg, "content")
                    and '"command"' in msg.content
                    and '"stdout"' in msg.content
                ):
                    try:
                        import json

                        tool_output = json.loads(msg.content)
                        if tool_output.get("success") and tool_output.get("stdout"):
                            context_parts.append(f"  Command: {tool_output['command']}")
                            context_parts.append(f"  Output: {tool_output['stdout']}")
                            context_parts.append("")
                    except Exception:
                        pass

        return "\n".join(context_parts) if context_parts else "No data captured"

    async def parse_results(
        self, input_path: str, metrics: list[str] | None = None
    ) -> ResultUpdate:
        """
        Main entry point for parsing results.

        Args:
            input_path: Path to file or directory containing result files
            metrics: Optional list of metrics to extract (if None, uses config metrics)

        Returns:
            Structured ResultUpdate object
        """
        try:
            logger.info(f"Starting autonomous parsing of: {input_path}")

            # Use provided metrics or config metrics
            target_metrics = metrics or self.config.parsing.metrics

            if self.config.agent.debug:
                logger.info(f"🔍 DEBUG MODE ENABLED - Target metrics: {target_metrics}")
                logger.info(f"🔍 DEBUG MODE ENABLED - Input path: {input_path}")

            # Create initial messages for the agent
            initial_messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=get_initial_message(input_path, target_metrics)),
            ]

            if self.config.agent.debug:
                logger.info("🔍 DEBUG MODE - Initial messages created")
                logger.info(
                    f"🔍 DEBUG MODE - System prompt length: {len(initial_messages[0].content)} chars"
                )
                logger.info(
                    f"🔍 DEBUG MODE - Human message length: {len(initial_messages[1].content)} chars"
                )

            # Run the agent to discover and extract metrics
            if self.config.agent.debug:
                logger.info("🔍 DEBUG MODE - Starting agent execution...")

            runnable_config = RunnableConfig(recursion_limit=50)
            result = await self.agent.ainvoke(
                {"messages": initial_messages}, config=runnable_config
            )
            # result = await self.agent.ainvoke({"messages": initial_messages})

            if self.config.agent.debug:
                logger.info("🔍 DEBUG MODE - Agent execution completed")
                logger.info(f"🔍 DEBUG MODE - Result type: {type(result)}")
                if isinstance(result, dict):
                    logger.info(f"🔍 DEBUG MODE - Result keys: {list(result.keys())}")
                    if "messages" in result:
                        logger.info(
                            f"🔍 DEBUG MODE - Number of messages: {len(result['messages'])}"
                        )
                        for i, msg in enumerate(result["messages"]):
                            if hasattr(msg, "content"):
                                logger.info(
                                    f"🔍 DEBUG MODE - Message {i}: {msg.content[:100]}..."
                                )

            # Extract JSON from the agent's final response
            return self._extract_json_from_agent_response(result, target_metrics)

        except Exception as e:
            logger.error(f"Error in parse_results: {str(e)}")
            if self.config.agent.debug:
                import traceback

                logger.error(
                    f"🔍 DEBUG MODE - Full traceback: {traceback.format_exc()}"
                )
            raise

    def _extract_json_from_agent_response(
        self, result: dict[str, Any], target_metrics: list[str]
    ) -> ResultUpdate:
        """Extract JSON from the agent's final response and convert to ResultUpdate."""
        try:
            if "messages" not in result or not result["messages"]:
                raise ValueError("No messages found in agent response")

            # Get the final message from the agent
            final_message = result["messages"][-1]
            if not hasattr(final_message, "content"):
                raise ValueError("Final message has no content")

            content = final_message.content

            # Look for JSON in the content
            import json
            import re

            # Try to find JSON block
            json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in agent response")

            # Parse the JSON
            parsed_data = json.loads(json_str)

            if self.config.agent.debug:
                logger.info(f"🔍 DEBUG MODE - Extracted JSON: {json_str[:200]}...")

            # Convert to ResultUpdate
            return ResultUpdate(**parsed_data)

        except Exception as e:
            logger.error(f"Error extracting JSON from agent response: {str(e)}")
            if self.config.agent.debug:
                logger.error(
                    f"🔍 DEBUG MODE - Agent response content: {content[:500]}..."
                )

            # Fallback to empty result
            return ResultUpdate(benchmarkExecutionID="auto_generated", resultInfo=[])
