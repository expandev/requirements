from abc import ABC, abstractmethod

""" Interface para implementação de adaptadores de LLMs """
class LLMAdapter(ABC):
    @abstractmethod
    def call_model(self, prompt):
        pass
    # ...

""" Exemplo Implementação do GPT"""
class GPT4Adapter(LLMAdapter):
    def call_model(self, prompt):
        pass
        # return openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}]
        # )
# ...