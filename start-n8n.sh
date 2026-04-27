#!/bin/bash
# Load all env vars from .env and start n8n.
# Use this instead of running `n8n` directly so NODE_FUNCTION_ALLOW_BUILTIN
# (and other vars) reach the task-runner sandbox.
set -e
cd "$(dirname "$0")"
set -a
source ./.env
set +a
echo "Loaded env. NODE_FUNCTION_ALLOW_BUILTIN=$NODE_FUNCTION_ALLOW_BUILTIN"
exec n8n
