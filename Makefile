.PHONY: tests

install:
	python -m pip install -e .

test:
	uv run ruff format
	uv run ruff check
	uv run pytest --cov=. --maxfail=1 --cov-report term

docker-build:
	docker build . -t mbrola

docker-run:
	docker run -it mbrola
