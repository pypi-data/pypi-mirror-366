# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts
ARG DEBIAN_FRONTEND=noninteractive

# Update package list and install necessary tools and dependencies
RUN apt-get update && \
    apt-get install -y \
    sudo \
    git \
    curl \
    gnupg \
    make \
    build-essential \
    pkg-config \
    libzmq3-dev \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    libbz2-dev



# Make a 'dev' user
RUN echo 'root:dev' | chpasswd
RUN useradd -ms /bin/bash dev && echo 'dev:dev' | chpasswd && adduser dev sudo
RUN echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY --chown=dev:dev .devcontainer/scripts/gu /usr/local/bin/gu
COPY --chown=dev:dev .devcontainer/scripts/.bashrc /home/dev/.bashrc

USER dev

# Install Python 3 using apt
RUN sudo apt-get install -y python3 python3-pip

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh


