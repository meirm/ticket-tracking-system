#!/bin/bash

# Run the Docker container
podman run -d --name tts --rm  -p 8000:8000 ticket-system-dev