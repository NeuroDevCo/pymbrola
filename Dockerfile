FROM python:3.12-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential curl git jq

WORKDIR /pymbrola

COPY . .

RUN pip install .

RUN python3 -m mbrola

CMD ["/bin/bash"]
