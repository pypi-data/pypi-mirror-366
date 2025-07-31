from dotenv import load_dotenv
import os
from typing import Any

def setup_environment_variables() -> Any:
    """
    Loads environment variables from the .env file.
    """
    load_dotenv()

    """
    Set all environment to os.environ
    """
    for key, value in os.environ.items():
        os.environ[key] = value
    
    return os.environ 

def enable_langsmith_tracing(project_name: str):
    """
    Enables LangSmith tracing.
    """
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = project_name
    if os.getenv("LANGCHAIN_API_KEY") is None:
        raise ValueError("LANGCHAIN_API_KEY is not set")