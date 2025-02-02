FROM python:3.11.5-bookworm AS builder


# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
ENV VIRTUAL_ENV="/home/pythonrunner/.venv"
ENV PATH="/home/pythonrunner/.local/bin:${VIRTUAL_ENV}/bin:${PATH}"

# install environment dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    checkinstall \
    cmake \
    pkg-config \
    yasm \
    libjpeg-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libxine2-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libv4l-dev \
    python3-dev \
    python3-numpy \
    libtbb-dev \
    libgtk2.0-dev \
    ffmpeg \
    && apt-get clean


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

FROM builder AS dev-container
USER root

# copy app
COPY . /app/

# set work directory
WORKDIR /app

EXPOSE  5001

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]