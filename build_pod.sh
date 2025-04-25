#!/bin/bash

# Build the Docker image
podman build -t ticket-system-dev -f Dockerfile_dev .
