import os

BASE_DIR = "ai_project"

FILES = {
    # Config
    "ai_system/config/__init__.py": "",
    "ai_system/config/settings.py": """from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DB_URL: str = "postgresql://user:pass@localhost/db"

    class Config:
        env_file = ".env"

settings = Settings()
""",
    "ai_system/config/model_registry.py": "# Modelo de registro dinâmico de modelos de IA",
    # Models
    "ai_system/models/__init__.py": "",
    "ai_system/models/base.py": """class BaseModel:
    def load(self):
        raise NotImplementedError

    def forward(self, *args, **kwargs):
        raise NotImplementedError
""",
    "ai_system/models/embeddings/openai.py": "# Exemplo de embedding com OpenAI",
    "ai_system/models/generators/image_gen.py": "# Geração de imagem com modelo",
    "ai_system/models/transcribers/whisper.py": "# Transcrição com Whisper",
    # Agents
    "ai_system/agents/__init__.py": "",
    "ai_system/agents/base.py": """class BaseAgent:
    def __init__(self, tools=None):
        self.tools = tools or []

    def run(self, message: str):
        raise NotImplementedError
""",
    "ai_system/agents/prompts/support_prompt.txt": "You are a helpful assistant.",
    "ai_system/agents/tools/search_tool.py": "# Ferramenta de busca",
    "ai_system/agents/chat_agents/support_agent.py": "# Agente de suporte baseado em LLM",
    # Workflows
    "ai_system/workflows/__init__.py": "",
    "ai_system/workflows/components/embed_search.py": "# Componente embed -> search",
    "ai_system/workflows/pipelines.py": "# Pipelines de workflows completos",
    # DB
    "ai_system/db/__init__.py": "",
    "ai_system/db/base.py": "# Abstrações comuns de DB",
    "ai_system/db/relational/postgres.py": "# PostgreSQL client",
    "ai_system/db/vector/faiss.py": "# FAISS vector store",
    # Services
    "ai_system/services/__init__.py": "",
    "ai_system/services/cache.py": "# Cache helper",
    "ai_system/services/logging.py": "# Logging config",
    "ai_system/services/retry.py": "# Retry logic",
    # Utils
    "ai_system/utils/__init__.py": "",
    "ai_system/utils/io.py": "# Funções de I/O",
    "ai_system/utils/text.py": "# Manipulação de texto",
    # Server
    "server/__init__.py": "",
    "server/app.py": """from fastapi import FastAPI
from server.routes import chat

app = FastAPI()
app.include_router(chat.router, prefix="/chat")
""",
    "server/routes/__init__.py": "",
    "server/routes/chat.py": """from fastapi import APIRouter
from server.schemas.chat import ChatRequest

router = APIRouter()

@router.post("/")
def chat_endpoint(request: ChatRequest):
    return {"response": f"Received: {request.message}"}
""",
    "server/schemas/__init__.py": "",
    "server/schemas/chat.py": """from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
""",
    "server/middlewares/__init__.py": "",
    "server/middlewares/auth.py": "# Middleware de autenticação",
    # Scripts
    "scripts/init_db.py": "# Script para inicializar o banco de dados",
    "scripts/test_pipeline.py": "# Executa uma pipeline de teste",
    # Tests
    "tests/__init__.py": "",
    "tests/models/__init__.py": "",
    "tests/agents/__init__.py": "",
    # Root files
    ".env": "OPENAI_API_KEY=\nDB_URL=postgresql://user:pass@localhost/db",
    "README.md": "# Projeto AI\n\nProjeto modular para sistemas de IA generativa e classificação.",
    "run.py": "# Entry point para rodar workflows ou servidores",
    "pyproject.toml": '[tool.poetry]\nname = "ai_project"\nversion = "0.1.0"\ndescription = "Projeto de IA modular"\n',
    "requirements.txt": "fastapi\npydantic\nuvicorn\n",
}


def create_project():
    for path, content in FILES.items():
        full_path = os.path.join(BASE_DIR, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    create_project()
