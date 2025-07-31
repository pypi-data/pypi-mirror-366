from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from enum import Enum
import os

class AICompany(Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"

class LLM(Enum):
    # OpenAI models
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O_1106 = "gpt-4o-1106"
    GPT_4O_1106_PREVIEW = "gpt-4o-1106-preview"
    # Anthropic models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet"
    # Google models
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    # DeepSeek models
    DEEPSEEK_R1 = "deepseek-r1"
    # Ollama models
    OLLAMA_LLAMA3_8B = "llama3.8b"
    OLLAMA_LLAMA3_8B_INSTRUCT = "llama3.8b-instruct"
    OLLAMA_LLAMA3_8B_INSTRUCT_V2 = "llama3.8b-instruct-v2"
    OLLAMA_LLAMA3_8B_INSTRUCT_V3 = "llama3.8b-instruct-v3"


def get_llm(
    ai_company: AICompany, 
    model_name: LLM, 
    temperature: float = 0.8
    ) -> ChatOpenAI | ChatGoogleGenerativeAI | ChatAnthropic | ChatDeepSeek | ChatOllama | None:
    """
    Get a LLM model.
    """
    if ai_company == AICompany.OPENAI: 
        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set")
        return ChatOpenAI(model=model_name.value, temperature=temperature)
    elif ai_company == AICompany.GOOGLE:
        if os.getenv("GOOGLE_API_KEY") is None:
            raise ValueError("GOOGLE_API_KEY is not set")
        return ChatGoogleGenerativeAI(model=model_name.value, temperature=temperature)
    elif ai_company ==  AICompany.ANTHROPIC:
        if os.getenv("ANTHROPIC_API_KEY") is None:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        return ChatAnthropic(model_name=model_name.value,temperature=temperature, timeout=None, stop=None)
    elif ai_company == AICompany.DEEPSEEK:
        if os.getenv("DEEPSEEK_API_KEY") is None:
            raise ValueError("DEEPSEEK_API_KEY is not set") 
        return ChatDeepSeek(model=model_name.value, temperature=temperature)
    elif ai_company == AICompany.OLLAMA:
        if os.getenv("OLLAMA_BASE_URL") is None:
            raise ValueError("OLLAMA_BASE_URL is not set")
        return ChatOllama(model=model_name.value, temperature=temperature, base_url=(os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434"))