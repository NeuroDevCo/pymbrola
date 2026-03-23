FROM ubuntu:22.04
WORKDIR /project
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl git build-essential gcc python3
COPY bin/install.sh /install.sh 
RUN git config --global core.compression 0
RUN chmod +x /install.sh && /install.sh
COPY mbrola/mbrola.py /project/