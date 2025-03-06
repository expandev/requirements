from core.adapters.llm_adapters import LLMAdapter
from core.adapters.prompt_adapters import BasePromptStrategy
from core.proxies import AgentProxy

class RequirementAgent(AgentProxy):
    def __init__(self):
        pass

    def configurar(self, llm_adapter: LLMAdapter, prompt_strategy: BasePromptStrategy, knowledge_base):
        # Carrega do MD
        self.llm = llm_adapter
        self.prompt_strategy = prompt_strategy
        self.kb = knowledge_base
    
    def execute_task(self, input_data):
        #prompt = self.prompt_strategy.generate_prompt(input_data)
        #response = self.llm.call_model(prompt)
        #self._validate(response)
        return "Hello World!"
        
    def _validate(self, output):
        # Lógica de autocorreção
        if not self._check_quality(output):
            self._correct_errors(output)
	
    def _check_quality(output):
        return all([
            #self._check_completeness(agent_output),
            #self._check_ambiguity(agent_output),
            #self._check_consistency(agent_output)
        ])