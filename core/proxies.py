from abc import ABC, abstractmethod

class AgentProxy(ABC):
    def __init__(self, agent):
        self._agent = agent

    @abstractmethod
    def execute_task(self, input_data):
        # Aqui podem ser aplicadas verificações e log de acesso
        return self._agent.execute_task(input_data)