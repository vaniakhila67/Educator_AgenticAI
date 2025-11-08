#!/usr/bin/env bash
set -o errexit  # stop on error

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install requirements based on service type
if [ "$RENDER_SERVICE_TYPE" = "web" ]; then
    if [ "$RENDER_START_COMMAND" = "streamlit run frontend/app.py" ]; then
        pip install -r requirements-frontend.txt
    else
        pip install -r requirements.txt
    fi
fi