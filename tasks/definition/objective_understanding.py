from expandev.system_prompts.task_definition import TaskDefinition
from expandev.MD_reader.md_config_expandev import ExpandevConfigProvider
from pydantic import Field

class ObjectiveUnderstanding(TaskDefinition):
    """
    Task definition for understanding project objectives and requirements.
    """
    demand: str = Field(
        description="Specific demand for the agent",
        default=""
    )

    # Initialization of contents read from MD
    def __init__(self, demand: str, task_key=1, knowledge_base_path='knowledge/definition'):
        """
        Initialize the ObjectiveUnderstanding task.
        
        Args:
            demand: The user's specific demand
            task_key: Task number to be used (1, 2, 3, etc.)
            knowledge_base_path: Path to the knowledge base files
        """
        # Load markdown configuration with the configurable path for the knowledge base
        config = ExpandevConfigProvider(
            'docs/Agent_Construction/Expandev_Atena_Agent_Construction_Form.md',
            knowledge_base_path=knowledge_base_path
        )
        
        # Get the specified task by number
        task_key = f"Task{task_key}"
        
        # Check if the task exists
        if task_key not in config.tasks:
            available_tasks = ", ".join(config.tasks.keys())
            raise ValueError(f"Task {task_key} not found. Available tasks: {available_tasks}")
            
        task_config = config.tasks[task_key]
        
        # Get the formatted description (with placeholder substitutions)
        formatted_outcomes = task_config.get_formatted_description()
        
        # Initialize the parent class with mandatory fields
        super().__init__(
            problems_to_solve=config.problems,
            main_objective=task_config.main_objective,
            expected_outcomes=formatted_outcomes,
            language=task_config.language,
            expected_output=task_config.expected_output
        )
        
        self.demand = demand
