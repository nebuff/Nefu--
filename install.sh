#!/bin/bash

NEFU_URL="https://raw.githubusercontent.com/nebuff/Nefu--/refs/heads/main/nefu_interpreter/nefu.py"
INSTALL_PATH="/usr/local/bin/nefu"

echo "Welcome to Nefu installer!"

read -p "Do you want to install Nefu? [y/n]: " INSTALL_CHOICE
if [[ "$INSTALL_CHOICE" != "y" && "$INSTALL_CHOICE" != "Y" ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Detect OS
OS="$(uname -s)"

check_existing_unix() {
    if [ -f "$INSTALL_PATH" ]; then
        read -p "Nefu installation found at $INSTALL_PATH. Do you want to update/overwrite it? [y/n]: " REINSTALL
        if [[ "$REINSTALL" != "y" && "$REINSTALL" != "Y" ]]; then
            echo "Skipping installation."
            exit 0
        fi
    fi
}

install_python_mac() {
    if ! command -v python3 >/dev/null 2>&1; then
        read -p "Python3 not found. Do you want to install Python3 using brew? [y/n]: " PY_CHOICE
        if [[ "$PY_CHOICE" == "y" || "$PY_CHOICE" == "Y" ]]; then
            if ! command -v brew >/dev/null 2>&1; then
                echo "Homebrew not found. Installing Homebrew first..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python
        else
            echo "Python3 is required to run Nefu. Exiting."
            exit 1
        fi
    fi
}

install_python_linux() {
    if ! command -v python3 >/dev/null 2>&1; then
        read -p "Python3 not found. Install using apt? [y/n]: " PY_CHOICE
        if [[ "$PY_CHOICE" == "y" || "$PY_CHOICE" == "Y" ]]; then
            sudo apt update
            sudo apt install -y python3
        else
            echo "Python3 is required to run Nefu. Exiting."
            exit 1
        fi
    fi
}

install_nefu_unix() {
    echo "Downloading Nefu interpreter..."
    sudo curl -fsSL "$NEFU_URL" -o "$INSTALL_PATH"
    if [ $? -ne 0 ]; then
        echo "Error downloading Nefu."
        exit 1
    fi

    # Make it executable
    sudo chmod +x "$INSTALL_PATH"

    # Ensure shebang line exists
    FIRST_LINE=$(head -n 1 "$INSTALL_PATH")
    if [[ "$FIRST_LINE" != "#!"* ]]; then
        if [[ "$OS" == "Darwin" ]]; then
            sudo sed -i '' '1i\
#!/usr/bin/env python3
' "$INSTALL_PATH"
        else
            sudo sed -i '1i #!/usr/bin/env python3' "$INSTALL_PATH"
        fi
    fi

    echo "Nefu installed/updated successfully!"
    echo "Run programs using: nefu <file.nfu>"
}

install_windows() {
    echo "Setting up Nefu on Windows..."

    NEFU_DIR="$USERPROFILE\\Nefu"
    NEFU_BATCH="$NEFU_DIR\\nefu.bat"
    EXISTING=0
    if [ -f "$NEFU_DIR\\nefu.py" ]; then
        EXISTING=1
        read -p "Existing Nefu installation found in $NEFU_DIR. Update/overwrite? [y/n]: " REINSTALL
        if [[ "$REINSTALL" != "y" && "$REINSTALL" != "Y" ]]; then
            echo "Skipping installation."
            exit 0
        fi
    fi

    mkdir -p "$NEFU_DIR"
    curl -fsSL "$NEFU_URL" -o "$NEFU_DIR\\nefu.py"

    # Create a wrapper batch file
    echo "@echo off
python \"$NEFU_DIR\\nefu.py\" %*" > "$NEFU_BATCH"

    echo "Please ensure $NEFU_DIR is in your PATH, then run: nefu <file.nfu>"
    echo "Windows setup finished."
}

# Main
case "$OS" in
    Darwin)
        install_python_mac
        check_existing_unix
        install_nefu_unix
        ;;
    Linux)
        install_python_linux
        check_existing_unix
        install_nefu_unix
        ;;
    CYGWIN*|MINGW*|MSYS*)
        install_windows
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac
