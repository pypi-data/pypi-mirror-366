"""Core Agent implementation for Coda."""

import asyncio
import json
from collections.abc import Callable

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from coda.base.providers.base import BaseProvider, Message, Role, Tool, ToolCall
from coda.base.theme import ThemeManager

from .agent_types import (
    PerformedAction,
    PerformedActionType,
    RequiredAction,
    RunResponse,
)
from .function_tool import FunctionTool


class Agent:
    """
    An AI agent that can execute tasks using provided tools and instructions.

    The agent manages the interaction loop with the AI provider, executes tools,
    and handles the conversation flow.
    """

    def __init__(
        self,
        provider: BaseProvider,
        model: str,
        instructions: str = "You are a helpful assistant",
        tools: list[Callable | FunctionTool] | None = None,
        name: str | None = None,
        description: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        console: Console | None = None,
        **kwargs,
    ):
        """
        Initialize an agent.

        Args:
            provider: The AI provider to use
            model: Model identifier
            instructions: System instructions for the agent
            tools: List of tools the agent can use
            name: Optional agent name
            description: Optional agent description
            temperature: Sampling temperature
            max_tokens: Max tokens per response
            console: Rich console for output
            **kwargs: Additional provider-specific parameters
        """
        self.provider = provider
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        self.name = name or "Agent"
        self.description = description
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.console = console or Console()
        self.kwargs = kwargs
        self.theme_manager = ThemeManager()
        self.console_theme = self.theme_manager.get_console_theme()

        # Process tools
        self._function_tools: list[FunctionTool] = self._process_tools()
        self._tool_map: dict[str, FunctionTool] = {tool.name: tool for tool in self._function_tools}

    def _process_tools(self) -> list[FunctionTool]:
        """Convert all tools to FunctionTool format."""
        function_tools = []

        for tool in self.tools:
            if isinstance(tool, FunctionTool):
                function_tools.append(tool)
            elif callable(tool):
                # Must be decorated with @tool
                try:
                    function_tools.append(FunctionTool.from_callable(tool))
                except ValueError:
                    self.console.print(
                        f"[{self.console_theme.warning}]Warning: {tool.__name__} is not decorated with @tool, skipping[/{self.console_theme.warning}]"
                    )

        return function_tools

    def _get_provider_tools(self) -> list[Tool]:
        """Convert FunctionTools to provider Tool format."""
        provider_tools = []

        for func_tool in self._function_tools:
            provider_tool = Tool(
                name=func_tool.name,
                description=func_tool.description,
                parameters=func_tool.parameters,
            )
            provider_tools.append(provider_tool)

        return provider_tools

    async def run_async(
        self,
        input: str,
        messages: list[Message] | None = None,
        max_steps: int = 10,
        on_fulfilled_action: Callable[[RequiredAction, PerformedAction], None] | None = None,
        status=None,  # Optional status indicator
        **kwargs,
    ) -> RunResponse:
        """
        Run the agent asynchronously.

        Args:
            input: User input message
            messages: Optional message history
            max_steps: Maximum tool execution steps
            on_fulfilled_action: Callback for completed actions
            **kwargs: Additional parameters

        Returns:
            RunResponse with final result
        """
        # Initialize messages if not provided
        if messages is None:
            messages = []

        # Always ensure system instructions are at the beginning
        if self.instructions:
            # Check if system message already exists
            has_system_msg = any(msg.role == Role.SYSTEM for msg in messages)
            if not has_system_msg:
                messages.insert(0, Message(role=Role.SYSTEM, content=self.instructions))

        # Add user message
        messages.append(Message(role=Role.USER, content=input))

        # Get provider tools
        provider_tools = self._get_provider_tools()

        # Check if model supports tools
        model_info = next((m for m in self.provider.list_models() if m.id == self.model), None)
        supports_tools = model_info and model_info.supports_functions and provider_tools

        # Main execution loop
        step_count = 0
        final_response = None

        # Loop detection state
        recent_tool_calls = []  # Track recent tool calls for loop detection
        loop_detection_window = 3  # Number of recent calls to check
        max_same_tool_calls = 2  # Max times same tool can be called consecutively

        while step_count < max_steps:
            try:
                # Make request to provider
                if supports_tools:
                    response = await asyncio.to_thread(
                        self.provider.chat,
                        messages=messages,
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        tools=provider_tools,
                        **self.kwargs,
                    )
                else:
                    # Fallback to regular chat
                    response = await asyncio.to_thread(
                        self.provider.chat,
                        messages=messages,
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        **self.kwargs,
                    )

                # Check for tool calls
                if response.tool_calls:
                    # Check for tool call loops before proceeding
                    loop_detected = self._detect_tool_call_loops(
                        response.tool_calls,
                        recent_tool_calls,
                        loop_detection_window,
                        max_same_tool_calls,
                    )

                    if loop_detected:
                        # Break out of loop with a directive to provide final answer
                        self.console.print(
                            f"[{self.console_theme.warning}]⚠️  Loop detected: Same tool called multiple times. Forcing final answer...[/{self.console_theme.warning}]"
                        )

                        # Force a final response by disabling tool support temporarily
                        # and asking for a summary of existing tool results
                        final_prompt = "Based on the tool execution results above, provide a complete final answer to the user's original question. Do not call any more tools."

                        # Get final response without tools
                        try:
                            final_response_obj = await asyncio.to_thread(
                                self.provider.chat,
                                messages=messages + [Message(role=Role.USER, content=final_prompt)],
                                model=self.model,
                                temperature=self.temperature,
                                max_tokens=self.max_tokens,
                                tools=None,  # No tools allowed
                                **self.kwargs,
                            )

                            if final_response_obj.content:
                                self._print_response(final_response_obj.content)
                                final_response = final_response_obj
                                break
                            else:
                                # If still no content, use a fallback
                                self.console.print(
                                    f"[{self.console_theme.error}]Unable to get final response. Providing fallback.[/{self.console_theme.error}]"
                                )
                                final_response = type(
                                    "obj",
                                    (object,),
                                    {
                                        "content": "I have executed the requested tools but encountered an issue providing a final response.",
                                        "model": self.model,
                                    },
                                )
                                break

                        except Exception as e:
                            self.console.print(
                                f"[{self.console_theme.error}]Error getting final response: {e}[/{self.console_theme.error}]"
                            )
                            final_response = type(
                                "obj",
                                (object,),
                                {
                                    "content": "I executed the requested tools but encountered an error providing the final response.",
                                    "model": self.model,
                                },
                            )
                            break

                    # Display response if any
                    if response.content:
                        self._print_response(response.content)
                    # Add assistant message with tool calls
                    messages.append(
                        Message(
                            role=Role.ASSISTANT,
                            content=response.content or "",
                            tool_calls=response.tool_calls,
                        )
                    )

                    # Track tool calls for loop detection
                    for tool_call in response.tool_calls:
                        recent_tool_calls.append(tool_call.name)
                        if len(recent_tool_calls) > loop_detection_window:
                            recent_tool_calls.pop(0)

                    # Handle tool calls
                    performed_actions = await self._handle_tool_calls(
                        response.tool_calls, on_fulfilled_action, status
                    )

                    # Add tool results to messages
                    for action in performed_actions:
                        messages.append(
                            Message(
                                role=Role.TOOL,
                                content=action.function_call_output,
                                tool_call_id=action.action_id,
                            )
                        )

                    step_count += 1
                    # Continue loop to get final response
                    if status:
                        status.update(
                            f"[{self.console_theme.bold} {self.console_theme.info}]Processing response...[/{self.console_theme.bold} {self.console_theme.info}]"
                        )
                else:
                    # No tool calls, we're done
                    if response.content:
                        self._print_response(response.content)
                        messages.append(Message(role=Role.ASSISTANT, content=response.content))
                    final_response = response
                    break

            except Exception as e:
                from ..errors import ErrorHandler, ProviderError

                # Wrap the error appropriately
                if "provider" in str(e).lower() or "api" in str(e).lower():
                    wrapped_error = ProviderError(
                        f"Provider error during execution: {str(e)}",
                        provider_name=self.provider.__class__.__name__,
                    )
                else:
                    wrapped_error = ErrorHandler.wrap_error(e, "agent_execution")

                error_msg = wrapped_error.user_message()
                self.console.print(
                    f"[{self.console_theme.error}]{error_msg}[/{self.console_theme.error}]"
                )

                # Log detailed error for debugging
                if wrapped_error.severity.value in ["error", "critical"]:
                    import logging

                    logging.error(ErrorHandler.format_error_chain(wrapped_error))

                final_response = type("obj", (object,), {"content": error_msg, "model": self.model})
                break

        if step_count >= max_steps:
            self.console.print(
                f"[{self.console_theme.warning}]Reached maximum steps ({max_steps})[/{self.console_theme.warning}]"
            )

        # Return response
        return RunResponse(
            session_id=None,
            data={
                "content": final_response.content if final_response else "",
                "model": self.model,
                "messages": messages,
            },
        )

    async def run_async_streaming(
        self,
        input: str,
        messages: list[Message] | None = None,
        max_steps: int = 10,
        on_fulfilled_action: Callable[[RequiredAction, PerformedAction], None] | None = None,
        status=None,  # Optional status indicator
        interrupt_check: Callable[[], bool] | None = None,  # Optional interrupt check
        **kwargs,
    ) -> tuple[str, list[Message]]:
        """
        Run the agent asynchronously with streaming support.

        Args:
            input: User input message
            messages: Optional message history
            max_steps: Maximum tool execution steps
            on_fulfilled_action: Callback for completed actions
            **kwargs: Additional parameters

        Returns:
            Tuple of (final_response_content, updated_messages)
        """
        # Initialize messages if not provided
        if messages is None:
            messages = []

        # Always ensure system instructions are at the beginning
        if self.instructions:
            # Check if system message already exists
            has_system_msg = any(msg.role == Role.SYSTEM for msg in messages)
            if not has_system_msg:
                messages.insert(0, Message(role=Role.SYSTEM, content=self.instructions))

        # Add user message
        messages.append(Message(role=Role.USER, content=input))

        # Get provider tools
        provider_tools = self._get_provider_tools()

        # Check if model supports tools
        model_info = next((m for m in self.provider.list_models() if m.id == self.model), None)
        supports_tools = model_info and model_info.supports_functions and provider_tools

        # Main execution loop
        step_count = 0
        final_response_content = ""

        # Loop detection state
        recent_tool_calls = []  # Track recent tool calls for loop detection
        loop_detection_window = 3  # Number of recent calls to check
        max_same_tool_calls = 2  # Max times same tool can be called consecutively
        first_chunk = True

        while step_count < max_steps:
            # Check for interrupt
            if interrupt_check and interrupt_check():
                if status:
                    status.stop()
                self.console.print(
                    f"\n[{self.console_theme.warning}]Response interrupted by user[/{self.console_theme.warning}]"
                )
                return "Response interrupted.", messages

            try:
                # Make request to provider
                if supports_tools:
                    response = await asyncio.to_thread(
                        self.provider.chat,
                        messages=messages,
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        tools=provider_tools,
                        **self.kwargs,
                    )
                else:
                    # Use streaming for final response when no tools
                    if status:
                        status.update(
                            f"[{self.console_theme.bold} {self.console_theme.info}]Generating response...[/{self.console_theme.bold} {self.console_theme.info}]"
                        )

                    stream = self.provider.chat_stream(
                        messages=messages,
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        **self.kwargs,
                    )

                    # Stream the response
                    response_content = ""
                    for chunk in stream:
                        # Check for interrupt
                        if interrupt_check and interrupt_check():
                            if status:
                                status.stop()
                            self.console.print(
                                f"\n[{self.console_theme.warning}]Response interrupted by user[/{self.console_theme.warning}]"
                            )
                            return "Response interrupted.", messages

                        if first_chunk:
                            # Stop status before printing response
                            if status:
                                status.stop()
                            self.console.print(
                                f"\n[{self.console_theme.bold} {self.console_theme.assistant_message}]{self.name}:[/{self.console_theme.bold} {self.console_theme.assistant_message}] ",
                                end="",
                            )
                            first_chunk = False

                        self.console.print(chunk.content, end="")
                        response_content += chunk.content

                    if response_content:
                        self.console.print()  # Add newline after streaming
                        messages.append(Message(role=Role.ASSISTANT, content=response_content))

                    return response_content, messages

                # Check for tool calls
                if response.tool_calls:
                    # Check for tool call loops before proceeding
                    loop_detected = self._detect_tool_call_loops(
                        response.tool_calls,
                        recent_tool_calls,
                        loop_detection_window,
                        max_same_tool_calls,
                    )

                    if loop_detected:
                        # Break out of loop with a directive to provide final answer
                        self.console.print(
                            f"[{self.console_theme.warning}]⚠️  Loop detected: Same tool called multiple times. Forcing final answer...[/{self.console_theme.warning}]"
                        )

                        # Force a final response using streaming
                        final_prompt = "Based on the tool execution results above, provide a complete final answer to the user's original question. Do not call any more tools."

                        # Get final response with streaming
                        try:
                            if status:
                                status.update(
                                    f"[{self.console_theme.bold} {self.console_theme.info}]Getting final response...[/{self.console_theme.bold} {self.console_theme.info}]"
                                )

                            stream = self.provider.chat_stream(
                                messages=messages + [Message(role=Role.USER, content=final_prompt)],
                                model=self.model,
                                temperature=self.temperature,
                                max_tokens=self.max_tokens,
                                **self.kwargs,
                            )

                            # Stream the final response
                            response_content = ""
                            for chunk in stream:
                                # Check for interrupt
                                if interrupt_check and interrupt_check():
                                    if status:
                                        status.stop()
                                    self.console.print(
                                        f"\n[{self.console_theme.warning}]Response interrupted by user[/{self.console_theme.warning}]"
                                    )
                                    return "Response interrupted.", messages

                                if first_chunk:
                                    # Stop status before printing response
                                    if status:
                                        status.stop()
                                    self.console.print(
                                        f"\n[{self.console_theme.bold} {self.console_theme.assistant_message}]{self.name}:[/{self.console_theme.bold} {self.console_theme.assistant_message}] ",
                                        end="",
                                    )
                                    first_chunk = False

                                self.console.print(chunk.content, end="")
                                response_content += chunk.content

                            if response_content:
                                self.console.print()  # Add newline after streaming
                                messages.append(
                                    Message(role=Role.ASSISTANT, content=response_content)
                                )
                                return response_content, messages
                            else:
                                # Fallback
                                fallback_content = "I have executed the requested tools but encountered an issue providing a final response."
                                self.console.print(
                                    f"[{self.console_theme.error}]{fallback_content}[/{self.console_theme.error}]"
                                )
                                return fallback_content, messages

                        except Exception as e:
                            error_content = f"I executed the requested tools but encountered an error providing the final response: {e}"
                            self.console.print(
                                f"[{self.console_theme.error}]{error_content}[/{self.console_theme.error}]"
                            )
                            return error_content, messages

                    # Display response if any
                    if response.content and response.content.strip():
                        self._print_response(response.content)
                    # Add assistant message with tool calls
                    messages.append(
                        Message(
                            role=Role.ASSISTANT,
                            content=response.content or "",
                            tool_calls=response.tool_calls,
                        )
                    )

                    # Track tool calls for loop detection
                    for tool_call in response.tool_calls:
                        recent_tool_calls.append(tool_call.name)
                        if len(recent_tool_calls) > loop_detection_window:
                            recent_tool_calls.pop(0)

                    # Handle tool calls
                    performed_actions = await self._handle_tool_calls(
                        response.tool_calls, on_fulfilled_action, status, interrupt_check
                    )

                    # Add tool results to messages
                    for action in performed_actions:
                        messages.append(
                            Message(
                                role=Role.TOOL,
                                content=action.function_call_output,
                                tool_call_id=action.action_id,
                            )
                        )

                    step_count += 1
                    # Continue loop to get final response
                    if status:
                        status.update(
                            f"[{self.console_theme.bold} {self.console_theme.info}]Processing response...[/{self.console_theme.bold} {self.console_theme.info}]"
                        )
                else:
                    # No tool calls, we have the final response
                    if response.content:
                        # Stop status before printing response
                        if status:
                            status.stop()
                        # We already have the full response from the non-streaming call
                        # For better UX, we should stream it character by character
                        self.console.print(
                            f"\n[{self.console_theme.bold} {self.console_theme.assistant_message}]{self.name}:[/{self.console_theme.bold} {self.console_theme.assistant_message}] ",
                            end="",
                        )

                        # Simulate streaming by printing character by character
                        import time

                        for char in response.content:
                            self.console.print(char, end="")
                            time.sleep(0.001)  # Small delay for streaming effect

                        self.console.print()  # Add newline after response
                        messages.append(Message(role=Role.ASSISTANT, content=response.content))
                        return response.content, messages
                    else:
                        # This shouldn't happen, but handle it
                        return "", messages

            except Exception as e:
                # Check if this is an OCI ServiceError
                error_type = type(e).__name__
                if error_type == "ServiceError" and hasattr(e, "message") and hasattr(e, "status"):
                    # Format OCI error nicely
                    self.console.print(
                        Panel(
                            f"[{self.console_theme.bold}]OCI API Error ({e.status})[/{self.console_theme.bold}]\n\n{e.message}",
                            title="Error",
                            border_style="red",
                            padding=(1, 2),
                        )
                    )

                    # Add helpful context for common errors
                    if "finetune base model" in str(e.message).lower():
                        self.console.print(
                            f"\n💡 [{self.console_theme.dim}]This model is a base model that doesn't support chat/tools. Try a different model.[/{self.console_theme.dim}]"
                        )
                    elif (
                        "not supported" in str(e.message).lower()
                        and "tool" in str(e.message).lower()
                    ):
                        self.console.print(
                            f"\n💡 [{self.console_theme.dim}]This model doesn't support tool/function calling. Try without tools or use a different model.[/{self.console_theme.dim}]"
                        )

                    # Return a clean error message
                    error_msg = f"OCI API Error ({e.status}): {e.message}"
                else:
                    # Generic error handling
                    error_msg = f"Error during agent execution: {str(e)}"
                    self.console.print(
                        Panel(error_msg, title="Error", border_style="red", padding=(1, 2))
                    )

                return error_msg, messages

        if step_count >= max_steps:
            self.console.print(
                f"[{self.console_theme.warning}]Reached maximum steps ({max_steps})[/{self.console_theme.warning}]"
            )

        return final_response_content, messages

    def _detect_tool_call_loops(
        self,
        new_tool_calls: list[ToolCall],
        recent_tool_calls: list[str],
        window_size: int,
        max_same_calls: int,
    ) -> bool:
        """
        Detect if the agent is stuck in a tool call loop.

        Args:
            new_tool_calls: Tool calls from current response
            recent_tool_calls: List of recent tool call names
            window_size: Size of the sliding window for detection
            max_same_calls: Maximum allowed consecutive calls to same tool

        Returns:
            True if a loop is detected, False otherwise
        """
        # Check if any of the new tool calls would create a loop
        for tool_call in new_tool_calls:
            tool_name = tool_call.name

            # Count how many times this tool appears in recent calls
            recent_count = recent_tool_calls.count(tool_name)

            # If this tool has been called too many times recently, it's a loop
            if recent_count >= max_same_calls:
                return True

            # Also check for alternating patterns (A-B-A-B...)
            if len(recent_tool_calls) >= 4:
                last_four = recent_tool_calls[-4:]
                if (
                    last_four[0] == last_four[2]
                    and last_four[1] == last_four[3]
                    and tool_name in last_four
                ):
                    return True

        return False

    def run(self, input: str, **kwargs) -> RunResponse:
        """Synchronous wrapper for run_async."""
        try:
            asyncio.get_running_loop()
            # We're already in an event loop, can't use run_until_complete
            # This shouldn't happen in normal usage
            raise RuntimeError(
                "Cannot call synchronous run() from within an async context. Use run_async() instead."
            )
        except RuntimeError:
            # No event loop running, create one
            return asyncio.run(self.run_async(input, **kwargs))

    async def _handle_tool_calls(
        self,
        tool_calls: list[ToolCall],
        on_fulfilled_action: Callable | None = None,
        status=None,
        interrupt_check: Callable[[], bool] | None = None,
    ) -> list[PerformedAction]:
        """Handle tool calls from the AI."""
        performed_actions = []

        # Update status if provided, otherwise print message
        if status:
            status.update(
                f"[{self.console_theme.bold} {self.console_theme.info}]Executing tools...[/{self.console_theme.bold} {self.console_theme.info}]"
            )
        else:
            self.console.print(
                f"\n[{self.console_theme.dim}]Executing tools...[/{self.console_theme.dim}]"
            )

        for tool_call in tool_calls:
            # Check for interrupt before each tool execution
            if interrupt_check and interrupt_check():
                if status:
                    status.stop()
                self.console.print(
                    f"\n[{self.console_theme.warning}]Tool execution interrupted by user[/{self.console_theme.warning}]"
                )
                break

            # Create required action
            required_action = RequiredAction.from_tool_call(tool_call)

            # Show execution
            self._print_tool_execution(tool_call)

            # Execute tool
            performed_action = await self._execute_tool_call(tool_call, required_action.action_id)

            if performed_action:
                performed_actions.append(performed_action)

                # Show result
                self._print_tool_result(performed_action)

                # Callback if provided
                if on_fulfilled_action:
                    on_fulfilled_action(required_action, performed_action)

        return performed_actions

    async def _execute_tool_call(
        self, tool_call: ToolCall, action_id: str
    ) -> PerformedAction | None:
        """Execute a single tool call."""
        try:
            # Get the tool
            tool = self._tool_map.get(tool_call.name)
            if not tool:
                return PerformedAction(
                    action_id=action_id,
                    performed_action_type=PerformedActionType.FUNCTION_CALLING,
                    function_call_output=f"Error: Tool '{tool_call.name}' not found",
                )

            # Execute
            result = await tool.execute(tool_call.arguments)

            # Format result
            if isinstance(result, dict):
                output = json.dumps(result, indent=2)
            elif not isinstance(result, str):
                output = str(result)
            else:
                output = result

            return PerformedAction(
                action_id=action_id,
                performed_action_type=PerformedActionType.FUNCTION_CALLING,
                function_call_output=output,
            )

        except Exception as e:
            from ..errors import ToolExecutionError

            # Create a proper tool execution error
            tool_error = ToolExecutionError(message=str(e), tool_name=tool_call.name, cause=e)

            return PerformedAction(
                action_id=action_id,
                performed_action_type=PerformedActionType.FUNCTION_CALLING,
                function_call_output=f"Error: {tool_error.user_message()}",
            )

    def _print_response(self, content: str):
        """Print AI response."""
        self.console.print(
            f"\n[{self.console_theme.bold} {self.console_theme.assistant_message}]{self.name}:[/{self.console_theme.bold} {self.console_theme.assistant_message}] {content}"
        )

    def _print_tool_execution(self, tool_call: ToolCall):
        """Print tool execution info."""
        self.console.print(
            f"\n[{self.console_theme.info}]→ Running tool:[/{self.console_theme.info}] {tool_call.name}"
        )
        if tool_call.arguments:
            args_str = json.dumps(tool_call.arguments, indent=2)
            self.console.print(
                Panel(
                    Syntax(args_str, "json", theme="monokai"),
                    title=f"[{self.console_theme.info}]Arguments[/{self.console_theme.info}]",
                    expand=False,
                )
            )

    def _print_tool_result(self, action: PerformedAction):
        """Print tool result."""
        if "Error" in action.function_call_output:
            self.console.print(
                f"[{self.console_theme.error}]✗ Error:[/{self.console_theme.error}] {action.function_call_output}"
            )
        else:
            self.console.print(
                f"[{self.console_theme.success}]✓ Result:[/{self.console_theme.success}]"
            )
            # Try to format as JSON
            try:
                result_json = json.loads(action.function_call_output)
                self.console.print(
                    Panel(
                        Syntax(json.dumps(result_json, indent=2), "json", theme="monokai"),
                        expand=False,
                    )
                )
            except Exception:
                self.console.print(Panel(action.function_call_output, expand=False))

    def as_tool(
        self, tool_name: str | None = None, tool_description: str | None = None
    ) -> FunctionTool:
        """
        Convert this agent to a tool that can be used by other agents.

        Args:
            tool_name: Optional custom name
            tool_description: Optional custom description

        Returns:
            FunctionTool representing this agent
        """
        from coda.services.agents.decorators import tool

        name = tool_name or self.name or "run_sub_agent"
        description = tool_description or self.description or "Run a sub-agent"

        # Create wrapper function
        @tool(name=name, description=description)
        async def agent_wrapper(input: str, **kwargs) -> str:
            """Execute this agent with the given input."""
            response = await self.run_async(input=input, **kwargs)
            return response.content

        return FunctionTool.from_callable(agent_wrapper)
