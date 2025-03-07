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
    def set_provider_and_normalize(self) -> 'LLMProxy':
        """Sets the provider based on the model and normalizes parameters."""
        
        self.set_provider()

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

    @abstractmethod
    def set_provider(self) -> None:
        # Set provider
        self.provider = MODEL_TO_PROVIDER.get(self.model)
        
        # Set base URL if not provided
        if self.provider == "deepseek" and not self.base_url:
            self.base_url = "https://api.deepseek.com/v1"
        pass
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initializes the appropriate client based on the provider."""
        pass
    
    @abstractmethod
    def _prepare_model_call(self, messages: List[Dict[str, str]], tools=None):
        """Prepares parameters for LLM call."""
        pass

    @abstractmethod
    def call(
        self, 
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
    ) -> str:
        pass

    @abstractmethod
    def supports_function_calling(self) -> bool:
        """Checks if the model supports function calling."""
        pass
    
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

    def supports_stop_words(self) -> bool:
        """Checks if the model supports stop words."""
        # All supported providers support stop words
        return True
    
    def __str__(self) -> str:
        """String representation of the LLM."""
        return f"LLMProxy({self.model}, temp={self.temperature})"
