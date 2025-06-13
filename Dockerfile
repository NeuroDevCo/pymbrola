FROM ubuntu:22.04

WORKDIR /project

COPY ./mbrola/install.py /project/.

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y git build-essential python3-full python3-rich
RUN git config --global core.compression 0
RUN python3 /project/install.py
