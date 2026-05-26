"""Gerenciamento de caminhos e diretórios do projeto. Autora: Nathalia Adriele"""

from src.config.settings import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DIR,
    INTERIM_DIR,
    PROCESSED_DIR,
    REPORTS_DIR,
    LOGS_DIR,
    DOCS_DIR,
)


def ensure_directories() -> None:
    """Cria todos os diretórios do projeto caso não existam."""
    dirs = [
        DATA_DIR,
        RAW_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        REPORTS_DIR,
        LOGS_DIR,
        DOCS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def get_project_root() -> str:
    """Retorna o caminho raiz do projeto como string."""
    return str(PROJECT_ROOT)
