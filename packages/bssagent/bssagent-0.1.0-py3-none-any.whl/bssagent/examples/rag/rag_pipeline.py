from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from bssagent.rag import create_rag_pipeline, create_rag_pipeline, GOOGLE_AI_EMBEDDING_MODELS
from bssagent.rag.rag import RAGConfig

from bssagent.environment import setup_environment_variables

setup_environment_variables()

# Define sources
sources = [
    {'type': 'url', 'url': 'https://example.com'},
]

config = RAGConfig(
    embedding_model_name=GOOGLE_AI_EMBEDDING_MODELS['GEMINI_EMBEDDING_EXP_03_07'],
    vector_db_type='chroma',
    chunk_size=500,
    chunk_overlap=100,
    persist_directory='./vector_store',
    include_metadata=True
)

pipeline = create_rag_pipeline(
    embedding_model_name=GOOGLE_AI_EMBEDDING_MODELS['GEMINI_EMBEDDING_EXP_03_07'],
    vector_db_type='chroma',
    llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash"),
    sources=sources,
    config=config
)

# Query the system
result = pipeline.query("What is the main topic?")
print(result.answer)
