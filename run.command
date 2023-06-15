#!/bin/bash

cd "$(dirname "$0")"

# Check if Git is installed
if ! command -v git &>/dev/null; then
    echo "Git is not installed. Please install Git before running this script."
    exit 1
fi

# Check if the repository directory exists
if [ ! -d "./" ]; then
    # Clone the repository if it doesn't exist
    git clone https://github.com/Orlando-Valenzuela/live-sale-report.git .
fi

# Read the contents of requirements.txt
requirements=$(cat live-sale-report/requirements.txt)

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
pip3 install --upgrade -r live-sale-report/requirements.txt

# Run livesale.py
python3 live-sale-report/livesale.py