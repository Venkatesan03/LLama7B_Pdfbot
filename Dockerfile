ARG CONTAINER_TIMEZONE=UTC
FROM ubuntu:20.04

WORKDIR /LangChainPdfBot
COPY . .
ARG DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the default Python version
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Verify installation
RUN python3 --version && pip3 --version

RUN chmod +x install.sh
RUN ./install.sh

