#!/bin/bash
# run_tests.sh — Executes your Flask test suite inside Docker
# Usage: ./run_tests.sh [container_name]
# If no container name is provided, defaults to "adhdpapi-web".

# Exit immediately if a command exits with a non-zero status
set -e

# Optionally rebuild container (uncomment the next line if desired)
# docker-compose up --build -d

CONTAINER_NAME=${1:-adhdpapi-web}

echo "🔍 Running Caelum test suite in container: $CONTAINER_NAME..."

# Run the tests and tee the output to a log file
docker exec -it $CONTAINER_NAME python -m unittest discover -s tests | tee test_output.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
  echo "✅ All tests passed!"
else
  echo "❌ Some tests failed. Review logs above."
fi
