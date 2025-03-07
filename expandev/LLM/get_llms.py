"""
Módulo auxiliar para criar instâncias de LLM a partir de um nome de modelo
e temperatura, mantendo compatibilidade com código existente.
"""

import os
from dotenv import load_dotenv, find_dotenv
from expandev.LLM.LLM_definition import LLM
from expandev.LLM.langchain_llm_adapter import create_langchain_compatible_llm

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())

# Obter chaves de API do ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Conjuntos de modelos
OPENAI_MODELS = {
    "gpt-4", 
    "gpt-4o", 
    "gpt-4o-mini", 
    "gpt-4-turbo", 
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4o"
}

ANTHROPIC_MODELS = {
    "claude-3-opus-20240229", 
    "claude-3-sonnet-20240229", 
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet",
    "claude-3-5-haiku-20241022"
}

DEEPSEEK_MODELS = {
    "deepseek-chat",
    "deepseek-reasoner"
}

def get_llm(model: str, temperature: float):
    """
    Cria uma instância de LLM com base no nome do modelo e temperatura.
    
    Esta função é um wrapper para manter a compatibilidade com código existente
    que usa a função get_llm() para obter um modelo de linguagem.
    
    Args:
        model (str): Nome do modelo de linguagem
        temperature (float): Temperatura para geração de texto (0.0-1.0)
        
    Returns:
        LangChainAdapter: Um adaptador compatível com LangChain
        
    Raises:
        ValueError: Se o modelo não for reconhecido
    """
    # Determinar a chave API e URL base com base no modelo
    api_key = None
    base_url = None
    
    if model in OPENAI_MODELS:
        api_key = OPENAI_API_KEY
    elif model in ANTHROPIC_MODELS:
        api_key = ANTHROPIC_API_KEY
    elif model in DEEPSEEK_MODELS:
        api_key = DEEPSEEK_API_KEY
        base_url = "https://api.deepseek.com/v1"
    else:
        raise ValueError(f"Modelo '{model}' não reconhecido")
    
    # Criar instância LLM
    llm = LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url
    )
    
    # Envolver em um adaptador compatível com LangChain
    return create_langchain_compatible_llm(llm)