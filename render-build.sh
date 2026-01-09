#!/usr/bin/env bash
# exit on error
set -o errexit

# first check if uv is there 
if ! command -v uv &> /dev/null; then
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# sourcing is not a problem anyways
source $HOME/.cargo/env

# Install dependencies
uv sync --no-dev

# Run migrations (for your SQLite db)
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --no-input

