import logging
import time
from django.db import transaction
from django.utils import timezone
from apps.agents.models import Agent, AgentTool, AgentExecution

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing and executing AI agents with tools."""

    @staticmethod
    @transaction.atomic
    def create_agent(organization, name, description, model_config, tools=None, system_prompt=""):
        """Create a new AI agent.

        Args:
            organization: Organization instance
            name: Agent name
            description: Agent description
            model_config: dict with model configuration
                - provider_id: AIProviderConfig ID
                - model_id: model string (e.g., 'gpt-4o')
                - temperature: float (default 0.7)
                - memory_config: dict (optional)
            tools: Optional list of AgentTool IDs or instances
            system_prompt: System prompt for the agent

        Returns:
            Agent instance
        """
        provider_id = model_config.get("provider_id")
        model_id = model_config.get("model_id", "gpt-4o")
        temperature = model_config.get("temperature", 0.7)
        memory_config = model_config.get("memory_config", {})

        agent = Agent.objects.create(
            organization=organization,
            name=name,
            description=description,
            system_prompt=system_prompt,
            provider_id=provider_id,
            model_id=model_id,
            temperature=temperature,
            memory_config=memory_config,
            is_active=True,
        )

        if tools:
            tool_ids = [t.id if isinstance(t, AgentTool) else t for t in tools]
            agent.tools.set(tool_ids)

        logger.info(f"Agent '{name}' created for org {organization.id} with model {model_id}")
        return agent

    @staticmethod
    @transaction.atomic
    def update_agent(agent, **kwargs):
        """Update an agent configuration.

        Args:
            agent: Agent instance
            **kwargs: Fields to update (name, description, system_prompt,
                      model_id, temperature, memory_config, is_active, tools)

        Returns:
            Updated Agent instance
        """
        updatable_fields = [
            "name", "description", "system_prompt", "model_id",
            "temperature", "memory_config", "is_active", "provider_id",
        ]

        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(agent, field, value)

        if "tools" in kwargs:
            tool_ids = [t.id if isinstance(t, AgentTool) else t for t in kwargs["tools"]]
            agent.tools.set(tool_ids)

        agent.save()
        logger.info(f"Agent '{agent.name}' (id={agent.id}) updated")
        return agent

    @staticmethod
    async def execute_agent(agent, organization, user, input_data, **kwargs):
        """Execute an agent with its configured tools.

        The agent will:
        1. Build a conversation from the system prompt and input data
        2. Call the AI model
        3. If the model requests a tool call, execute the tool and loop
        4. Return the final response

        Args:
            agent: Agent instance
            organization: Organization instance
            user: User executing the agent
            input_data: dict or str with the user input
            **kwargs: Additional parameters (max_tool_calls, etc.)

        Returns:
            dict with response, tokens_used, tool_calls made
        """
        max_tool_calls = kwargs.get("max_tool_calls", 5)

        # Create execution record
        execution = AgentExecution.objects.create(
            agent=agent,
            status="running",
            input_data=input_data if isinstance(input_data, dict) else {"input": input_data},
        )

        start_time = time.time()

        try:
            # Build initial messages
            messages = []
            if agent.system_prompt:
                messages.append({"role": "system", "content": agent.system_prompt})

            # Add user input
            if isinstance(input_data, dict):
                user_content = input_data.get("message", input_data.get("input", str(input_data)))
            else:
                user_content = str(input_data)

            messages.append({"role": "user", "content": user_content})

            # Determine provider name
            provider_name = "openai"
            if agent.provider:
                provider_name_map = {1: "openai", 2: "anthropic", 3: "gemini"}
                provider_name = provider_name_map.get(agent.provider.provider_name, "openai")

            tool_calls_made = []
            total_tokens = 0

            for _ in range(max_tool_calls):
                # Call AI
                from apps.ai.services import AIService
                result = await AIService.call_ai(
                    messages=messages,
                    model=agent.model_id,
                    provider_name=provider_name,
                    temperature=agent.temperature,
                    organization=organization,
                    user=user,
                )

                total_tokens += result.get("tokens_input", 0) + result.get("tokens_output", 0)

                # Check if the model wants to call a tool
                # (for OpenAI, tool calls are in the response)
                content = result.get("content", "")

                # Simple tool detection based on content patterns
                # In a real implementation, you'd use the model's function calling feature
                tool_call_info = AgentService._detect_tool_call(content, agent)
                if tool_call_info:
                    tool_name = tool_call_info["tool_name"]
                    tool_args = tool_call_info.get("arguments", {})

                    # Execute the tool
                    tool = AgentTool.objects.filter(code=tool_name).first()
                    if tool:
                        tool_result = await AgentService.execute_tool(
                            agent=agent,
                            tool=tool,
                            context={
                                "execution": execution,
                                "input_data": input_data,
                                "arguments": tool_args,
                                "organization": organization,
                                "user": user,
                            },
                        )
                        tool_calls_made.append({
                            "tool": tool_name,
                            "arguments": tool_args,
                            "result": tool_result,
                        })

                        # Add tool result to conversation
                        messages.append({"role": "assistant", "content": content})
                        messages.append({
                            "role": "user",
                            "content": f"Tool '{tool_name}' returned: {tool_result}",
                        })
                    else:
                        # Unknown tool, just use the response as-is
                        break
                else:
                    # No tool call, we're done
                    break

            duration_ms = int((time.time() - start_time) * 1000)

            # Update execution record
            execution.status = "completed"
            execution.output_data = {
                "content": content,
                "tool_calls": tool_calls_made,
            }
            execution.tokens_used = total_tokens
            execution.duration_ms = duration_ms
            execution.save()

            logger.info(
                f"Agent '{agent.name}' execution {execution.id} completed: "
                f"{total_tokens} tokens, {len(tool_calls_made)} tool calls, "
                f"{duration_ms}ms"
            )

            return {
                "execution_id": execution.id,
                "content": content,
                "tokens_used": total_tokens,
                "tool_calls": tool_calls_made,
                "duration_ms": duration_ms,
            }
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            execution.status = "failed"
            execution.error_message = str(exc)
            execution.duration_ms = duration_ms
            execution.save()
            logger.error(f"Agent '{agent.name}' execution {execution.id} failed: {exc}")
            raise

    @staticmethod
    def _detect_tool_call(content, agent):
        """Detect if the AI response contains a tool call request.

        This is a simplified implementation. In production, use the model's
        native function calling API (e.g., OpenAI's tool_calls).

        Args:
            content: AI response content
            agent: Agent instance (for tool configuration)

        Returns:
            dict with tool_name and arguments, or None
        """
        import json
        import re

        # Look for patterns like: TOOL_CALL: tool_name(arg1=value1, arg2=value2)
        # or JSON tool call blocks
        patterns = [
            r'TOOL_CALL:\s*(\w+)\((.+?)\)',
            r'```json\s*\{.*?"tool"\s*:\s*"(\w+)".*?\}\s*```',
        ]

        tool_codes = set(agent.tools.values_list("code", flat=True)) if agent.tools.exists() else set()

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                tool_name = match.group(1)
                if tool_name in tool_codes:
                    try:
                        args_str = match.group(2) if match.lastindex > 1 else "{}"
                        arguments = json.loads(args_str) if args_str.startswith("{") else {}
                    except (json.JSONDecodeError, IndexError):
                        arguments = {}
                    return {"tool_name": tool_name, "arguments": arguments}

        return None

    @staticmethod
    async def execute_tool(agent, tool, context):
        """Execute a specific tool.

        Args:
            agent: Agent instance
            tool: AgentTool instance
            context: dict with execution context
                - execution: AgentExecution instance
                - input_data: original input
                - arguments: tool arguments
                - organization: Organization instance
                - user: User instance

        Returns:
            Tool execution result (str or dict)
        """
        handler_path = tool.handler_path
        if not handler_path:
            raise ValueError(f"Tool '{tool.code}' has no handler configured")

        import importlib
        module_path, func_name = handler_path.rsplit(".", 1) if "." in handler_path else (handler_path, None)
        if not func_name:
            raise ValueError(f"Invalid handler path: {handler_path}")

        module = importlib.import_module(module_path)
        handler = getattr(module, func_name, None)

        if not handler or not callable(handler):
            raise ValueError(f"Tool handler not found: {handler_path}")

        arguments = context.get("arguments", {})
        tool_input = tool.input_schema or {}

        # Validate required arguments
        required_args = tool_input.get("required", [])
        for arg in required_args:
            if arg not in arguments:
                raise ValueError(f"Tool '{tool.code}' requires argument: {arg}")

        logger.info(f"Executing tool '{tool.code}' for agent '{agent.name}'")

        # Call the handler (supports both sync and async)
        result = handler(
            agent=agent,
            **arguments,
        )

        if hasattr(result, "__await__"):
            result = await result

        return result
