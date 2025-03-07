import json
import logging
import os
import warnings
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from langchain_core.messages import AIMessage, BaseMessage
from core.proxies.llm_proxy import LLMProxy

logger = logging.getLogger(__name__)

"""
Adaptador para que a classe LLM seja compatível com interfaces do LangChain.

Este módulo fornece uma classe invólucro (wrapper) que permite que nossa implementação 
de LLM seja usada de forma semelhante a um LLM do LangChain.
"""
class LLMAdapter(LLMProxy):
    """
    Adaptador que permite usar nossa classe LLM com a interface semelhante ao LangChain.
    
    Esta classe envolve uma instância de LLM e fornece métodos compatíveis
    com diferentes interfaces, convertendo entre formatos de mensagem conforme necessário.
    """
    
    def __init__(self, llm: LLMProxy):
        """
        Inicializa o adaptador com uma instância de LLM.
        
        Args:
            llm (LLMProxy): A instância de LLM a ser adaptada
        """
        self.llm = llm
    
    def invoke(self, messages: List[Union[BaseMessage, Dict[str, str]]]) -> AIMessage:
        """
        Invoca o LLM com mensagens no formato LangChain e retorna uma AIMessage.
        
        Args:
            messages: Lista de mensagens (objetos LangChain ou dicionários)
            
        Returns:
            AIMessage: Mensagem de resposta no formato LangChain
        """
        # Converter mensagens para o formato dict que nosso LLM espera
        formatted_messages = []
        
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                # Já está no formato correto
                formatted_messages.append(msg)
            elif hasattr(msg, "type") and hasattr(msg, "content"):
                # É um objeto BaseMessage do LangChain
                role = self._convert_message_type_to_role(msg)
                formatted_messages.append({
                    "role": role,
                    "content": msg.content
                })
            else:
                # Formato desconhecido, tentar extrair o máximo de informações
                content = getattr(msg, "content", str(msg))
                formatted_messages.append({
                    "role": "user",  # Fallback para user
                    "content": content
                })
        
        # Chamar o LLM
        response_text = self.llm.call(formatted_messages)
        
        # Criar e retornar uma AIMessage
        return AIMessage(content=response_text)
    
    def call(self, messages, **kwargs):
        """
        Método de compatibilidade para código que chama 'call' em vez de 'invoke'.
        Este método simplesmente encaminha para o método invoke.
        
        Args:
            messages: Mensagens para enviar ao LLM
            **kwargs: Parâmetros adicionais (ignorados para compatibilidade)
            
        Returns:
            AIMessage: Resposta do LLM
        """
        return self.invoke(messages)
    
    def _convert_message_type_to_role(self, message) -> str:
        """
        Converte o tipo de mensagem para o role usado no nosso formato.
        
        Args:
            message: Mensagem (pode ser BaseMessage ou outro formato)
            
        Returns:
            str: Role ('system', 'user', ou 'assistant')
        """
        # Se for um dicionário com 'role', use-o diretamente
        if isinstance(message, dict) and "role" in message:
            return message["role"]
            
        # Se tiver atributo 'type'
        if hasattr(message, "type"):
            message_type = message.type
            
            if message_type == "system":
                return "system"
            elif message_type == "human":
                return "user"
            elif message_type == "ai":
                return "assistant"
                
        # Fallback
        return "user"


# TODO -- aonde vai isso?? 
def create_langchain_compatible_llm(llm: LLMProxy) -> LLMAdapter:
    """
    Cria um adaptador compatível com LangChain para nossa classe LLM.
    
    Args:
        llm (LLMProxy): A instância de LLM a ser adaptada
        
    Returns:
        LLMAdapter: O adaptador compatível com LangChain
    """
    return LLMAdapter(llm)
