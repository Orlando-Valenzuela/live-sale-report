#!/bin/bash

# Change working path
cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Please install Python 3 before running this script."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &>/dev/null; then
    echo "pip3 is not installed. Please install pip3 before running this script."
    exit 1
fi

# Read the contents of requirements.txt
requirements=$(cat requirements.txt)

# Iterate over each value in requirements.txt
while IFS= read -r line; do
    # Check if the Python library is installed
    if ! python3 -c "import $line" &>/dev/null; then
        # Prompt the user to install the dependency
        read -p "The Python library '$line' is not installed. Would you like to install it? (y/n): " answer
        if [[ $answer =~ ^[Yy]$ ]]; then
            # Install the dependency
            pip3 install "$line"
        fi
    fi
done <<< "$requirements"

# Verify all dependencies are up to date
pip3 install --upgrade -r requirements.txt

# Run livesale.py
python3 livesale.py