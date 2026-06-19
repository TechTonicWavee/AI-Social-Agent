import os
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

def get_ollama_model():
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7,
    )

model = get_ollama_model()