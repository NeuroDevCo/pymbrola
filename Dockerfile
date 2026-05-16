FROM python:3.12-slim-trixie

ARG HOST_UID=1000
ARG HOST_GID=1000

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential curl git jq

WORKDIR /app


COPY bin/install.sh ./install.sh 
RUN chmod +x ./install.sh && ./install.sh -v it4

RUN useradd -m appuser && chown -R appuser /app
USER appuser

RUN git config --global core.compression 0

RUN python3 -m pip install mbrola

CMD ["/bin/bash"]