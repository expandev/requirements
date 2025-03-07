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
from core.proxies.task_proxy import TaskProxy
from core.models import AgentModel

"""
AgentProxy Module (AgentDefinition) - Defines and manages agent profiles in the Atena system.

This module provides the structure to define agents and their attributes,
including roles, objectives, and operational contexts.
"""
class AgentProxy(AgentModel, ABC):
    

    def inicialize(self, demand_id: int, task: TaskProxy):
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
        self.agent = AgentModel(knowledge_area="Default")
        self.task = task(demand="Default")
        
        self._initialize_conversation(demand_id)
        
        # Update agent and task with proper data from the database
        self.agent = AgentModel(knowledge_area=self.knowledge_area)
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
