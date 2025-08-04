FROM ghcr.io/catthehacker/ubuntu:act-22.04

ENV PATH="/root/.local/bin:$PATH"

RUN pip install uv

RUN uv python install 3.12

SHELL ["/bin/bash", "-c"]

