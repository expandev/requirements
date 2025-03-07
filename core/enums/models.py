from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())

# Obter chaves de API do ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

class Models(Enum):
    # OpenAI Models
    GPT_4               = {"provider": "openai", "model": "gpt-4"}
    GPT_4O              = {"provider": "openai", "model": "gpt-4o"}
    GPT_4O_MINI         = {"provider": "openai", "model": "gpt-4o-mini"}
    GPT_4_TURBO         = {"provider": "openai", "model": "gpt-4-turbo"}
    GPT_3_5_TURBO       = {"provider": "openai", "model": "gpt-3.5-turbo"}
    GPT_3_5_TURBO_16K   = {"provider": "openai", "model": "gpt-3.5-turbo-16k"}
    
    # Anthropic Models
    CLAUDE_3_OPUS_20240229      = {"provider": "anthropic", "model": "claude-3-opus-20240229"}
    CLAUDE_3_SONNET_20240229    = {"provider": "anthropic", "model": "claude-3-sonnet-20240229"}
    CLAUDE_3_HAIKU_20240307     = {"provider": "anthropic", "model": "claude-3-haiku-20240307"}
    CLAUDE_3_5_SONNET           = {"provider": "anthropic", "model": "claude-3-5-sonnet"}
    CLAUDE_3_5_HAIKU_20241022   = {"provider": "anthropic", "model": "claude-3-5-haiku-20241022"}
    
    # DeepSeek Models
    DEEPSEEK_CHAT               = {"provider": "deepseek", "model": "deepseek-chat"}
    DEEPSEEK_REASONER           = {"provider": "deepseek", "model": "deepseek-reasoner"}
    

# Context window sizes for different models
# TODO - Migrar para Enum (core\enums\models.py)
LLM_CONTEXT_WINDOW_SIZES = {
    # openai
    "gpt-4": 8192,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000,
    "gpt-3.5-turbo": 16385,
    "gpt-3.5-turbo-16k": 16385,
    # anthropic
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 180000,
    "claude-3-haiku-20240307": 150000,
    "claude-3-5-sonnet": 200000,
    "claude-3-5-haiku-20241022": 8192,
    
    # deepseek
    "deepseek-chat": 128000,
    "deepseek-reasoner": 128000,
}

DEFAULT_CONTEXT_WINDOW_SIZE = 8192
CONTEXT_WINDOW_USAGE_RATIO = 0.75

# Mapping of models to providers
# TODO - Migrar para Enum (core\enums\models.py)
MODEL_TO_PROVIDER = {
    # OpenAI models
    "gpt-4": "openai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4-turbo": "openai",
    "gpt-3.5-turbo": "openai",
    "gpt-3.5-turbo-16k": "openai",
    
    # Claude models
    "claude-3-opus-20240229": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-haiku-20240307": "anthropic",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-5-haiku-20241022": "anthropic",
    
    # DeepSeek models
    "deepseek-chat": "deepseek",
    "deepseek-reasoner": "deepseek",
}

# Conjuntos de modelos
# TODO - Usar Enum (core\enums\models.py)
OPENAI_MODELS = {
    "gpt-4", 
    "gpt-4o", 
    "gpt-4o-mini", 
    "gpt-4-turbo", 
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4o"
}

# TODO - Usar Enum (core\enums\models.py)
ANTHROPIC_MODELS = {
    "claude-3-opus-20240229", 
    "claude-3-sonnet-20240229", 
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet",
    "claude-3-5-haiku-20241022"
}

# TODO - Usar Enum (core\enums\models.py)
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
        LLMAdapter: Um adaptador compatível com LangChain
        
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
    # llm = LLMProxy(
    #     model=model,
    #     temperature=temperature,
    #     api_key=api_key,
    #     base_url=base_url
    # )
    
    # Envolver em um adaptador compatível com LangChain
    #return create_langchain_compatible_llm(llm)
    pass