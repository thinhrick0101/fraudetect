#!/bin/bash
# This script tears down the environment for the fraud detection system.

echo "Stopping and removing all services..."
# The -v flag removes named volumes, which is useful for a clean restart.
docker-compose -f docker/docker-compose.yml down -v

# Optional: Clean up local artifacts
# Uncomment the lines below if you want to remove generated data and logs.
# echo "Cleaning up local artifacts..."
# rm -rf mlruns/
# rm -rf data/processed/*
# rm -f logs/*.log

echo "Teardown complete."
