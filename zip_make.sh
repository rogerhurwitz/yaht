#!/bin/sh

zip -r $1 "README.md" "rules.md" "requirements.txt" "pyproject.toml" "Dockerfile" "src/yaht/" "tests/" "unit_tests.py" "run_tests.sh" "build_docker.sh" -x "**/__pycache__/*" "**/.DS_Store" 
