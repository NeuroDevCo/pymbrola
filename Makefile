build:
	hatch build

publish:
	hatch publish

install:
	python -m pip install -e .

main:
	hatch run .\src\mbrola\mbrola.py

docker-build:
	docker build . -t mbrola:v0.0.2

docker-run:
	docker run -it mbrola:v0.0.2