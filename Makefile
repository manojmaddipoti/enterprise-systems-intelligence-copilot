.PHONY: setup seed init-db run-api run-web test evals docker-build docker-run

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[dev]"
	cd web && npm install

seed:
	.venv/bin/python -m data.seed.generate_data

init-db:
	.venv/bin/python -m db.duckdb.init_db

run-api:
	.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-web:
	cd web && npm run dev

test:
	.venv/bin/pytest

evals:
	.venv/bin/python -m evals.run_evals

docker-build:
	docker compose build

docker-run:
	docker compose up
