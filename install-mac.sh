#!/bin/bash

# --- Configuration ---
# Directory to clone Didier Stevens' tools into
DIDIER_STEVENS_DIR="$HOME/tools/DidierStevensSuite"
INSTALL_DIDIER_TOOLS=true # Set to false to skip cloning Didier Stevens' Suite

# --- Helper Functions ---
print_info() {
    echo "INFO: $1"
}

print_warn() {
    echo "WARN: $1"
}

print_error() {
    echo "ERROR: $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- OS Detection ---
OS=""
if [[ "$(uname)" == "Linux" ]]; then
    OS="Linux"
    # Check if apt exists (for Debian/Ubuntu based)
    if ! command_exists apt; then
        print_error "apt package manager not found. This script is primarily for Debian/Ubuntu based systems."
        # Add checks for other Linux package managers (yum, dnf, pacman) if needed
        exit 1
    fi
elif [[ "$(uname)" == "Darwin" ]]; then
    OS="macOS"
    # Check if Homebrew exists
    if ! command_exists brew; then
        print_error "Homebrew (brew) not found. Please install it from https://brew.sh/"
        exit 1
    fi
else
    print_error "Unsupported operating system."
    exit 1
fi

print_info "Detected OS: $OS"
print_info "Starting forensic tools installation..."

# --- Ensure Git is installed ---
if ! command_exists git; then
    print_info "Attempting to install Git..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt update && sudo apt install -y git
    elif [[ "$OS" == "macOS" ]]; then
        brew install git
    fi
    if ! command_exists git; then
        print_error "Failed to install Git. Please install it manually."
        exit 1
    fi
fi

# --- Ensure Python3/pip3 are installed ---
if ! command_exists python3 || ! command_exists pip3; then
    print_info "Attempting to install Python 3 and pip..."
     if [[ "$OS" == "Linux" ]]; then
        sudo apt update && sudo apt install -y python3 python3-pip
    elif [[ "$OS" == "macOS" ]]; then
        brew install python # pip3 should come with this
    fi
     if ! command_exists python3 || ! command_exists pip3; then
        print_error "Failed to install Python 3 / pip3. Please install them manually."
        exit 1
    fi
fi

# --- Ensure Ruby/gem are installed ---
if ! command_exists ruby || ! command_exists gem; then
    print_info "Attempting to install Ruby and RubyGems..."
     if [[ "$OS" == "Linux" ]]; then
        sudo apt update && sudo apt install -y ruby ruby-dev build-essential # build-essential often needed for gems
    elif [[ "$OS" == "macOS" ]]; then
        brew install ruby # gem should come with this
    fi
     if ! command_exists ruby || ! command_exists gem; then
        print_error "Failed to install Ruby / Gem. Please install them manually."
        exit 1
    fi
fi


# --- Install Packages via System Package Manager (apt/brew) ---
print_info "Installing tools via $OS package manager..."
SYSTEM_PACKAGES=(
    imagemagick   # ImageMagick (identify, compare)
    steghide      # Steghide
    mediainfo     # Mediainfo CLI
    # file        # Usually pre-installed on Linux/macOS
    # strings     # Usually pre-installed on Linux/macOS
    # stegdetect  # Often tricky, might need specific source or compile
)

# Platform-specific package adjustments
if [[ "$OS" == "Linux" ]]; then
    sudo apt update
    sudo apt install -y "${SYSTEM_PACKAGES[@]}" || print_warn "Some system packages might have failed to install."
    # Attempt to install stegdetect on Linux, might fail
    sudo apt install -y stegdetect || print_warn "Could not install 'stegdetect' via apt. May require manual compilation."
elif [[ "$OS" == "macOS" ]]; then
    brew update
    brew install "${SYSTEM_PACKAGES[@]}" || print_warn "Some Homebrew packages might have failed to install."
    # Attempt to install stegdetect on macOS, might fail
    brew install stegdetect || print_warn "Could not install 'stegdetect' via brew. May require manual compilation."
fi

# --- Install Python Packages via pip3 ---
print_info "Installing Python tools via pip3..."
PIP_PACKAGES=(
    peepdf        # Peepdf PDF Analyzer
    # oletools    # Includes pdfid.py - alternative to manual download if preferred
)
sudo pip3 install "${PIP_PACKAGES[@]}" || pip3 install --user "${PIP_PACKAGES[@]}" || print_warn "Some pip packages might have failed to install. Ensure pip3 is configured correctly."

# --- Install Ruby Packages via gem ---
print_info "Installing Ruby tools via gem..."
GEM_PACKAGES=(
    origami-pdf   # Origami PDF Walker/Analyzer
    zsteg         # zsteg Steganography detector
)
# Using sudo for system-wide gem install might be needed depending on Ruby setup
sudo gem install "${GEM_PACKAGES[@]}" || gem install --user-install "${GEM_PACKAGES[@]}" || print_warn "Some Ruby gems might have failed to install. Ensure Ruby/Gem is configured correctly."

# --- Install Didier Stevens Suite via Git ---
if [ "$INSTALL_DIDIER_TOOLS" = true ]; then
    print_info "Installing Didier Stevens Suite via Git..."
    if ! command_exists git; then
        print_error "Git is not installed. Cannot clone Didier Stevens Suite."
    else
        if [ -d "$DIDIER_STEVENS_DIR" ]; then
            print_warn "Directory $DIDIER_STEVENS_DIR already exists. Skipping clone."
        else
            mkdir -p "$(dirname "$DIDIER_STEVENS_DIR")"
            git clone https://github.com/DidierStevens/DidierStevensSuite.git "$DIDIER_STEVENS_DIR"
            if [ $? -eq 0 ]; then
                print_info "Successfully cloned Didier Stevens Suite to $DIDIER_STEVENS_DIR"
                print_warn "IMPORTANT: Add $DIDIER_STEVENS_DIR to your PATH or call scripts like pdfid.py using the full path."
            else
                print_error "Failed to clone Didier Stevens Suite."
            fi
        fi
    fi
fi

# --- Final Checks & Notes ---
print_info "Checking installation status for some tools..."
command_exists pdfinfo || print_warn "pdfinfo (from poppler-utils) not checked/installed by this script, install manually if needed ('sudo apt install poppler-utils' or 'brew install poppler')."
command_exists exiftool || print_warn "exiftool not checked/installed by this script, install manually if needed ('sudo apt install libimage-exiftool-perl' or 'brew install exiftool')."
command_exists qpdf || print_warn "qpdf not checked/installed by this script, install manually if needed ('sudo apt install qpdf' or 'brew install qpdf')."
command_exists mutool || print_warn "mutool (from mupdf-tools) not checked/installed by this script, install manually if needed ('sudo apt install mupdf-tools' or 'brew install mupdf-tools')."

print_info "Installation script finished."
print_warn "Please verify installations and ensure tool directories are in your PATH."
print_warn "Some tools like StegDetect might require manual compilation if package manager install failed."
