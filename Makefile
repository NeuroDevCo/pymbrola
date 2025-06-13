install:
	python -m pip install -e .

test:
	uv run pytest --cov=mbrola --cov-report=term-missing
	
main:
	uv run .\src\mbrola\mbrola.py

docker-build:
	docker build . -t mbrola:v0.0.2

docker-run:
	docker run -it mbrola:v0.0.2