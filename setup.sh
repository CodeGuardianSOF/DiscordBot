#!/bin/bash

# Function to check if a command exists
command_exists () {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system packages
install_packages () {
    echo "Installing system packages..."
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-pip git || { echo "Failed to install packages with apt-get"; exit 1; }
    elif command_exists brew; then
        brew update
        brew install python3 git || { echo "Failed to install packages with brew"; exit 1; }
    elif command_exists yum; then
        sudo yum install -y python3 python3-venv python3-pip git || { echo "Failed to install packages with yum"; exit 1; }
    else
        echo "Package manager not supported. Install Python 3, pip, and git manually."
        exit 1
    fi
}

# Function to set up the virtual environment and install Python packages
setup_virtualenv () {
    echo "Setting up the virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
    source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || { echo "Failed to install Python packages"; exit 1; }
    else
        echo "requirements.txt not found"
        exit 1
    fi
}

# Function to configure the bot
configure_bot () {
    echo "Configuring the bot..."
    if [ ! -f "config/config.yaml" ]; then
        echo "Configuration file 'config/config.yaml' not found."
        read -p "Do you want to edit the 'config.yaml' file now? (y/n) " choice
        case "$choice" in
            y|Y ) nano config/config.yaml ;;
            n|N ) echo "Skipping configuration editing. Make sure to create and edit 'config.yaml' before running the bot." ;;
            * ) echo "Invalid choice. Exiting."; exit 1 ;;
        esac
    else
        read -p "Do you want to edit the existing 'config/config.yaml' file now? (y/n) " choice
        case "$choice" in
            y|Y ) nano config/config.yaml ;;
            n|N ) echo "Skipping configuration editing." ;;
            * ) echo "Invalid choice. Exiting."; exit 1 ;;
        esac
    fi
}

# Function to create a helper script for running the bot
create_run_script () {
    echo "Creating run script..."
    cat > run.sh <<EOL
#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the bot
python main.py
EOL
    chmod +x run.sh || { echo "Failed to make run.sh executable"; exit 1; }
}

# Function to print usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --help           Show this help message"
    echo "  --config <file>  Specify a configuration file (default: config/config.yaml)"
}

# Check for sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        echo "This script must be run as root. Please use sudo."
        exit 1
    fi
}

# Main script
main () {
    check_sudo

    CONFIG_FILE="config/config.yaml"

    while [ "$1" != "" ]; do
        case $1 in
            --help )           usage
                               exit
                               ;;
            --config )         shift
                               CONFIG_FILE=$1
                               ;;
            * )                usage
                               exit 1
        esac
        shift
    done

    # Install system packages
    install_packages

    # Navigate to the repository directory
    cd "$(dirname "$0")" || { echo "Failed to change directory"; exit 1; }

    # Set up the virtual environment and install Python packages
    setup_virtualenv

    # Configure the bot
    configure_bot

    # Create run script
    create_run_script

    # Inform the user
    echo "Setup complete. Use './run.sh' to start the bot."

    # Delete the script
    echo "Deleting setup script..."
    rm -- "$0" || { echo "Failed to delete the script"; exit 1; }
}

# Execute the main function
main "$@"

