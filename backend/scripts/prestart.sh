#!/bin/sh

set -e
set -x

python -m backend.backend_pre_start

cd /app/backend
alembic upgrade head

python -m backend.initial_data