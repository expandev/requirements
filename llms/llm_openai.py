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
    
    def _initialize_client(self) -> None:
        """Initializes the appropriate client based on the provider."""
        if self._client is not None:
            return  # Client already initialized
            
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=self.base_url,
                timeout=self.timeout,
            )  
        except Exception as e:
            logger.error(f"Failed to initialize client for {self.provider}: {str(e)}")
            raise
    
    def _prepare_model_call(self, messages: List[Dict[str, str]], tools=None):
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

        try: 
            return self._call_model(messages, tools, available_functions)
        except Exception as e:
            logger.error(f"Error calling {self.provider} API: {str(e)}")
            raise
    
    def _call_model(self, messages, tools=None, available_functions=None):
        """Makes a call to the OpenAI API."""
        params = self._prepare_model_call(messages, tools)
        
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
    
    def supports_function_calling(self) -> bool:
        """Checks if the model supports function calling."""
        # Only OpenAI and some DeepSeek models support function calling
        return True

    def set_provider(self) -> None:
        # Set provider
        self.provider = MODEL_TO_PROVIDER.get(self.model)