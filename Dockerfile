FROM python:3.12
WORKDIR /project
ENV DEBIAN_FRONTEND=noninteractive
COPY src/mbrola/install.sh /install.sh 
RUN apt-get update && apt-get install -y git build-essential gcc
RUN git config --global core.compression 0
RUN 
RUN chmod +x /install.sh && /install.sh
COPY src/mbrola/mbrola.py /project/