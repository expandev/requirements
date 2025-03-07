"""
AtenaSystem - Workflow Processing and AI Interaction System

This module implements the main Atena system, responsible for:
- Managing workflows and their interactions
- Processing messages using LLM (Large Language Model)
- Maintaining conversation history
- Saving results to the database

"""

from typing import List, Optional, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from expandev.system_prompts.system_prompt import SystemPrompt
from agents.definition.atena import AtenaAgent
from tasks.definition.objective_understanding import ObjectiveUnderstanding
from expandev.system_prompts.task_definition import TaskDefinition
from utils.database_conversation import DatabaseConversation
from expandev.MD_reader.md_config_expandev import ExpandevConfigProvider
from dotenv import load_dotenv, find_dotenv
from enum import Enum
import logging
import os
import json

# Logging configuration for event tracking and error handling
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemState(Enum):
    """
    Possible states of the Atena system.
    
    States:
        ACTIVE: System is operational and ready to process messages
        ERROR: System encountered an error and needs to be restarted
        ENDED: System has finished its execution normally
    """
    ACTIVE = "active"
    ERROR = "error"
    ENDED = "ended"

class AtenaSystem:
    """
    The main system of Atena for workflow and interaction processing.
    
    This class manages the entire lifecycle of an interaction with Atena, including:
    - Environment and component initialization
    - System state management
    - Message processing via LLM
    - History storage
    - Database integration
    
    Attributes:
        state (SystemState): Current state of the system
        user (str): Current system user
        database (DatabaseConversation): Database connection
        demand (str): Demand being processed
        knowledge_area (str): Workflow knowledge area
        messages (List[BaseMessage]): Message history
        total_conversation_tokens (int): Total tokens used
        input_tokens (int): Input token counter
        output_tokens (int): Output token counter
        agent (AtenaAgent): Agent responsible for processing
        task (ObjectiveUnderstanding): Current task being executed
        llm (LLM): Language model used for processing
        iteration_id (int): ID of the current iteration
    """
    
    def __init__(self, demand_id: int):
        """
        Initializes the Atena system with all necessary components.
        
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
        self.agent = AtenaAgent(knowledge_area="Default")
        self.task = ObjectiveUnderstanding(demand="Default")
        
        self._initialize_conversation(demand_id)
        
        # Update agent and task with proper data from the database
        self.agent = AtenaAgent(knowledge_area=self.knowledge_area)
        self.task = ObjectiveUnderstanding(demand=self.demand)
        
        # Initialize remaining components
        self._initialize_components()
        self._initialize_system()

    def _setup_environment(self) -> None:
        """
        Configures the system environment.
        
        - Loads environment variables from the .env file
        - Sets the system user
        
        This method uses dotenv to safely load sensitive configurations.
        """
        if not load_dotenv(find_dotenv()):
            logger.warning("No .env file found - using default configurations")
        self.user = os.getenv('USER')

    def _setup_database(self) -> None:
        """
        Initializes and sets up the database connection.
        
        Establishes a connection to the database, which will be used
        to persist workflow and conversation history information.
        
        Raises:
            Exception: If the database connection fails
        """
        try:
            self.database = DatabaseConversation()
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            self.state = SystemState.ERROR
            raise

    def _initialize_conversation(self, demand_id: int) -> None:
        """
        Initializes conversation data by calling sp_start_conversation.
        
        This method:
        1. Sets up task and agent information as JSON
        2. Calls the stored procedure sp_start_conversation
        3. Retrieves demand_config, knowledge_area, and iteration_id
        
        Args:
            demand_id: ID of the demand to be processed
            
        Raises:
            ValueError: If demand data is not found
            RuntimeError: If an error occurs while processing the data
        """
        try:
            # Default task configuration as JSON
            task_config = json.dumps({
                "problems_to_solve": self.task.problems_to_solve,
                "main_objective": self.task.main_objective,
                "expected_outcomes": self.task.expected_outcomes,
                "language": self.task.language,
                "expected_output": self.task.expected_output
            })
            
            # Agent configuration as JSON
            agent_config = json.dumps({
                "name": self.agent.name,
                "role": self.agent.role,
                "field_of_work": self.agent.field_of_work,
                "expertise_level": self.agent.expertise_level,
                "professional_background": self.agent.professional_background,
                "technical_skills": self.agent.technical_skills,
                "resources": self.agent.resources,
                "communication_approach": self.agent.communication_approach,
                "response_style": self.agent.response_style,
                "proactivity_level": self.agent.proactivity_level,
                "autonomy": self.agent.autonomy
            })
            
            # Start conversation in the database
            demand_config_json, knowledge_area_json, self.iteration_id = self.database.startConversation(
                demand_id=demand_id,
                user=self.user,
                task_name="conversation_history",
                task_config=task_config,
                agent_name=self.agent.name,
                agent_config=agent_config
            )
            
            if not demand_config_json or not self.iteration_id:
                raise ValueError(f"Could not start conversation for demand ID {demand_id}")
                
            # Extract data from returned JSONs
            demand_config = json.loads(demand_config_json) if isinstance(demand_config_json, str) else demand_config_json
            self.demand = demand_config.get('description', 'No description available')
            self.knowledge_area = self._extract_knowledge_area(knowledge_area_json)
                
            # Detailed logging for debugging
            logger.info(f"Loaded demand: {self.demand[:50]}...")
            logger.info(f"Loaded knowledge area: {self.knowledge_area}")
            logger.info(f"Conversation started: Iteration ID {self.iteration_id}")
            
        except Exception as e:
            logger.error(f"Error initializing conversation: {e}")
            self.state = SystemState.ERROR
            raise
    
    def _extract_knowledge_area(self, knowledge_area_json) -> str:
        """
        Extracts the knowledge area from the provided JSON, handling different possible formats.
        
        Args:
            knowledge_area_json: Knowledge area data in various possible formats
            
        Returns:
            str: Extracted knowledge area as text
        """
        if not knowledge_area_json:
            return "Unspecified area"
        
        try:
            knowledge_area_data = json.loads(knowledge_area_json) if isinstance(knowledge_area_json, str) else knowledge_area_json
            if isinstance(knowledge_area_data, dict):
                return knowledge_area_data.get('name') or knowledge_area_data.get('area') or str(next(iter(knowledge_area_data)))
            return str(knowledge_area_data)
        except json.JSONDecodeError:
            return knowledge_area_json

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
        try:
            # Initialize data structures for history
            self.messages: List[BaseMessage] = []
            self.total_conversation_tokens: int = 0
            self.input_tokens: int = 0
            self.output_tokens: int = 0
            
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            self.state = SystemState.ERROR
            raise

    def _initialize_system(self) -> None:
        """
        Initializes the natural language processing system.

        This method configures:
        1. Task definitions
        2. LLM configuration from the markdown file
        3. System prompt
        4. Language model (LLM)

        Raises:
            RuntimeError: If LLM or components fail to initialize
        """
        try:
            # Configure task definitions (only mandatory fields)
            task_def = TaskDefinition(
                problems_to_solve=self.task.problems_to_solve,
                main_objective=self.task.main_objective,
                expected_outcomes=self.task.expected_outcomes,
                language=self.task.language,
                expected_output=self.task.expected_output
            )
            
            # Load configurations from the markdown file
            config = ExpandevConfigProvider('docs/Agent_Construction/Expandev_Atena_Agent_Construction_Form.md')
            
            # Extract LLM configurations from the first task
            task1_config = config.tasks.get("Task1", None)
            
            if task1_config and hasattr(task1_config, 'llm_config'):
                # Retrieve the model and temperature from the markdown file
                model_name = task1_config.llm_config.model
                temperature = task1_config.llm_config.temperature
                max_tokens = task1_config.llm_config.max_tokens
                
                logger.info(f"Using LLM configurations from markdown file: model={model_name}, temperature={temperature}")
            else:
                # Default values if not found in the markdown file
                model_name = "claude-3-5-haiku-20241022"
                temperature = 0.5
                max_tokens = None
                
                logger.warning("LLM configurations not found in markdown file. Using default values.")
            
            # Configure LLM with values retrieved from markdown
            # Importar diretamente do nosso módulo
            from expandev.LLM.LLM_definition import LLM
            llm_def = LLM(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Create system prompt
            system_prompt = SystemPrompt(
                agent_profile=self.agent,
                task_definition=task_def,
                llm_config=llm_def
            )
            
            # Initialize processing components
            self.system_message = SystemMessage(content=system_prompt.format())
            
            # Importar o adaptador para LangChain para que podemos usar a interface 'invoke'
            from expandev.LLM.langchain_llm_adapter import create_langchain_compatible_llm
            # Configurar o LLM com nosso adaptador para manter compatibilidade com LangChain
            self.llm = create_langchain_compatible_llm(llm_def)
            
            # Adicionar a mensagem do sistema à lista de mensagens
            self.messages = [self.system_message]
            
            # Count tokens for the system prompt
            system_tokens = len(self.system_message.content.split())  # Simplified estimation
            self.input_tokens += system_tokens
            self.total_conversation_tokens += system_tokens
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.state = SystemState.ERROR
            raise RuntimeError(f"Failed to initialize system: {str(e)}")
        
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
        history_text = []
        for msg in self.messages[1:]:  # Skips system prompt
            content = msg.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            prefix = "User" if isinstance(msg, HumanMessage) else "Atena"
            formatted_msg = f"{prefix}: {content}"
            history_text.append(formatted_msg)
        
        return "\n---\n".join(history_text)

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
        try:
            # Prepare the history
            full_history = self._format_history()
            
            # Finalize the conversation in the database
            success = self.database.endConversation(
                iteration_id=self.iteration_id,
                result=full_history,
                input_token=self.input_tokens,
                output_token=self.output_tokens
            )
            
            if success:
                logger.info(f"Conversation finalized for iteration_id: {self.iteration_id}")
                logger.info(f"Total tokens - Input: {self.input_tokens}, Output: {self.output_tokens}")
                print("\nConversation history successfully saved in the database!")
            else:
                logger.error(f"Failed to finalize conversation for iteration_id: {self.iteration_id}")
                print("\nError saving conversation history in the database!")
            
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            print(f"\nError saving history in the database: {str(e)}")
            raise


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
        if self.state != SystemState.ACTIVE:
            raise RuntimeError("System is not active to process messages")
            
        try:
            # Add user message to history
            user_message = HumanMessage(content=user_input)
            self.messages.append(user_message)
            
            # Estimate input tokens (based on words - approximate)
            input_token_count = len(user_input.split())
            self.input_tokens += input_token_count
            
            # Chamar o LLM usando o método invoke do adaptador LangChain
            response = self.llm.invoke(self.messages)
            
            # A resposta já é um AIMessage, então podemos usá-la diretamente
            self.messages.append(response)
            
            # Extrair o conteúdo texto da resposta
            response_content = response.content
            
            # Fallback para contagem de tokens: estimativa baseada em palavras
            output_token_count = len(response_content.split())
            self.output_tokens += output_token_count
            self.total_conversation_tokens += input_token_count + output_token_count
            
            # Log token count
            logger.info(f"Tokens - Input: {self.input_tokens}, Output: {self.output_tokens}, Total: {self.total_conversation_tokens}")
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.state = SystemState.ERROR
            raise
    
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