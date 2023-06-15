#!/bin/bash

# change directory to script's location
script_dir="$(dirname "$0")"
cd "$script_dir" || { echo "Changing directory failed"; exit 1; }

# Function to check if a command is available
check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Function to prompt user for installing a package
prompt_install() {
    read -rp "$1 is not installed. Would you like to install it? (y/n): " ans
    ans=${ans,,}  # convert to lowercase
    if [[ "$ans" != "y" ]]; then
        echo "$1 is required. Exiting."
        exit 1
    fi
}

# Check if Homebrew is installed
if ! check_command brew; then
    prompt_install "Homebrew"
    # installing Homebrew
    if ! /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        echo "Installing Homebrew failed"; 
        exit 1
    fi
fi

# Check if git is installed
if ! check_command git; then
    prompt_install "git"
    # install git with Homebrew
    if ! brew install git; then
        echo "Installing git failed"; 
        exit 1
    fi
fi

# Clone or pull the repository depending on whether it's already a Git repository
git_origin="https://github.com/Orlando-Valenzuela/live-sale-report.git"
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git init || { echo "Git init failed"; exit 1; }
    git remote add origin "$git_origin" || { echo "Adding remote failed"; exit 1; }
    git fetch origin || { echo "Fetching from origin failed"; exit 1; }
    git reset --hard origin/main || { echo "Resetting to origin/main failed"; exit 1; }
    git checkout . || { echo "Git checkout failed"; exit 1; }
else
    current_origin=$(git remote get-url origin)
    if [ "$current_origin" != "$git_origin" ]; then
        git remote set-url origin "$git_origin"
    fi
    # Clean untracked files and directories to avoid merge conflicts
    git clean -f -d
    if ! git pull origin main; then
        echo "Git pull failed"; 
        exit 1
    fi
fi

# check if python3 is installed
if ! check_command python3; then
    prompt_install "Python3"
    # install python3 with Homebrew
    if ! brew install python3; then
        echo "Installing Python3 failed";
        exit 1
    fi
fi

# check if pip3 is installed
if ! check_command pip3; then
    prompt_install "pip3"
    # pip3 should be included with python3, this is just to confirm it's there
    echo "pip3 should be installed with Python3. Please ensure it is before continuing."
    exit 1
fi

# iterate over requirements.txt
while IFS= read -r requirement || [[ -n "$requirement" ]]
do
    if ! pip3 show "$requirement" > /dev/null 2>&1; then
        prompt_install "Python package $requirement"
        if ! pip3 install "$requirement"; then
            echo "Installing Python package $requirement failed"; 
            exit 1
        fi
    fi
    echo "Checking for updates to $requirement"
    pip3 install --upgrade "$requirement"
done < requirements.txt

# finally, launch the python script
python3 livesale.py