#!/bin/bash

# Function to print in blue (info logs)
info_log () {
    echo -e "\033[1;34m$(date +'%Y-%m-%d %H:%M:%S') INFO: $1\033[0m"
}

# Function to print in orange (questions)
ask_question () {
    echo -e "\033[1;33m$1\033[0m"
}

# Function to print in red (error logs)
error_log () {
    echo -e "\033[1;31m$(date +'%Y-%m-%d %H:%M:%S') ERROR: $1\033[0m" >&2
}

# Function to check if a command exists
command_exists () {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system packages
install_packages () {
    info_log "Installing system packages..."
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-pip git nano || { error_log "Failed to install packages with apt-get"; exit 1; }
    elif command_exists brew; then
        brew update
        brew install python3 git nano || { error_log "Failed to install packages with brew"; exit 1; }
    elif command_exists yum; then
        sudo yum install -y python3 python3-venv python3-pip git nano || { error_log "Failed to install packages with yum"; exit 1; }
    else
        error_log "Package manager not supported. Install Python 3, pip, git, and nano manually."
        exit 1
    fi
}

# Function to set up the virtual environment and install Python packages
setup_virtualenv () {
    info_log "Setting up the virtual environment..."
    python3 -m venv venv || { error_log "Failed to create virtual environment"; exit 1; }
    source venv/bin/activate || { error_log "Failed to activate virtual environment"; exit 1; }
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || { error_log "Failed to install Python packages"; exit 1; }
    else
        error_log "requirements.txt not found"
        exit 1
    fi
}

# Function to configure the bot
configure_bot () {
    info_log "Configuring the bot..."
    if [ ! -f "$CONFIG_FILE" ]; then
        ask_question "Configuration file '$CONFIG_FILE' not found. Do you want to edit the 'config.yaml' file now? (y/n)"
        read -p "" choice
        case "$choice" in
            y|Y ) nano config/config.yaml ;;
            n|N ) error_log "Skipping configuration editing. Make sure to create and edit '$CONFIG_FILE' before running the bot." ;;
            * ) error_log "Invalid choice. Exiting."; exit 1 ;;
        esac
    else
        ask_question "Do you want to edit the existing '$CONFIG_FILE' file now? (y/n)"
        read -p "" choice
        case "$choice" in
            y|Y ) nano "$CONFIG_FILE" ;;
            n|N ) info_log "Skipping configuration editing." ;;
            * ) error_log "Invalid choice. Exiting."; exit 1 ;;
        esac
    fi
}

# Function to create a helper script for running the bot
create_run_script () {
    info_log "Creating run script..."
    cat > run.sh <<EOL
#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the bot
python main.py
EOL
    chmod +x run.sh || { error_log "Failed to make run.sh executable"; exit 1; }
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
    if [ "$(id -u)" -ne 0 ]; then
        error_log "This script must be run as root. Please use sudo."
        exit 1
    fi
}

# Cleanup function to remove temporary files
cleanup() {
    info_log "Cleaning up..."
    deactivate 2>/dev/null || true
    rm -rf venv || true
    error_log "Setup failed. Cleanup complete."
}

# Main script
main () {
    trap cleanup EXIT

    check_sudo

    CONFIG_FILE="${CONFIG_FILE:-config/config.yaml}"

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
    cd "$(dirname "$0")" || { error_log "Failed to change directory"; exit 1; }

    # Set up the virtual environment and install Python packages
    setup_virtualenv

    # Configure the bot
    configure_bot

    # Create run script
    create_run_script

    # Inform the user
    info_log "Setup complete. Use './run.sh' to start the bot."

    # Delete the script
    info_log "Deleting setup script..."
    rm -- "$0" || { error_log "Failed to delete the script"; exit 1; }

    trap - EXIT
}

# Execute the main function
main "$@"
