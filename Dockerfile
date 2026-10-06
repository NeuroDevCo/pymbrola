FROM python:3.12-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential curl git jq

WORKDIR /pymbrola

ENV OUTPUT_DIR=/pymbrola/output

COPY . .

# make the output dir writable by whatever UID runs the container
RUN useradd -m user && chown -R user:user /pymbrola
RUN mkdir -p ${OUTPUT_DIR} && chmod 777 ${OUTPUT_DIR} 
RUN pip install .

RUN python3 -m src.mbrola

CMD ["python3"]
