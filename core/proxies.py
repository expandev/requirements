from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import json
import logging
import os
import warnings
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union, Type
from pydantic import BaseModel, Field, field_validator, model_validator
from langchain_core.messages import AIMessage, BaseMessage
from core.enums.models import Models, MODEL_TO_PROVIDER, LLM_CONTEXT_WINDOW_SIZES, DEFAULT_CONTEXT_WINDOW_SIZE, CONTEXT_WINDOW_USAGE_RATIO
from agents.definition.atena import SystemState
    
"""
AgentProxy Module (AgentDefinition) - Defines and manages agent profiles in the Atena system.

This module provides the structure to define agents and their attributes,
including roles, objectives, and operational contexts.
"""
class AgentProxy(BaseModel, ABC):
    def __init__(self, demand_id: int, task):
        """
        Initializes the agent system with all necessary components.
        
        The initialization process follows this order:
        1. Sets the initial state to ACTIVE
        2. Loads environment variables
        3. Sets up the database connection
        4. Initializes workflow data using sp_start_conversation
        5. Configures system components
        6. Creates agent and task instances
        7. Starts the processing system
        
        Args:
            demand_id: ID of the demand to be processed
                    
        Raises:
            ValueError: If demand data cannot be retrieved
            RuntimeError: If any component fails to initialize
        """
        self.state = SystemState.ACTIVE
        self._setup_environment()
        self._setup_database()
        
        # Initialize agent and task with default values first
        self.agent = AgentProxy(knowledge_area="Default")
        self.task = task(demand="Default")
        
        self._initialize_conversation(demand_id)
        
        # Update agent and task with proper data from the database
        self.agent = AgentProxy(knowledge_area=self.knowledge_area)
        self.task = task(demand=self.demand)
        
        # Initialize remaining components
        self._initialize_components()
        self._initialize_system()

    @abstractmethod
    def _setup_environment(self) -> None:
        """
        Configures the system environment.
        
        - Loads environment variables from the .env file
        - Sets the system user
        
        This method uses dotenv to safely load sensitive configurations.
        """
        pass

    @abstractmethod
    def _setup_database(self) -> None:
        """
        Initializes and sets up the database connection.
        
        Establishes a connection to the database, which will be used
        to persist workflow and conversation history information.
        
        Raises:
            Exception: If the database connection fails
        """
        pass
    
    @abstractmethod
    def _initialize_conversation(self, demand_id: int) -> None:
        pass
    
    @abstractmethod
    def _extract_knowledge_area(self, knowledge_area_json) -> str:
        """
        Extracts the knowledge area from the provided JSON, handling different possible formats.
        
        Args:
            knowledge_area_json: Knowledge area data in various possible formats
            
        Returns:
            str: Extracted knowledge area as text
        """
        pass

    @abstractmethod
    def _initialize_components(self) -> None:
        """
        Initializes the main system components.
        
        This method configures:
        1. Message list and token counters
        2. Atena agent with the specific knowledge area
        3. Objective understanding task with the demand
        
        Raises:
            Exception: If any component fails to initialize
        """
        pass
        
    @abstractmethod
    def _initialize_system(self) -> None:
        """
        Initializes the natural language processing system.

        This method configures:
        1. Task definitions
        2. LLM configuration from the markdown file
        3. System prompt
        4. Language model (LLMProxy)

        Raises:
            RuntimeError: If LLM or components fail to initialize
        """
        pass
    
    @abstractmethod
    def _format_history(self) -> str:
        """
        Formats the message history for storage.
        
        The method:
        1. Processes each message in history
        2. Identifies the type (user or Atena)
        3. Properly formats them
        4. Joins all messages with a separator
        
        Returns:
            str: Formatted history ready for storage
            
        Note:
            Ignores the first message (system prompt)
        """
        pass
    
    @abstractmethod
    def save_history(self) -> None:
        """
        Saves the complete conversation history to the database using sp_end_conversation.
        
        The saving process:
        1. Formats the message history
        2. Calls the stored procedure sp_end_conversation with the iteration_id
        
        This method is useful for:
        - Later analysis of conversations
        - System auditing
        - Process improvements
        
        Raises:
            Exception: If an error occurs during saving
        """
        pass

    @abstractmethod
    def process_message(self, user_input: str) -> str:
        """
        Processes a user message and generates a response.
        
        The processing includes:
        1. Validating system state
        2. Adding the message to history
        3. Invoking the language model
        4. Updating counters and history
        
        Args:
            user_input: User message text
            
        Returns:
            str: Generated system response
            
        Raises:
            RuntimeError: If the system is not active
            Exception: If an error occurs during processing
        """
        pass
    
    @abstractmethod
    def _update_token_counters(self, response, input_token_count: int) -> None:
        """
        Updates token counters based on the model's response.
        
        This function has been simplified as litellm handles token counting differently.
        We're using a basic word-based estimation in the process_message method instead.
        
        Args:
            response: The complete model response
            input_token_count: Initial input token estimation
        """
        # Método simplificado já que a contagem de tokens é feita diretamente no process_message
        pass
    
    @abstractmethod
    def start_conversation(self) -> None:
        """
        Starts a new conversation with the system.
        
        The method:
        1. Sets the system state to ACTIVE
        2. Initializes the message history
        3. Displays the system prompt
        
        Raises:
            Exception: If an error occurs during initialization
        """
        pass

"""
Defines configurations and parameters for a language model.

This class is responsible for:
- Storing information about the model to be used
- Managing generation parameters (temperature, max_tokens, etc.)
- Validating model configurations
- Making calls to language models via their native APIs
"""
class LLMProxy(BaseModel, ABC):
    
    # Class fields
    model: str = Field(
        description="Name of the language model to be used"
    )
    
    temperature: float = Field(
        default=0.7,
        description="Generation temperature (0.0-1.0)"
    )
    
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum response tokens"
    )
    
    provider: Optional[str] = Field(
        default=None,
        description="Provider of the model (determined automatically)"
    )
    
    timeout: Optional[float] = Field(
        default=None,
        description="Timeout for API calls in seconds"
    )
    
    base_url: Optional[str] = Field(
        default=None,
        description="Custom API base URL"
    )
    
    api_key: Optional[str] = Field(
        default=None,
        description="Custom API key"
    )
    
    api_version: Optional[str] = Field(
        default=None,
        description="API version"
    )
    
    # Additional generation parameters
    top_p: Optional[float] = Field(
        default=None,
        description="Nucleus sampling probability"
    )
    
    presence_penalty: Optional[float] = Field(
        default=None,
        description="Presence penalty to reduce repetitions"
    )
    
    frequency_penalty: Optional[float] = Field(
        default=None,
        description="Frequency penalty to reduce repetitions"
    )
    
    stop: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Sequences to indicate where the model should stop generating"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for deterministic sampling"
    )
    
    # Internal settings
    _client = None
    _normalized_stop: List[str] = []
    
    # Validators
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validates the LLM temperature."""
        if v < 0.0 or v > 1.0:
            raise ValueError('Temperature must be between 0.0 and 1.0')
        return v
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v: Optional[int]) -> Optional[int]:
        """Validates the token limit, if provided."""
        if v is not None and v <= 0:
            raise ValueError('The maximum number of tokens must be greater than zero')
        return v
    
    @field_validator('top_p')
    @classmethod
    def validate_top_p(cls, v: Optional[float]) -> Optional[float]:
        """Validates the top_p parameter, if provided."""
        if v is not None and (v <= 0.0 or v > 1.0):
            raise ValueError('Top-p value must be between 0.0 and 1.0')
        return v
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validates if the model is recognized."""
        v = v.strip()  # Removes extra spaces
        if v not in MODEL_TO_PROVIDER:
            raise ValueError(f"Model '{v}' not recognized. Choose a valid model from OpenAI, Anthropic, or DeepSeek")
        return v
    
    @model_validator(mode='after')
    @abstractmethod
    def set_provider_and_normalize(self) -> 'LLMProxy': #TODO
        """Sets the provider based on the model and normalizes parameters."""
        # Set provider
        self.provider = MODEL_TO_PROVIDER.get(self.model)
        
        # Set base URL if not provided
        if self.provider == "deepseek" and not self.base_url:
            self.base_url = "https://api.deepseek.com/v1"
        
        # Normalize stop sequences
        if self.stop is None:
            self._normalized_stop = []
        elif isinstance(self.stop, str):
            self._normalized_stop = [self.stop]
        else:
            self._normalized_stop = self.stop
            
        # Initialize client
        self._initialize_client()
            
        return self
    
    @abstractmethod #TODO
    def _initialize_client(self) -> None:
        """Initializes the appropriate client based on the provider."""
        if self._client is not None:
            return  # Client already initialized
            
        try:
            if self.provider == "openai":
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key or os.environ.get("OPENAI_API_KEY"),
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
                
            elif self.provider == "anthropic":
                from anthropic import Anthropic
                self._client = Anthropic(
                    api_key=self.api_key or os.environ.get("ANTHROPIC_API_KEY"),
                )
                
            elif self.provider == "deepseek":
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key or os.environ.get("DEEPSEEK_API_KEY"),
                    base_url=self.base_url or "https://api.deepseek.com/v1",
                    timeout=self.timeout,
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize client for {self.provider}: {str(e)}")
            raise
    
    def get_context_window_size(self) -> int:
        """
        Returns the context window size, using 75% of the maximum to avoid
        cutting off messages mid-thread.
        """
        # Look for a matching context window size for the model
        for key, value in LLM_CONTEXT_WINDOW_SIZES.items():
            if self.model.startswith(key):
                return int(value * CONTEXT_WINDOW_USAGE_RATIO)
                
        # If no specific size is found, use the default
        return int(DEFAULT_CONTEXT_WINDOW_SIZE * CONTEXT_WINDOW_USAGE_RATIO)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the configuration to a dictionary."""
        return {k: v for k, v in self.model_dump().items() if v is not None and not k.startswith('_')}
    
    @abstractmethod #TODO
    def _prepare_openai_call(self, messages: List[Dict[str, str]], tools=None):
        """Prepares parameters for OpenAI API call."""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            params["max_tokens"] = self.max_tokens
        if self.top_p:
            params["top_p"] = self.top_p
        if self.presence_penalty:
            params["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty:
            params["frequency_penalty"] = self.frequency_penalty
        if self._normalized_stop:
            params["stop"] = self._normalized_stop
        if self.seed:
            params["seed"] = self.seed
        if tools:
            params["tools"] = tools
            
        return params
    
    @abstractmethod #TODO
    def _prepare_anthropic_call(self, messages):
        """Prepares parameters for Anthropic API call."""
        # Convert messages to Anthropic format
        # Anthropic expects system message separately and uses 'user' and 'assistant' roles
        system_message = None
        formatted_messages = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_message = content
            elif role == "user":
                formatted_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                formatted_messages.append({"role": "assistant", "content": content})
        
        # For Claude models, the maximum output is typically a fraction of the context window
        # Most Claude models allow around 4k-8k tokens of output
        # So we use a more conservative value for max_tokens
        
        # Determine the appropriate value for max_tokens
        if self.max_tokens is not None:
            # If the user specified a value, use that
            max_tokens = self.max_tokens
        else:
            # Otherwise, use a reasonable value based on the model
            # To avoid trying to use the entire context window as max_tokens,
            # we use a more conservative calculation (about 1/5 of the context window)
            context_size = 0
            for key, value in LLM_CONTEXT_WINDOW_SIZES.items():
                if self.model.startswith(key):
                    context_size = value
                    break
            
            if context_size == 0:
                context_size = DEFAULT_CONTEXT_WINDOW_SIZE
                
            # Use 1/5 of the window as a reasonable value for output tokens
            # but with an upper limit of 8192, which is safe for most models
            max_tokens = min(int(context_size * 0.2), 8192)
        
        params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
        }
        
        if system_message:
            params["system"] = system_message
            
        if self.top_p:
            params["top_p"] = self.top_p
        if self._normalized_stop:
            params["stop_sequences"] = self._normalized_stop
            
        return params
    
    @abstractmethod #TODO
    def _prepare_deepseek_call(self, messages: List[Dict[str, str]], tools=None):
        """Prepares parameters for DeepSeek API call (via OpenAI format)."""
        # DeepSeek uses OpenAI format
        return self._prepare_openai_call(messages, tools)
    
    #TODO
    def call(
        self, 
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        High-level LLM call method that:
          1) Accepts either a string or a list of messages
          2) Converts string input to the required message format
          3) Calls the appropriate provider API
          4) Handles function/tool calls if supported
          5) Returns the final text response

        Parameters:
        - messages (Union[str, List[Dict[str, str]]]): The input messages for the LLM.
          - If a string is provided, it will be converted into a message list with a single entry.
          - If a list of dictionaries is provided, each dictionary should have 'role' and 'content' keys.
        - tools (Optional[List[dict]]): A list of tool schemas for function calling.
        - available_functions (Optional[Dict[str, Any]]): A dictionary mapping function names to actual Python functions.

        Returns:
        - str: The final text response from the LLM or the result of a tool function call.
        """
        # Ensure client is initialized
        if self._client is None:
            self._initialize_client()
            
        # Convert string to message format if needed
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        try: #TODO
            # Make the appropriate API call based on provider
            if self.provider == "openai":
                return self._call_openai(messages, tools, available_functions)
                
            elif self.provider == "anthropic":
                return self._call_anthropic(messages)
                
            elif self.provider == "deepseek":
                return self._call_deepseek(messages, tools, available_functions)
                
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error calling {self.provider} API: {str(e)}")
            raise
    
    @abstractmethod #TODO
    def _call_model(self, messages, tools=None, available_functions=None):
        pass

    #TODO
    def _call_openai(self, messages, tools=None, available_functions=None):
        """Makes a call to the OpenAI API."""
        params = self._prepare_openai_call(messages, tools)
        
        response = self._client.chat.completions.create(**params)
        
        # Check for tool calls
        if tools and available_functions and hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            
            if function_name in available_functions:
                try:
                    function_args = json.loads(tool_call.function.arguments)
                    fn = available_functions[function_name]
                    result = fn(**function_args)
                    return result
                except Exception as e:
                    logger.error(f"Error executing function '{function_name}': {e}")
        
        # Return text response
        return response.choices[0].message.content or ""
    
    #TODO
    def _call_anthropic(self, messages):
        """Makes a call to the Anthropic API."""
        params = self._prepare_anthropic_call(messages)
        
        try:
            response = self._client.messages.create(**params)
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error in Anthropic API call: {str(e)}")
            # More detailed error information for debugging
            logger.error(f"Params used: {json.dumps({k: str(v) if k != 'messages' else '[messages]' for k, v in params.items()})}")
            raise
    
    #TODO
    def _call_deepseek(self, messages, tools=None, available_functions=None):
        """Makes a call to the DeepSeek API (via OpenAI format)."""
        # DeepSeek uses OpenAI format
        return self._call_openai(messages, tools, available_functions)
    
    def format(self) -> str:
        """Formats the LLM configuration into a structured string."""
        template = """
            ### LLM CONFIGURATION ###
            - Model: {model} (Provider: {provider})
            - Temperature: {temperature}{max_tokens_str}
        """
        max_tokens_str = f"\n- Max Tokens: {self.max_tokens}" if self.max_tokens else ""
        
        return template.format(
            model=self.model,
            provider=self.provider,
            temperature=self.temperature,
            max_tokens_str=max_tokens_str
        )
    
    @abstractmethod #TODO
    def supports_function_calling(self) -> bool:
        """Checks if the model supports function calling."""
        # Only OpenAI and some DeepSeek models support function calling
        return self.provider in ["openai", "deepseek"]
    
    def supports_stop_words(self) -> bool:
        """Checks if the model supports stop words."""
        # All supported providers support stop words
        return True
    
    def __str__(self) -> str:
        """String representation of the LLM."""
        return f"LLMProxy({self.model}, temp={self.temperature})"

"""
TaskProxy Module - Defines and manages task definitions in the Atena system.
"""
class TaskProxy(BaseModel):
    """
    Defines a task to be performed by an agent.
    """
    
    # Mandatory fields
    problems_to_solve: List[str] = Field(
        description="List of problems that the task should solve"
    )
    
    main_objective: str = Field(
        description="Main objective of the task"
    )
    
    expected_outcomes: str = Field(
        description="Expected outcomes and their rules"
    )
    
    language: str = Field(
        description="Language for execution"
    )
    
    expected_output: str = Field(
        description="Expected output format"
    )
    
    # Optional fields
    out_of_scope: List[str] = Field(
        default_factory=list,
        description="Items out of scope"
    )
    
    output_json: Optional[Type[BaseModel]] = Field(
        default=None,
        description="Model for structured output"
    )

    # Validators
    @field_validator('main_objective', 'expected_outcomes', 'language', 'expected_output')
    @classmethod
    def validate_non_empty(cls, v: str, field: str) -> str:
        """Validates that the field is not empty."""
        if not v or not v.strip():
            raise ValueError(f'{field.name} cannot be empty')
        return v.strip()

    def _format_json_schema(self) -> str:
        """Formats the JSON schema for display."""
        return (
            self.output_json.model_json_schema(indent=2)
            if self.output_json
            else "No JSON schema defined"
        )

    def format(self) -> str:
        """Formats the task definition into a structured string."""
        template = """
            ### TASK DEFINITION ###

            PROBLEMS TO SOLVE:
            {problems}

            MAIN OBJECTIVE:
            {main_objective}

            EXPECTED OUTCOMES:
            {expected_outcomes}

            LANGUAGE: {language}
            EXPECTED OUTPUT: {expected_output}

            {optional_fields}
        """
        # Formats optional fields if they exist
        optional_fields = []
        
        if self.out_of_scope:
            optional_fields.append("OUT OF SCOPE:\n" + 
                "\n".join(f"- {item}" for item in self.out_of_scope))
            
        if self.output_json:
            optional_fields.append("OUTPUT JSON SCHEMA:\n" + self._format_json_schema())
            
        return template.format(
            problems="\n".join(f"- {p}" for p in self.problems_to_solve),
            main_objective=self.main_objective,
            expected_outcomes=self.expected_outcomes,
            language=self.language,
            expected_output=self.expected_output,
            optional_fields="\n\n".join(optional_fields) if optional_fields else ""
        )

    def is_complete(self) -> bool:
        """Checks if the task has all mandatory fields filled."""
        return bool(
            self.problems_to_solve and
            self.main_objective and
            self.expected_outcomes and
            self.language and
            self.expected_output
        )

