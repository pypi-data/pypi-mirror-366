import json
import os
from typing import List, Type, Optional, Any
from litellm import completion
from .tool import ToolInterface
from .context import AgentContext
from .exceptions import AgentExecutionError


class BaseAgent:
    """
    Base class for AI agents using litellm for LLM integration.
    """
    name: str = "base_agent"
    description: str = "A base AI agent"
    instructions: str = "You are a helpful AI assistant."
    instructions_file: Optional[str] = None
    model: str = "gpt-4o"
    tools: List[Type[ToolInterface]] = []
    
    @classmethod
    def run(cls, message: str, context: Optional[AgentContext] = None) -> str:
        """
        Run the agent with a message and return the response.
        
        Args:
            message: The user's message
            context: Optional agent context for maintaining conversation state
            
        Returns:
            str: The agent's response
        """
        # Create an instance to call hooks
        instance = cls()
        
        # Create context if not provided
        if context is None:
            context = AgentContext()
        else:
            # Reset tool count for new run
            context.reset_tool_count()
        
        # Add system message if this is a new conversation
        if not context.messages:
            # Get instructions from file if specified, otherwise use inline instructions
            instructions = cls._get_instructions()
            context.add_message("system", instructions)
        
        # Add user message
        context.add_message("user", message)
        
        # Initialize tools
        tool_instances = {tool().definition()["name"]: tool() for tool in cls.tools}
        tool_definitions = [tool_instance.definition() for tool_instance in tool_instances.values()]
        
        # Main execution loop
        while True:
            try:
                # Check if we can still make tool calls
                if not context.can_call_tools() and tool_definitions:
                    # Remove tools from the request if we've hit the limit
                    # Call hook before LLM call
                    try:
                        instance.before_llm_call(context.messages, None)
                    except Exception:
                        pass  # Don't let hook errors interrupt execution
                    
                    response = completion(
                        model=cls.model,
                        messages=context.messages
                    )
                else:
                    # Normal request with tools
                    # Call hook before LLM call
                    try:
                        instance.before_llm_call(context.messages, tool_definitions)
                    except Exception:
                        pass  # Don't let hook errors interrupt execution
                    
                    response = completion(
                        model=cls.model,
                        messages=context.messages,
                        tools=tool_definitions if tool_definitions else None
                    )
                
                # Call hook after LLM response
                try:
                    instance.after_llm_response(response, context.messages)
                except Exception:
                    pass  # Don't let hook errors interrupt execution
                
                # Extract the response
                message_content = response.choices[0].message
                
                # Check if the model wants to use tools
                if hasattr(message_content, 'tool_calls') and message_content.tool_calls:
                    # Add assistant message with tool calls
                    context.add_message("assistant", message_content.content or "")
                    
                    # Process each tool call
                    for tool_call in message_content.tool_calls:
                        context.add_tool_call({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        })
                        
                        # Execute the tool
                        tool_name = tool_call.function.name
                        
                        try:
                            if tool_name not in tool_instances:
                                # Return error as tool result instead of throwing exception
                                error_result = json.dumps({"error": f"Tool '{tool_name}' not found"})
                                context.add_tool_result(tool_call.id, error_result)
                                continue
                            
                            # Parse arguments
                            arguments = json.loads(tool_call.function.arguments)
                            
                            # Call hook before tool call
                            try:
                                instance.before_tool_call(tool_name, arguments, context)
                            except Exception:
                                pass  # Don't let hook errors interrupt execution
                            
                            # Execute tool
                            tool_instance = tool_instances[tool_name]
                            result = tool_instance.execute(arguments, context)
                            
                            # Call hook after tool result
                            try:
                                instance.after_tool_result(tool_name, result, context)
                            except Exception:
                                pass  # Don't let hook errors interrupt execution
                            
                            # Add tool result
                            context.add_tool_result(tool_call.id, result)
                            
                        except Exception as e:
                            # Add error as tool result
                            error_result = json.dumps({"error": str(e)})
                            context.add_tool_result(tool_call.id, error_result)
                    
                    # Check if we've hit the tool call limit
                    if not context.can_call_tools():
                        # Force a final response without tools
                        # Call hook before LLM call
                        try:
                            instance.before_llm_call(context.messages, None)
                        except Exception:
                            pass  # Don't let hook errors interrupt execution
                        
                        final_response = completion(
                            model=cls.model,
                            messages=context.messages
                        )
                        
                        # Call hook after LLM response
                        try:
                            instance.after_llm_response(final_response, context.messages)
                        except Exception:
                            pass  # Don't let hook errors interrupt execution
                        
                        final_content = final_response.choices[0].message.content
                        context.add_message("assistant", final_content)
                        return final_content
                    
                    # Continue the loop for another iteration
                    continue
                
                else:
                    # No tool calls, return the response
                    content = message_content.content
                    context.add_message("assistant", content)
                    return content
                    
            except Exception as e:
                raise AgentExecutionError(f"Agent execution failed: {str(e)}")
    
    @classmethod
    def _get_instructions(cls) -> str:
        """
        Get instructions from file if specified, otherwise return inline instructions.
        
        Returns:
            str: The instructions for the agent
        """
        if cls.instructions_file:
            try:
                # Just use the path as provided by the user
                # They can use absolute or relative paths based on their project structure
                with open(cls.instructions_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except FileNotFoundError:
                raise AgentExecutionError(f"Instructions file not found: {cls.instructions_file}")
            except Exception as e:
                raise AgentExecutionError(f"Error reading instructions file: {str(e)}")
        
        return cls.instructions
    
    def before_llm_call(self, messages: List[dict], tools: Optional[List[dict]]) -> None:
        """
        Hook called before making an LLM call.
        Override this method to add custom behavior before LLM calls.
        
        Args:
            messages: The messages that will be sent to the LLM
            tools: The tools available for this call (None if no tools)
        """
        pass
    
    def after_llm_response(self, response: Any, messages: List[dict]) -> None:
        """
        Hook called after receiving an LLM response.
        Override this method to add custom behavior after LLM responses.
        
        Args:
            response: The response object from the LLM
            messages: The messages that were sent to the LLM
        """
        pass
    
    def before_tool_call(self, tool_name: str, arguments: dict, context: AgentContext) -> None:
        """
        Hook called before executing a tool.
        Override this method to add custom behavior before tool execution.
        
        Args:
            tool_name: The name of the tool being called
            arguments: The arguments being passed to the tool
            context: The current agent context
        """
        pass
    
    def after_tool_result(self, tool_name: str, result: str, context: AgentContext) -> None:
        """
        Hook called after a tool returns a result.
        Override this method to add custom behavior after tool execution.
        
        Args:
            tool_name: The name of the tool that was called
            result: The result returned by the tool
            context: The current agent context
        """
        pass
    
    @classmethod
    def with_context(cls, context: AgentContext) -> 'AgentRunner':
        """
        Create an agent runner with a specific context.
        
        Args:
            context: The agent context to use
            
        Returns:
            AgentRunner: A runner instance bound to the context
        """
        return AgentRunner(cls, context)


class AgentRunner:
    """Helper class to run an agent with a persistent context."""
    
    def __init__(self, agent_class: Type[BaseAgent], context: AgentContext):
        self.agent_class = agent_class
        self.context = context
    
    def run(self, message: str) -> str:
        """Run the agent with the stored context."""
        return self.agent_class.run(message, self.context)