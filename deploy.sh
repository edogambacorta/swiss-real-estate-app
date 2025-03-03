#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting deployment process..."

# Check if required environment variables are set
echo "Checking environment variables..."
python3 check_env.py

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Streamlit app
echo "Starting the Streamlit app..."
streamlit run main.py

echo "Deployment process completed."
