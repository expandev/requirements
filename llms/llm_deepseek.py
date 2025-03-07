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
from core.enums.system import SystemState
from core.proxies.llm_proxy import LLMProxy

"""
Defines configurations and parameters for a OpenAI LLMs.
"""
class OpenAILLM(LLMProxy):

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
    
    @abstractmethod #TODO
    def supports_function_calling(self) -> bool:
        """Checks if the model supports function calling."""
        # Only OpenAI and some DeepSeek models support function calling
        return self.provider in ["openai", "deepseek"]

    @abstractmethod
    def _prepare_model_call(self, messages: List[Dict[str, str]], tools=None):
        """Prepares parameters for LLM call."""
        pass
    
    @abstractmethod
    def set_provider(self) -> None:
        # Set provider
        self.provider = MODEL_TO_PROVIDER.get(self.model)
        
        # Set base URL if not provided
        if self.provider == "deepseek" and not self.base_url:
            self.base_url = "https://api.deepseek.com/v1"
        pass