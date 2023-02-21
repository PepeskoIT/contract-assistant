#!/bin/sh

# # Run migration
alembic upgrade head

# Run sync
python3 main.py