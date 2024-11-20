FROM ubuntu:22.04

WORKDIR /project

# Install dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    make \
    gcc \
    mbrola

# Install Python dependencies
RUN pip install numpy pandas matplotlib mbrola

# Install MBROLA
RUN git clone https://github.com/numediart/MBROLA-voices.git ~/MBROLA-voices &&\
    cp -r ~/MBROLA-voices/data/. /usr/share/mbrola/
RUN git clone https://github.com/numediart/MBROLA.git ~/MBROLA &&\
    cd ~/MBROLA && \
    make 