FROM python:3.12-alpine

ENV CODE_DIR="/multitool"

LABEL from="python:3.12-alpine"
LABEL code_dir=${CODE_DIR}

# Install dependencies
RUN apk update && \
    apk add gcc g++ linux-headers openssl-dev curl

# Install Multitool library
COPY ./setup.py ${CODE_DIR}/
COPY ./requirements.txt ${CODE_DIR}/
COPY ./multitool ${CODE_DIR}/multitool/
COPY ./examples ${CODE_DIR}/examples/

RUN python -m pip install ${CODE_DIR}

# Check
RUN multitool
