# PrivacyRadar - atalhos para desenvolvimento e deploy

.PHONY: help run-backend run-frontend install-backend install-frontend test docker-up docker-down

help:
	@echo "PrivacyRadar - Comandos úteis"
	@echo ""
	@echo "  make install-backend   Instala dependências do backend (venv + pip install -e .)"
	@echo "  make install-frontend  Instala dependências do frontend (npm install)"
	@echo "  make run-backend       Sobe a API em http://localhost:8000"
	@echo "  make run-frontend       Sobe o frontend em http://localhost:5173"
	@echo "  make test              Roda testes do backend"
	@echo "  make docker-up         Sobe API + Web com Docker Compose"
	@echo "  make docker-down       Para os containers"
	@echo ""

install-backend:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -e .

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && .venv/bin/python run.py

run-frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/python -m pytest tests/ -v

docker-up:
	docker compose up --build

docker-down:
	docker compose down
