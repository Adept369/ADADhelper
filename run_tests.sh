#!/bin/bash

# run_tests.sh — Executes your Flask test suite inside Docker

echo "🔍 Running Caelum test suite in container: adhdpapi-web..."

docker exec -it adhdpapi-web python -m unittest discover -s tests

if [ $? -eq 0 ]; then
  echo "✅ All tests passed!"
else
  echo "❌ Some tests failed. Review logs above."
fi
# To Use run chmod +x run_tests.sh and then ./run_tests.sh



