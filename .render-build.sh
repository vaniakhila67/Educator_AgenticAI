#!/usr/bin/env bash
set -o errexit  # stop on error

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install requirements based on service type
if [ "$RENDER_SERVICE_TYPE" = "web" ]; then
    if echo "$RENDER_START_COMMAND" | grep -q "streamlit"; then
        # Use simplified frontend requirements
        pip install -r requirements-frontend-render.txt
    else
        # Use simplified backend requirements
        pip install -r requirements-render.txt
    fi
fi