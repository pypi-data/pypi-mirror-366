sync:
	uv sync --locked

lint: sync
	uv run ruff check --no-fix
	uv run basedpyright

test: sync
	uv run coverage run -m pytest
	uv run coverage report

qa: sync lint test

e2e: sync
	uv run pytest -m e2e --e2e
