from bssagent.rag import RAGPipeline
from bssagent.rag.rag import RAGConfig
from bssagent.rag.embedding_models import GOOGLE_AI_EMBEDDING_MODELS

config = RAGConfig(
    embedding_model_name=GOOGLE_AI_EMBEDDING_MODELS['GEMINI_EMBEDDING_EXP_03_07'],
    vector_db_type='chroma',
    persist_directory='./vector_store',
)

pipeline = RAGPipeline(
    config=config
)
pipeline.load_vector_store(config.persist_directory or "./vector_store")


print(pipeline.similarity_search("What is the main topic?", k=2))