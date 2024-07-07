#!/bin/bash

LOG_FILE="setup.log"
CONFIG_FILE="config/config.yaml"
REQUIRED_COMMANDS=("python3" "pip3" "git")

# Function to print in blue (info logs)
info_log () {
    echo -e "\033[1;34m$(date +'%Y-%m-%d %H:%M:%S') INFO: $1\033[0m"
    echo "$(date +'%Y-%m-%d %H:%M:%S') INFO: $1" >> $LOG_FILE
}

# Function to print in red (error logs)
error_log () {
    echo -e "\033[1;31m$(date +'%Y-%m-%d %H:%M:%S') ERROR: $1\033[0m" >&2
    echo "$(date +'%Y-%m-%d %H:%M:%S') ERROR: $1" >> $LOG_FILE
}

# Function to print in yellow (warning logs)
warn_log () {
    echo -e "\033[1;33m$(date +'%Y-%m-%d %H:%M:%S') WARNING: $1\033[0m"
    echo "$(date +'%Y-%m-%d %H:%M:%S') WARNING: $1" >> $LOG_FILE
}

# Function to check if a command exists
command_exists () {
    command -v "$1" >/dev/null 2>&1
}

# Function to install a system package
install_package () {
    PACKAGE=$1
    info_log "Installing $PACKAGE..."
    if command_exists apt-get; then
        sudo apt-get install -y $PACKAGE || { error_log "Failed to install $PACKAGE with apt-get"; exit 1; }
    elif command_exists yum; then
        sudo yum install -y $PACKAGE || { error_log "Failed to install $PACKAGE with yum"; exit 1; }
    elif command_exists brew; then
        brew install $PACKAGE || { error_log "Failed to install $PACKAGE with brew"; exit 1; }
    else
        error_log "Package manager not supported. Install $PACKAGE manually."
        exit 1
    fi
}

# Function to check if all required commands are available
check_dependencies () {
    info_log "Checking required dependencies..."
    for cmd in "${REQUIRED_COMMANDS[@]}"; do
        if ! command_exists $cmd; then
            error_log "Required command '$cmd' is not available. Please install it and try again."
            exit 1
        fi
    done
}

# Function to upgrade pip
upgrade_pip () {
    info_log "Upgrading pip..."
    pip3 install --upgrade pip || { error_log "Failed to upgrade pip"; exit 1; }
}

# Function to install system packages
install_packages () {
    info_log "Installing system packages..."
    PACKAGES=("python3" "python3-venv" "python3-pip" "git")
    for PACKAGE in "${PACKAGES[@]}"; do
        install_package $PACKAGE
    done
}

# Function to set up the virtual environment and install Python packages
setup_virtualenv () {
    info_log "Setting up the virtual environment..."
    if [ -d "venv" ]; then
        warn_log "Virtual environment already exists. Reusing existing environment."
    else
        python3 -m venv venv || { error_log "Failed to create virtual environment"; exit 1; }
    fi
    source venv/bin/activate || { error_log "Failed to activate virtual environment"; exit 1; }
    upgrade_pip
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || { error_log "Failed to install Python packages"; exit 1; }
    else
        warn_log "requirements.txt not found. Skipping Python package installation."
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
}

# Check for sudo
check_sudo() {
    if [ "$(id -u)" -ne 0 ]; then
        error_log "This script must be run as root. Please use sudo."
        exit 1
    fi
}

# Backup existing configuration
backup_config() {
    info_log "Backing up existing configuration..."
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "${CONFIG_FILE}.bak" || { error_log "Failed to backup configuration file"; exit 1; }
    fi
}

# Restore configuration from backup
restore_config() {
    info_log "Restoring configuration from backup..."
    if [ -f "${CONFIG_FILE}.bak" ]; then
        mv "${CONFIG_FILE}.bak" "$CONFIG_FILE" || { error_log "Failed to restore configuration file"; exit 1; }
    fi
}

# Cleanup function to remove temporary files
cleanup() {
    info_log "Cleaning up..."
    deactivate 2>/dev/null || true
    rm -rf venv || true
    restore_config
    error_log "Setup failed. Cleanup complete."
}

# Main script
main () {
    trap cleanup EXIT

    check_sudo
    check_dependencies

    while [ "$1" != "" ]; do
        case $1 in
            --help )           usage
                               exit
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

    # Ensure main.py exists
    if [ ! -f "main.py" ]; then
        error_log "main.py not found. Ensure you are in the correct directory."
        exit 1
    fi

    # Set up the virtual environment and install Python packages
    setup_virtualenv

    # Backup configuration
    backup_config

    # Create run script
    create_run_script

    # Inform the user
    info_log "Setup complete. Use './run.sh' to start the bot."

    # Cleanup
    info_log "Deleting setup script and log file..."
    rm -- "$0" "$LOG_FILE" || { error_log "Failed to delete the script or log file"; exit 1; }

    trap - EXIT
}

# Execute the main function
main "$@"
