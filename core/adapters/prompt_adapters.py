from abc import ABC, abstractmethod


class BasePromptStrategy(ABC):
    @abstractmethod
    def generate_prompt(self, context):
        raise NotImplementedError("Subclasses devem implementar este método")

class DefaultPromptStrategy(BasePromptStrategy):
    def generate_prompt(self, context):
        return "Prompt padrão para agente."

class CustomPromptStrategy(BasePromptStrategy):
    def __init__(self, role, instructions):
        self.custom_role = role
        self.custom_instructions = instructions

    def generate_prompt(self, context):
        return f"Como {self.custom_role}, {self.custom_instructions}"