install:
	python -m pip install -e .

test:
	uv run ruff format
	uv run ruff check
	uv run pytest --cov=mbrola --cov-report=term-missing

docker-build:
	docker build . -t mbrola

docker-run:
	docker run -it mbrola
