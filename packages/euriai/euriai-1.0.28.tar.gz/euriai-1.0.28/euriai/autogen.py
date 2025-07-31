from typing import Optional, Dict, Any, List, Union
from types import SimpleNamespace
from euriai.client import EuriaiClient

try:
    # Try newer AutoGen structure first (v0.6+)
    try:
        from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
        from autogen_agentchat.teams import GroupChat, GroupChatManager
        import autogen_agentchat as autogen
    except ImportError:
        # Try alternative newer structure
        try:
            from autogen_agentchat.base import AssistantAgent, UserProxyAgent
            from autogen_agentchat import GroupChat, GroupChatManager
            import autogen_agentchat as autogen
        except ImportError:
            # Fall back to older AutoGen structure
            import autogen
            from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    autogen = None
    AssistantAgent = UserProxyAgent = GroupChat = GroupChatManager = None

def _ensure_autogen_imports():
    """Ensure AutoGen classes are properly imported."""
    global autogen, AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    
    try:
        # Force re-import of autogen module
        import importlib
        import sys
        
        # Remove any cached modules to force fresh import
        if 'autogen' in sys.modules:
            importlib.reload(sys.modules['autogen'])
        
        # Import the main module
        import autogen as _autogen
        
        # Import individual classes with explicit error handling
        from autogen import AssistantAgent as _AssistantAgent
        from autogen import UserProxyAgent as _UserProxyAgent  
        from autogen import GroupChat as _GroupChat
        from autogen import GroupChatManager as _GroupChatManager
        
        # Verify that all classes are not None
        if _AssistantAgent is None or _UserProxyAgent is None:
            raise ImportError("AutoGen classes imported as None")
        
        # Update global variables
        autogen = _autogen
        AssistantAgent = _AssistantAgent
        UserProxyAgent = _UserProxyAgent
        GroupChat = _GroupChat
        GroupChatManager = _GroupChatManager
        
        # Verify the globals were updated
        if AssistantAgent is None:
            raise ImportError("Failed to update global AssistantAgent variable")
            
        return True
        
    except ImportError as e:
        from . import check_optional_dependency
        check_optional_dependency("pyautogen", "AutoGen", "autogen")

class EuriaiModelClient:
    """
    Custom model client that uses Euri API for AutoGen integration.
    Implements the ModelClient protocol required by AutoGen.
    """
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize the Euri model client.
        
        Args:
            config: Configuration dictionary containing:
                - model: Euri model name (e.g., 'gpt-4.1-nano', 'claude-3-5-sonnet')
                - api_key: Euri API key
                - temperature: Model temperature (optional)
                - max_tokens: Maximum tokens (optional)
        """
        self.config = config
        self.model = config["model"]
        self.api_key = config.get("api_key")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)
        
        if not self.api_key:
            raise ValueError("Euri API key is required in config")
        
        # Initialize Euri client
        self.client = EuriaiClient(
            api_key=self.api_key,
            model=self.model
        )
        
        print(f"EuriaiModelClient initialized with model: {self.model}")
    
    def create(self, params: Dict[str, Any]) -> SimpleNamespace:
        """
        Create a response using the Euri API.
        
        Args:
            params: Parameters containing:
                - messages: List of message dictionaries
                - n: Number of responses (default 1)
                - temperature: Temperature override
                - max_tokens: Max tokens override
                
        Returns:
            Response object following AutoGen's ModelClientResponseProtocol
        """
        # Extract parameters
        messages = params.get("messages", [])
        n = params.get("n", 1)
        temperature = params.get("temperature", self.temperature)
        max_tokens = params.get("max_tokens", self.max_tokens)
        
        # Convert messages to prompt format
        prompt = self._convert_messages_to_prompt(messages)
        
        # Create response object
        response = SimpleNamespace()
        response.choices = []
        response.model = self.model
        response.usage = SimpleNamespace()
        
        # Generate responses
        for _ in range(n):
            try:
                # Call Euri API
                euri_response = self.client.generate_completion(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Extract content
                content = euri_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Create choice object
                choice = SimpleNamespace()
                choice.message = SimpleNamespace()
                choice.message.content = content
                choice.message.function_call = None
                choice.finish_reason = "stop"
                
                response.choices.append(choice)
                
                # Add usage info if available
                if "usage" in euri_response:
                    usage = euri_response["usage"]
                    response.usage.prompt_tokens = usage.get("prompt_tokens", 0)
                    response.usage.completion_tokens = usage.get("completion_tokens", 0)
                    response.usage.total_tokens = usage.get("total_tokens", 0)
                
            except Exception as e:
                print(f"Error calling Euri API: {e}")
                # Create error response
                choice = SimpleNamespace()
                choice.message = SimpleNamespace()
                choice.message.content = f"Error: {str(e)}"
                choice.message.function_call = None
                choice.finish_reason = "error"
                response.choices.append(choice)
        
        return response
    
    def message_retrieval(self, response: SimpleNamespace) -> List[str]:
        """
        Retrieve messages from the response.
        
        Args:
            response: Response object from create()
            
        Returns:
            List of response strings
        """
        return [choice.message.content for choice in response.choices]
    
    def cost(self, response: SimpleNamespace) -> float:
        """
        Calculate the cost of the response.
        
        Args:
            response: Response object from create()
            
        Returns:
            Cost of the response (0 for now)
        """
        return 0.0
    
    @staticmethod
    def get_usage(response: SimpleNamespace) -> Dict[str, Any]:
        """
        Get usage statistics from the response.
        
        Args:
            response: Response object from create()
            
        Returns:
            Usage statistics dictionary
        """
        usage = getattr(response, 'usage', SimpleNamespace())
        return {
            "prompt_tokens": getattr(usage, 'prompt_tokens', 0),
            "completion_tokens": getattr(usage, 'completion_tokens', 0),
            "total_tokens": getattr(usage, 'total_tokens', 0),
            "cost": 0.0,
            "model": response.model
        }
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert AutoGen messages to a prompt string.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"{role}: {content}")
        
        return "\n".join(prompt_parts)

class EuriaiAutoGen:
    """
    Enhanced AutoGen integration that uses Euri API for all LLM calls.
    """
    
    def __init__(self, api_key: str, default_model: str = "gpt-4.1-nano"):
        """
        Initialize the EuriaiAutoGen wrapper.
        
        Args:
            api_key: Your Euri API key
            default_model: Default model to use
        """
        _ensure_autogen_imports()
        
        self.api_key = api_key
        self.default_model = default_model
        self.agents: List[Any] = []
        self.group_chat: Optional[GroupChat] = None
        self.group_chat_manager: Optional[GroupChatManager] = None
        self.history: List[Dict[str, Any]] = []
    
    def create_assistant_agent(
        self,
        name: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> "AssistantAgent":
        """
        Create an assistant agent with Euri API integration.
        
        Args:
            name: Agent name
            system_message: System message for the agent
            model: Euri model to use
            temperature: Model temperature
            max_tokens: Maximum tokens
            **kwargs: Additional arguments for AssistantAgent
            
        Returns:
            Configured AssistantAgent
        """
        # Import AutoGen AssistantAgent class
        try:
            # Try newer AutoGen structure first (v0.6+)
            try:
                from autogen_agentchat.agents import AssistantAgent
            except ImportError:
                try:
                    from autogen_agentchat.base import AssistantAgent
                except ImportError:
                    # Fall back to older AutoGen structure
                    from autogen import AssistantAgent
        except ImportError:
            from . import check_optional_dependency
            check_optional_dependency("pyautogen", "AutoGen", "autogen")
            # This line will never be reached if AutoGen is missing
            # because check_optional_dependency raises ImportError
            raise  # Re-raise the original ImportError
        
        # Create config for Euri API
        config_list = [{
            "model": model or self.default_model,
            "model_client_cls": EuriaiModelClient,
            "api_key": self.api_key,
            "temperature": temperature,
            "max_tokens": max_tokens
        }]
        
        # Create agent with proper configuration for different AutoGen versions
        print(f"Debug: Creating AssistantAgent with name={name}, model={model or self.default_model}")
        
        # First, let's try to determine the correct constructor signature
        import inspect
        try:
            sig = inspect.signature(AssistantAgent.__init__)
            print(f"Debug: AssistantAgent constructor signature: {sig}")
        except Exception as e:
            print(f"Debug: Could not inspect AssistantAgent signature: {e}")
        
        # Try different constructor patterns
        agent = None
        last_error = None
        
        # Pattern 1: model_client with EuriaiModelClient
        try:
            print("Debug: Trying model_client=EuriaiModelClient")
            agent = AssistantAgent(
                name=name,
                system_message=system_message,
                model_client=EuriaiModelClient(config_list[0]),
                **kwargs
            )
            print("Debug: Success with model_client=EuriaiModelClient")
        except TypeError as e:
            last_error = e
            print(f"Debug: Failed with model_client=EuriaiModelClient: {e}")
            
            # Pattern 2: Minimal constructor
            try:
                print("Debug: Trying minimal constructor")
                agent = AssistantAgent(
                    name=name,
                    system_message=system_message,
                    **kwargs
                )
                print("Debug: Success with minimal constructor")
            except TypeError as e:
                last_error = e
                print(f"Debug: Failed with minimal constructor: {e}")
                
                # Pattern 3: Try with just name
                try:
                    print("Debug: Trying with just name")
                    agent = AssistantAgent(
                        name=name,
                        **kwargs
                    )
                    print("Debug: Success with just name")
                except TypeError as e:
                    last_error = e
                    print(f"Debug: Failed with just name: {e}")
                    raise last_error
        
        if agent is None:
            raise last_error
        
        # Debug: Check what methods the agent has
        print(f"Debug: AssistantAgent '{name}' methods: {[m for m in dir(agent) if not m.startswith('_')]}")
        print(f"Debug: AssistantAgent '{name}' has initiate_chat: {hasattr(agent, 'initiate_chat')}")
        
        # Note: No need to register model client with new AutoGen API
        # The model_client is passed directly to the constructor
        
        self.agents.append(agent)
        return agent
    
    def create_user_proxy_agent(
        self,
        name: str,
        is_termination_msg: Optional[callable] = None,
        code_execution_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "UserProxyAgent":
        """
        Create a user proxy agent.
        
        Args:
            name: Agent name
            is_termination_msg: Termination message function
            code_execution_config: Code execution configuration
            **kwargs: Additional arguments for UserProxyAgent
            
        Returns:
            Configured UserProxyAgent
        """
        # Import AutoGen UserProxyAgent class
        try:
            # Try newer AutoGen structure first (v0.6+)
            try:
                from autogen_agentchat.agents import UserProxyAgent
            except ImportError:
                try:
                    from autogen_agentchat.base import UserProxyAgent
                except ImportError:
                    # Fall back to older AutoGen structure
                    from autogen import UserProxyAgent
        except ImportError:
            from . import check_optional_dependency
            check_optional_dependency("pyautogen", "AutoGen", "autogen")
            # This line will never be reached if AutoGen is missing
            # because check_optional_dependency raises ImportError
            raise  # Re-raise the original ImportError
        
        # Try different constructor patterns for UserProxyAgent
        agent = None
        last_error = None
        
        # Pattern 1: Full parameters
        try:
            print(f"Debug: Creating UserProxyAgent '{name}' with full parameters")
            agent = UserProxyAgent(
                name=name,
                is_termination_msg=is_termination_msg,
                code_execution_config=code_execution_config or {"use_docker": False},
                **kwargs
            )
            print(f"Debug: UserProxyAgent '{name}' created successfully")
        except TypeError as e:
            last_error = e
            print(f"Debug: UserProxyAgent creation failed with full parameters: {e}")
            
            # Pattern 2: Minimal parameters
            try:
                print(f"Debug: Creating UserProxyAgent '{name}' with minimal parameters")
                agent = UserProxyAgent(
                    name=name,
                    **kwargs
                )
                print(f"Debug: UserProxyAgent '{name}' created successfully with minimal parameters")
            except TypeError as e:
                last_error = e
                print(f"Debug: UserProxyAgent creation failed with minimal parameters: {e}")
                raise last_error
        
        if agent is None:
            raise last_error
        
        # Debug: Check what methods the agent has
        print(f"Debug: UserProxyAgent '{name}' methods: {[m for m in dir(agent) if not m.startswith('_')]}")
        print(f"Debug: UserProxyAgent '{name}' has initiate_chat: {hasattr(agent, 'initiate_chat')}")
        
        self.agents.append(agent)
        return agent
    
    def create_group_chat(
        self,
        agents: List[Any],
        messages: Optional[List[Dict[str, str]]] = None,
        max_round: int = 10,
        admin_name: str = "Admin",
        speaker_selection_method: str = "auto",
        **kwargs
    ) -> GroupChat:
        """
        Create a group chat with multiple agents.
        
        Args:
            agents: List of agents for the group chat
            messages: Initial messages
            max_round: Maximum number of rounds
            admin_name: Admin agent name
            speaker_selection_method: Speaker selection method
            **kwargs: Additional arguments for GroupChat
            
        Returns:
            Configured GroupChat
        """
        # Import AutoGen GroupChat class
        try:
            # Try newer AutoGen structure first (v0.6+)
            try:
                from autogen_agentchat.teams import GroupChat
            except ImportError:
                try:
                    from autogen_agentchat import GroupChat
                except ImportError:
                    # Fall back to older AutoGen structure
                    from autogen import GroupChat
        except ImportError:
            from . import check_optional_dependency
            check_optional_dependency("pyautogen", "AutoGen", "autogen")
            raise  # Re-raise the original ImportError
        
        self.group_chat = GroupChat(
            agents=agents,
            messages=messages or [],
            max_round=max_round,
            admin_name=admin_name,
            speaker_selection_method=speaker_selection_method,
            **kwargs
        )
        
        return self.group_chat
    
    def create_group_chat_manager(
        self,
        groupchat: GroupChat,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> GroupChatManager:
        """
        Create a group chat manager.
        
        Args:
            groupchat: GroupChat instance
            model: Euri model to use
            temperature: Model temperature
            max_tokens: Maximum tokens
            **kwargs: Additional arguments for GroupChatManager
            
        Returns:
            Configured GroupChatManager
        """
        # Import AutoGen GroupChatManager class
        try:
            # Try newer AutoGen structure first (v0.6+)
            try:
                from autogen_agentchat.teams import GroupChatManager
            except ImportError:
                try:
                    from autogen_agentchat import GroupChatManager
                except ImportError:
                    # Fall back to older AutoGen structure
                    from autogen import GroupChatManager
        except ImportError:
            from . import check_optional_dependency
            check_optional_dependency("pyautogen", "AutoGen", "autogen")
            raise  # Re-raise the original ImportError
        
        # Create config for Euri API
        config_list = [{
            "model": model or self.default_model,
            "model_client_cls": EuriaiModelClient,
            "api_key": self.api_key,
            "temperature": temperature,
            "max_tokens": max_tokens
        }]
        
        # Create manager with proper configuration for different AutoGen versions
        print(f"Debug: Creating GroupChatManager with model={model or self.default_model}")
        
        # Try different constructor patterns
        manager = None
        last_error = None
        
        # Pattern 1: model_client with EuriaiModelClient
        try:
            print("Debug: Trying GroupChatManager with model_client=EuriaiModelClient")
            manager = GroupChatManager(
                groupchat=groupchat,
                model_client=EuriaiModelClient(config_list[0]),
                **kwargs
            )
            print("Debug: Success with model_client=EuriaiModelClient")
        except TypeError as e:
            last_error = e
            print(f"Debug: Failed with model_client=EuriaiModelClient: {e}")
            
            # Pattern 2: Minimal constructor
            try:
                print("Debug: Trying GroupChatManager with minimal constructor")
                manager = GroupChatManager(
                    groupchat=groupchat,
                    **kwargs
                )
                print("Debug: Success with minimal constructor")
            except TypeError as e:
                last_error = e
                print(f"Debug: Failed with minimal constructor: {e}")
                raise last_error
        
        if manager is None:
            raise last_error
        
        self.group_chat_manager = manager
        
        # Note: No need to register model client with new AutoGen API
        # The model_client is passed directly to the constructor
        
        return self.group_chat_manager
    
    def run_chat(
        self,
        agent1: Any,
        agent2: Any,
        message: str,
        max_turns: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a chat between two agents.
        
        Args:
            agent1: First agent (typically UserProxyAgent)
            agent2: Second agent (typically AssistantAgent)
            message: Initial message
            max_turns: Maximum number of turns
            **kwargs: Additional arguments for the conversation
            
        Returns:
            Chat result
        """
        try:
            # Check if agents have the old initiate_chat method (older AutoGen)
            if hasattr(agent1, 'initiate_chat') and callable(getattr(agent1, 'initiate_chat')):
                print(f"Debug: Using legacy initiate_chat API with {agent1.name}")
                result = agent1.initiate_chat(
                    agent2,
                    message=message,
                    max_turns=max_turns,
                    **kwargs
                )
            elif hasattr(agent2, 'initiate_chat') and callable(getattr(agent2, 'initiate_chat')):
                print(f"Debug: Using legacy initiate_chat API with {agent2.name}")
                result = agent2.initiate_chat(
                    agent1,
                    message=message,
                    max_turns=max_turns,
                    **kwargs
                )
            else:
                # New AutoGen API (v0.6+) - use message-based approach
                print("Debug: Using new AutoGen API with message-based conversation")
                result = self._run_new_autogen_chat(agent1, agent2, message, max_turns, **kwargs)
            
            # Store in history
            self.history.append({
                "type": "two_agent_chat",
                "agent1": getattr(agent1, 'name', str(agent1)),
                "agent2": getattr(agent2, 'name', str(agent2)),
                "message": message,
                "result": result
            })
            
            return result
            
        except Exception as e:
            # Provide detailed error information
            error_details = {
                "error": str(e),
                "agent1_type": type(agent1).__name__,
                "agent2_type": type(agent2).__name__,
                "agent1_has_initiate_chat": hasattr(agent1, 'initiate_chat'),
                "agent2_has_initiate_chat": hasattr(agent2, 'initiate_chat'),
                "agent1_has_run": hasattr(agent1, 'run'),
                "agent2_has_run": hasattr(agent2, 'run'),
                "available_methods": {
                    "agent1": [method for method in dir(agent1) if not method.startswith('_')],
                    "agent2": [method for method in dir(agent2) if not method.startswith('_')]
                }
            }
            print(f"Error in chat: {e}")
            print(f"Debug info: {error_details}")
            return error_details
    
    def _run_new_autogen_chat(
        self,
        agent1: Any,
        agent2: Any,
        message: str,
        max_turns: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run chat using the new AutoGen API (v0.6+).
        
        Args:
            agent1: First agent (typically UserProxyAgent)
            agent2: Second agent (typically AssistantAgent)
            message: Initial message
            max_turns: Maximum number of turns
            **kwargs: Additional arguments
            
        Returns:
            Chat result
        """
        try:
            # Import message types for new AutoGen API
            try:
                from autogen_core.components.models import UserMessage, AssistantMessage
            except ImportError:
                try:
                    from autogen_agentchat.messages import UserMessage, AssistantMessage
                except ImportError:
                    # Fallback: create simple message objects
                    UserMessage = lambda content: {"role": "user", "content": content}
                    AssistantMessage = lambda content: {"role": "assistant", "content": content}
            
            messages = []
            current_message = UserMessage(content=message)
            messages.append({"role": "user", "content": message, "sender": getattr(agent1, 'name', 'User')})
            
            # Alternate between agents for max_turns
            current_agent = agent2  # Start with the assistant agent
            other_agent = agent1
            
            for turn in range(max_turns):
                print(f"Debug: Turn {turn + 1}, {getattr(current_agent, 'name', 'Agent')} responding...")
                
                # Check if agent has 'run' method
                if hasattr(current_agent, 'run'):
                    # Use the 'run' method with messages
                    try:
                        # Create message list in the format expected by new AutoGen
                        message_objects = []
                        for msg in messages:
                            if msg["role"] == "user":
                                message_objects.append(UserMessage(content=msg["content"]))
                            else:
                                message_objects.append(AssistantMessage(content=msg["content"]))
                        
                        # Call the run method
                        response = current_agent.run(messages=message_objects)
                        
                        # Extract content from response
                        if hasattr(response, 'messages') and response.messages:
                            content = response.messages[-1].content if hasattr(response.messages[-1], 'content') else str(response.messages[-1])
                        elif hasattr(response, 'content'):
                            content = response.content
                        else:
                            content = str(response)
                        
                        # Add response to messages
                        messages.append({
                            "role": "assistant" if current_agent == agent2 else "user",
                            "content": content,
                            "sender": getattr(current_agent, 'name', 'Agent')
                        })
                        
                        print(f"Debug: {getattr(current_agent, 'name', 'Agent')} responded: {content[:100]}...")
                        
                        # Check for termination
                        if "TERMINATE" in content.upper():
                            print("Debug: Conversation terminated by agent")
                            break
                            
                    except Exception as e:
                        print(f"Debug: Error calling 'run' method: {e}")
                        # Try with simpler approach
                        try:
                            response = current_agent.run(message)
                            content = str(response)
                            messages.append({
                                "role": "assistant" if current_agent == agent2 else "user",
                                "content": content,
                                "sender": getattr(current_agent, 'name', 'Agent')
                            })
                        except Exception as e2:
                            print(f"Debug: Error with simple 'run' call: {e2}")
                            break
                
                else:
                    print(f"Debug: Agent {getattr(current_agent, 'name', 'Agent')} doesn't have 'run' method")
                    break
                
                # Switch agents for next turn
                current_agent, other_agent = other_agent, current_agent
            
            return {
                "success": True,
                "messages": messages,
                "total_turns": len([m for m in messages if m["role"] == "assistant"]),
                "conversation_summary": f"Completed {len(messages)} message exchanges"
            }
            
        except Exception as e:
            print(f"Debug: Error in new AutoGen chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages": messages if 'messages' in locals() else []
            }
    
    def run_group_chat(
        self,
        message: str,
        max_turns: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a group chat with multiple agents.
        
        Args:
            message: Initial message
            max_turns: Maximum number of turns
            **kwargs: Additional arguments for initiate_chat
            
        Returns:
            Group chat result
        """
        if not self.group_chat_manager:
            raise ValueError("Group chat manager not created. Use create_group_chat_manager() first.")
        
        try:
            # Create a user proxy to start the conversation
            user_proxy = self.create_user_proxy_agent(
                name="User",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0
            )
            
            result = user_proxy.initiate_chat(
                self.group_chat_manager,
                message=message,
                max_turns=max_turns,
                **kwargs
            )
            
            # Store in history
            self.history.append({
                "type": "group_chat",
                "message": message,
                "result": result
            })
            
            return result
            
        except Exception as e:
            print(f"Error in group chat: {e}")
            return {"error": str(e)}
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available Euri models.
        
        Returns:
            List of available models
        """
        return [
            "gpt-4.1-nano",
            "gpt-4.1-turbo",
            "gpt-4.1-preview",
            "claude-3-5-sonnet",
            "claude-3-5-haiku",
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get chat history.
        
        Returns:
            List of chat history entries
        """
        return self.history
    
    def reset(self):
        """
        Reset agents, group chat, and history.
        """
        self.agents = []
        self.group_chat = None
        self.group_chat_manager = None
        self.history = []
    
    def create_config_list(
        self,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Create a configuration list for manual agent creation.
        
        Args:
            model: Euri model name
            temperature: Model temperature
            max_tokens: Maximum tokens
            
        Returns:
            Configuration list for AutoGen
        """
        return [{
            "model": model,
            "model_client_cls": EuriaiModelClient,
            "api_key": self.api_key,
            "temperature": temperature,
            "max_tokens": max_tokens
        }]
    
    def test_setup(self) -> Dict[str, Any]:
        """
        Test the AutoGen setup and provide diagnostic information.
        
        Returns:
            Dictionary with setup test results
        """
        results = {
            "autogen_available": False,
            "agent_classes_available": False,
            "can_create_assistant": False,
            "can_create_user_proxy": False,
            "agents_have_initiate_chat": False,
            "errors": [],
            "recommendations": []
        }
        
        try:
            # Test AutoGen import
            _ensure_autogen_imports()
            results["autogen_available"] = True
            
            # Test agent classes
            if AssistantAgent and UserProxyAgent:
                results["agent_classes_available"] = True
            else:
                results["errors"].append("AutoGen agent classes not properly imported")
            
            # Test agent creation
            try:
                test_assistant = self.create_assistant_agent(
                    name="TestAssistant",
                    model="gpt-4.1-nano"
                )
                results["can_create_assistant"] = True
                results["assistant_has_initiate_chat"] = hasattr(test_assistant, 'initiate_chat')
            except Exception as e:
                results["errors"].append(f"Failed to create AssistantAgent: {e}")
            
            try:
                test_user_proxy = self.create_user_proxy_agent(
                    name="TestUser"
                )
                results["can_create_user_proxy"] = True
                results["user_proxy_has_initiate_chat"] = hasattr(test_user_proxy, 'initiate_chat')
            except Exception as e:
                results["errors"].append(f"Failed to create UserProxyAgent: {e}")
            
            # Check if at least one agent type has initiate_chat
            if results.get("assistant_has_initiate_chat") or results.get("user_proxy_has_initiate_chat"):
                results["agents_have_initiate_chat"] = True
            
            # Generate recommendations
            if not results["autogen_available"]:
                results["recommendations"].append("Install AutoGen: pip install pyautogen")
            
            if not results["agents_have_initiate_chat"]:
                results["recommendations"].append("AutoGen version might be incompatible. Try: pip install pyautogen==0.2.32")
            
            if results["can_create_assistant"] and results["can_create_user_proxy"]:
                results["recommendations"].append("Setup looks good! You can proceed with creating conversations.")
        
        except Exception as e:
            results["errors"].append(f"Setup test failed: {e}")
            results["recommendations"].append("Check AutoGen installation: pip install pyautogen")
        
        return results 