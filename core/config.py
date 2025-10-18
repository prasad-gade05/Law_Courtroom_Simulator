# """Configuration settings for the Legal RAG system"""
# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     GOOGLE_API_KEY: str
#     TAVILY_API_KEY: str
#     MAX_RETRIEVAL_TOKENS: int = 4000
#     DEFAULT_MODEL: str = "gemini-pro"
#     EMBEDDING_MODEL: str = "models/embedding-001"
#     GROQ_API_KEY: str
#     HUGGINGFACE_API_KEY: str
#     SERPER_API_KEY: str
#     KANOON_API_KEY: str
    
#     class Config:
#         env_file = ".env"

# settings = Settings() 