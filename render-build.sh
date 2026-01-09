#!/usr/bin/env bash
# exit on error
set -o errexit

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to the PATH explicitly so the shell can find it immediately
export PATH="$HOME/.local/bin:$PATH"

# Verify uv is working
uv --version

# Install dependencies using the lockfile
uv sync --no-dev

# Run migrations (for your SQLite db)
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --no-input