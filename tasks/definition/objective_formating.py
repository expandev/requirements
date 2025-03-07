import yaml
from crewai import Task
from typing import List, Optional
from utils.md_config import MDConfigProvider, create_pydantic_models

# Load the configuration
config = MDConfigProvider('docs/Agent_Construction/Atena_CrewAI_Agent_Construction_Form.md')

task2_config = config.tasks.get('Task2')
if not task2_config:
    raise ValueError("Task2 configuration not found in MD file")

# PhraseAnalysis = create_pydantic_models(task2_config.output_json)

class ObjectiveFormating(Task):
    def __init__(self, phrase: str, history: Optional[List[str]] = None, agent=None):

        task2_description = task2_config.description.format(
            history=history,
            phrase=phrase,
        )

        super().__init__(
            name=task2_config.name,
            description=task2_description,
            expected_output=task2_config.expected_output,
#            output_json=PhraseAnalysis,
#            agent=agent
        )