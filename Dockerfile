FROM python:3.10-slim

# Update and install essential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Python3 as the default python
RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN pip3 install poetry==1.8.3

# Copy Poetry files first to cache deps
COPY pyproject.toml poetry.lock ./

# Set Poetry environment variables
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install project dependencies using Poetry
RUN poetry lock --no-update && \ 
    poetry install --no-root && rm -rf $POETRY_CACHE_DIR && \
    apt-get update && apt-get install -y libgl1


WORKDIR /src

# Copy the actual app
COPY src ./src

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
