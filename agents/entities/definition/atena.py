from core.proxies import LLMProxy
from core.adapters.prompt_adapters import BasePromptStrategy
from core.models import AgentModel
from pydantic import Field
from typing import List, Optional, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from core.adapters.prompt_adapters import SystemPromptBase
from core.MD_reader.md_config_expandev import ExpandevConfigProvider

description_file_path = 'agent_description/definition/Expandev_Atena_Agent_Construction_Form.md'

class AtenaEntity(AgentModel):
    """
    Atena's agent implementation.
    
    This agent is configured using the Expandev MD format and includes
    specialized fields for defining its behavior and capabilities.
    """
    knowledge_area: str = Field(
        description="Specific area of knowledge for the agent",
        default=""
    )
    
    def __init__(self, knowledge_area: str):
        # Load configuration
        config = ExpandevConfigProvider(description_file_path)
        
        # Initialize parent class with named arguments
        super().__init__(
            # Basic Info
            name                    = config.agent_name,
            role                    = config.role,
            field_of_work           = config.field_of_work,
            expertise_level         = config.expertise_level.format(knowledge_area=knowledge_area),
            professional_background = config.professional_background,
            technical_skills        = config.technical_skills,
            resources               = config.resources,
            communication_approach  = config.communication_approach,
            response_style          = config.response_style,
            proactivity_level       = config.proactivity_level,
            autonomy                = config.autonomy,
            #llm                     = config.llm_config,
            #prompt_strategy         = config.prompt_strategy,
        )