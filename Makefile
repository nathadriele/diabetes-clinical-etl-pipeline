# =============================================================================
# sus-diabetes-etl-pipeline - Makefile
# =============================================================================

.PHONY: help setup download run test streamlit clean lint all

# Variáveis
PYTHON       := python
VENV         := .venv
PIP          := $(VENV)/bin/pip
PYTHON_VENV  := $(VENV)/bin/python
PYTEST       := $(VENV)/bin/pytest
STREAMLIT    := $(VENV)/bin/streamlit

help: ## Exibe esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Cria ambiente virtual e instala dependências
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Ambiente configurado com sucesso."

download: ## Baixa dados do DATASUS
	$(PYTHON_VENV) -m src.data.download_datasus_data
	@echo "✓ Download dos dados concluído."

run: ## Executa o pipeline ETL completo
	$(PYTHON_VENV) -m src.data.pipeline
	@echo "✓ Pipeline ETL executado com sucesso."

test: ## Executa os testes automatizados
	$(PYTEST) tests/ -v --tb=short
	@echo "✓ Testes executados."

test-cov: ## Executa testes com cobertura
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing
	@echo "✓ Testes com cobertura executados."

streamlit: ## Inicia a aplicação Streamlit
	$(STREAMLIT) run src/app/streamlit_app.py

clean: ## Remove arquivos temporários e cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov
	@echo "✓ Arquivos temporários removidos."

all: setup download run test ## Executa setup, download, pipeline e testes
	@echo "✓ Pipeline completo executado com sucesso."
