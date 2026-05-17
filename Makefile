.PHONY: tests

install:
	python -m pip install -e .

test:
	uv run ruff format
	uv run ruff check
	uv run pytest --maxfail=1 --cov --cov-branch --cov-report=xml

docker-build:
	docker build . -t gongcastro/pymbrola
	docker compose up -d

docker-run:
	docker run -it gongcastro/pymbrola:latest
