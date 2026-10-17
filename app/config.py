"""Configuration par variables d'environnement (défauts pour un poste local)."""

import os

# URL de l'API Ollama (endpoint compatible OpenAI : OLLAMA_BASE_URL + "/v1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Modèle de chat — valeur provisoire, à confirmer au CHECKPOINT 1
# (voir notes/model_smoke_test.md).
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")

# Modèle d'embeddings pour le RAG
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# Clé d'API (valeur factice pour Ollama ; utile si on pointe vers une autre API)
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")

# Nombre d'extraits d'annales injectés dans le prompt
TOP_K = int(os.getenv("TOP_K", "3"))
