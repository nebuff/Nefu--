#!/bin/bash

NEFU_URL="https://raw.githubusercontent.com/nebuff/Nefu--/refs/heads/main/nefu_interpreter/nefu.py"
INSTALL_PATH="/usr/local/bin/nefu"
VSIX_URL="https://github.com/nebuff/Nefu--/raw/main/nefu-syntax-for-vscode.vsix"
VSIX_FILE="/tmp/nefu-syntax-for-vscode.vsix"

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

    echo "Nefu interpreter installed at $INSTALL_PATH"
    echo "Run programs using: nefu <file.nfu>"
}

install_windows() {
    echo "Setting up Nefu on Windows..."

    NEFU_DIR="$USERPROFILE\\Nefu"
    NEFU_BATCH="$NEFU_DIR\\nefu.bat"
    if [ -f "$NEFU_DIR\\nefu.py" ]; then
        read -p "Existing Nefu installation found in $NEFU_DIR. Update/overwrite? [y/n]: " REINSTALL
        if [[ "$REINSTALL" != "y" && "$REINSTALL" != "Y" ]]; then
            echo "Skipping installation."
            exit 0
        fi
    fi

    mkdir -p "$NEFU_DIR"
    curl -fsSL "$NEFU_URL" -o "$NEFU_DIR\\nefu.py"

    echo "@echo off
python \"$NEFU_DIR\\nefu.py\" %*" > "$NEFU_BATCH"

    echo "Please ensure $NEFU_DIR is in your PATH, then run: nefu <file.nfu>"
    echo "Windows setup finished."
}

install_code_cli_mac() {
    if ! command -v code >/dev/null 2>&1; then
        echo "Adding VS Code CLI to PATH for macOS..."
        if [ -d "/Applications/Visual Studio Code.app" ]; then
            SHELL_RC="$HOME/.zshrc"
            if [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc"; fi
            echo 'export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"' >> "$SHELL_RC"
            export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
            echo "VS Code CLI added. Restart terminal if not detected."
        else
            echo "VS Code not found in /Applications. Install it first."
        fi
    fi
}

install_code_cli_linux() {
    if ! command -v code >/dev/null 2>&1; then
        echo "Installing VS Code CLI on Linux..."
        if command -v snap >/dev/null 2>&1; then
            sudo snap install code --classic
        elif command -v apt >/dev/null 2>&1; then
            sudo apt update
            sudo apt install -y code
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y code
        else
            echo "Could not install VS Code automatically. Install it manually: https://code.visualstudio.com/"
        fi
    fi
}

install_code_cli_windows() {
    if ! command -v code >/dev/null 2>&1; then
        echo "VS Code CLI not detected on Windows."
        echo "When installing VS Code, make sure 'Add to PATH' is checked."
    fi
}

install_vscode_extension() {
    if command -v code >/dev/null 2>&1; then
        read -p "Do you want to install the Nefu VS Code extension? [y/n]: " EXT_CHOICE
        if [[ "$EXT_CHOICE" == "y" || "$EXT_CHOICE" == "Y" ]]; then
            echo "Downloading Nefu VS Code extension..."
            curl -fsSL "$VSIX_URL" -o "$VSIX_FILE"
            if [ $? -ne 0 ]; then
                echo "Failed to download VSIX file."
                return
            fi
            echo "Installing extension..."
            code --install-extension "$VSIX_FILE" --force
            echo "Nefu syntax highlighting installed in VS Code"
        else
            echo "Skipped VS Code extension installation."
        fi
    else
        echo "VS Code not detected. Skipping extension installation."
    fi
}

# Main
case "$OS" in
    Darwin)
        install_python_mac
        check_existing_unix
        install_nefu_unix
        install_code_cli_mac
        install_vscode_extension
        ;;
    Linux)
        install_python_linux
        check_existing_unix
        install_nefu_unix
        install_code_cli_linux
        install_vscode_extension
        ;;
    CYGWIN*|MINGW*|MSYS*)
        install_windows
        install_code_cli_windows
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac
