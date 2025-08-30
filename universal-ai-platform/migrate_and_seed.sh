#!/bin/bash
# Usage: ./migrate_and_seed.sh <remote_host>
# Example: ./migrate_and_seed.sh root@164.90.167.193

set -e

REMOTE_HOST="$1"
CONTAINER_NAME="nexusai"

if [ -z "$REMOTE_HOST" ]; then
  echo "Usage: $0 <remote_host>"
  exit 1
fi

echo "Running Alembic migrations and seeding users on $REMOTE_HOST in container $CONTAINER_NAME..."

ssh "$REMOTE_HOST" "docker exec $CONTAINER_NAME alembic upgrade head && docker exec $CONTAINER_NAME python3 seed_test_users.py"

echo "Done."
