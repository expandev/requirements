from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from core.proxies import AgentProxy
from core.proxies import TaskProxy
from core.proxies import LLMProxy

"""
SystemPromptBase Module - Integration of agent profiles with task definitions.

This module combines agent and task definitions to create a complete 
system prompt.
"""
class SystemPromptBase(BaseModel):
    """
    Combines agent definition, task definition, and LLM configuration to create a complete system prompt.
    
    This class is responsible for:
    - Validating the integration between agent and task
    - Ensuring completeness of components
    - Formatting the final system prompt
    - Managing language model configurations
    
    Attributes:
        agent_profile: Definition of the agent with role, objectives, and context
        task_definition: Task definition with objectives and expected outputs
        llm_config: Language model configuration (optional)
    """
    
    agent_profile: AgentProxy = Field(
        description="Agent definition containing role, objectives, and background"
    )
    
    task_definition: TaskProxy = Field(
        description="Task definition containing objectives and expected outputs"
    )
    
    llm_config: Optional[LLMProxy] = Field(
        default=None,
        description="Language model configuration (optional)"
    )
    
    @model_validator(mode='after')
    def ensure_llm_config(self) -> 'SystemPromptBase':
        """
        Ensures that an LLM configuration exists, using a default value if necessary.
        """
        if self.llm_config is None:
            # Default value for Claude Haiku
            self.llm_config = LLMProxy(
                model="claude-3-5-haiku-20241022",
                temperature=0.5
            )
        return self
    
    def validate_components(self) -> bool:
        """
        Validates that all components (agent and task) are complete.
        
        Returns:
            bool: True if all components are valid and complete
        """
        return (
            self.agent_profile is not None and 
            self.task_definition is not None and
            self.agent_profile.is_complete() and
            self.task_definition.is_complete()
        )
    
    def format(self) -> str:
        """
        Formats the complete system prompt by combining agent, task, and LLM information.
        
        Returns:
            str: Formatted system prompt
            
        Raises:
            ValueError: If components are missing or incomplete
        """
        if not self.validate_components():
            raise ValueError("Agent profile or task definition is incomplete")
        
        llm_section = ""
        if self.llm_config:
            # Using a simpler format for the LLM configuration
            llm_section = f"""
### LLM CONFIGURATION ###
- Model: {self.llm_config.model}
- Temperature: {self.llm_config.temperature}"""
            
            if self.llm_config.max_tokens:
                llm_section += f"\n- Max Tokens: {self.llm_config.max_tokens}"
            
        return f"""### SYSTEM PROMPT ###

{self.agent_profile.format()}

{self.task_definition.format()}{llm_section}

### END SYSTEM PROMPT ###"""
    
    @property
    def model(self) -> str:
        """
        Returns the name of the configured language model.
        
        Returns:
            str: Language model name
        """
        if not self.llm_config:
            raise ValueError("LLM configuration is not set")
        return self.llm_config.model
    
    @property
    def temperature(self) -> float:
        """
        Returns the configured temperature for the language model.
        
        Returns:
            float: Temperature value
        """
        if not self.llm_config:
            return 0.5
        return self.llm_config.temperature
    
    @property
    def max_tokens(self) -> Optional[int]:
        """
        Returns the token limit if configured.
        
        Returns:
            Optional[int]: Token limit or None if not configured
        """
        if not self.llm_config:
            return None
        return self.llm_config.max_tokens
    
    def execute(self, user_message: str) -> str:
        """
        Executes the system prompt by calling the LLM with the combined context.
        
        This method:
        1. Formats the system prompt
        2. Combines it with the user message
        3. Makes the call to the LLM
        4. Returns the response
        
        Args:
            user_message: The user's input message
            
        Returns:
            str: The response from the LLM
        """
        if not self.llm_config:
            raise ValueError("LLM configuration is not set")
            
        system_content = self.format()
        
        # Format messages for the LLM call
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM with the formatted messages
        return self.llm_config.call(messages)
