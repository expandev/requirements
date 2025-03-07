from expandev.system_prompts.agent_definition import AgentDefinition
from expandev.MD_reader.md_config_expandev import ExpandevConfigProvider
from pydantic import Field

class AtenaAgent(AgentDefinition):
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
        config = ExpandevConfigProvider('docs/Agent_Construction/Expandev_Atena_Agent_Construction_Form.md')
        
        # Initialize parent class with named arguments
        super().__init__(
            # Basic Info
            name=config.agent_name,
            role=config.role,
            field_of_work=config.field_of_work,
            expertise_level=config.expertise_level.format(knowledge_area=knowledge_area),
            professional_background=config.professional_background,
            technical_skills=config.technical_skills,
            resources=config.resources,
            communication_approach=config.communication_approach,
            response_style=config.response_style,
            proactivity_level=config.proactivity_level,
            autonomy=config.autonomy
        )