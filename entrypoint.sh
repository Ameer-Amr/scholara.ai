#!/bin/sh

set -e

echo "--> Waiting for PostgreSQL to be ready..."
# Use python to quickly check if the database port is accepting connections
uv run python -c "
import socket
import time
import os
from urllib.parse import urlparse

url = urlparse(os.getenv('DATABASE_URL', ''))
hostname = url.hostname or 'db'
port = url.port or 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((hostname, port))
        s.close()
        break
    except socket.error:
        time.sleep(1)
"

echo "--> Database is up! Running database migrations..."
uv run alembic upgrade head

echo "--> Migrations complete. Starting FastAPI..."
exec "$@"