#!/bin/bash
#
# CCNotify Automated Installation Script for Unix-like systems (macOS/Linux)
# https://github.com/dazuiba/CCNotify
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/.claude/ccnotify"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SILENT_MODE=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--silent)
            SILENT_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "CCNotify Installation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -s, --silent    Silent mode (non-interactive)"
            echo "  --dry-run       Show what would be done without making changes"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

prompt_yes_no() {
    if [ "$SILENT_MODE" = true ]; then
        return 0  # Default to yes in silent mode
    fi
    
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify Python installation
check_python() {
    print_info "Checking Python installation..."
    
    local python_cmd=""
    local python_version=""
    
    # Try python3 first, then python
    if command_exists python3; then
        python_cmd="python3"
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
    elif command_exists python; then
        python_cmd="python"
        python_version=$(python --version 2>&1 | awk '{print $2}')
    else
        print_error "Python is not installed"
        echo "Please install Python 3.7 or higher:"
        echo "  macOS: brew install python3"
        echo "  Linux: sudo apt install python3 (Debian/Ubuntu)"
        echo "         sudo dnf install python3 (Fedora/RHEL)"
        echo "         sudo pacman -S python (Arch Linux)"
        exit 1
    fi
    
    # Check version (require 3.7+)
    local major=$(echo "$python_version" | cut -d. -f1)
    local minor=$(echo "$python_version" | cut -d. -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 7 ]); then
        print_error "Python $python_version is too old (requires 3.7+)"
        exit 1
    fi
    
    print_success "Python $python_version found ($python_cmd)"
    echo "$python_cmd"
}

# Check if pip is available
check_pip() {
    local python_cmd="$1"
    print_info "Checking pip installation..."
    
    if $python_cmd -m pip --version >/dev/null 2>&1; then
        print_success "pip is available"
        return 0
    else
        print_error "pip is not available"
        echo "Please install pip:"
        echo "  macOS: python3 -m ensurepip --upgrade"
        echo "  Linux: sudo apt install python3-pip (Debian/Ubuntu)"
        echo "         sudo dnf install python3-pip (Fedora/RHEL)"
        echo "         sudo pacman -S python-pip (Arch Linux)"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    local python_cmd="$1"
    print_info "Installing Python dependencies..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would install: plyer>=2.0.0"
        return 0
    fi
    
    if $python_cmd -m pip install --user "plyer>=2.0.0" >/dev/null 2>&1; then
        print_success "Installed plyer"
    else
        print_error "Failed to install plyer"
        echo "Try manually: $python_cmd -m pip install --user plyer"
        exit 1
    fi
}

# Create installation directory and copy files
install_files() {
    print_info "Installing CCNotify files..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would create directory: $INSTALL_DIR"
        print_info "[DRY RUN] Would copy: ccnotify.py, install_helper.py"
        return 0
    fi
    
    # Create directory
    mkdir -p "$INSTALL_DIR"
    print_success "Created directory: $INSTALL_DIR"
    
    # Copy main script
    if [ -f "$SCRIPT_DIR/ccnotify.py" ]; then
        cp "$SCRIPT_DIR/ccnotify.py" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/ccnotify.py"
        print_success "Installed ccnotify.py"
    else
        print_error "ccnotify.py not found in $SCRIPT_DIR"
        exit 1
    fi
    
    # Copy helper script
    if [ -f "$SCRIPT_DIR/install_helper.py" ]; then
        cp "$SCRIPT_DIR/install_helper.py" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/install_helper.py"
        print_success "Installed install_helper.py"
    else
        print_error "install_helper.py not found in $SCRIPT_DIR"
        exit 1
    fi
}

# Configure Claude hooks
configure_hooks() {
    local python_cmd="$1"
    print_info "Configuring Claude Code hooks..."
    
    if [ "$DRY_RUN" = true ]; then
        $python_cmd "$INSTALL_DIR/install_helper.py" install --dry-run
    else
        if $python_cmd "$INSTALL_DIR/install_helper.py" install; then
            print_success "Hooks configured successfully"
        else
            print_error "Failed to configure hooks"
            exit 1
        fi
    fi
}

# Offer to install platform-specific notification tools
install_platform_tools() {
    local os_type="$1"
    
    if [ "$SILENT_MODE" = true ]; then
        return 0  # Skip in silent mode
    fi
    
    echo ""
    print_info "Optional: Install platform-specific notification tools for better experience"
    
    if [ "$os_type" = "macos" ]; then
        if ! command_exists terminal-notifier; then
            echo ""
            echo "terminal-notifier provides native macOS notifications with better features."
            if prompt_yes_no "Install terminal-notifier via Homebrew?"; then
                if command_exists brew; then
                    if [ "$DRY_RUN" = true ]; then
                        print_info "[DRY RUN] Would run: brew install terminal-notifier"
                    else
                        brew install terminal-notifier
                        print_success "Installed terminal-notifier"
                    fi
                else
                    print_warning "Homebrew not found. Install from: https://brew.sh"
                    echo "Then run: brew install terminal-notifier"
                fi
            fi
        else
            print_success "terminal-notifier is already installed"
        fi
    elif [ "$os_type" = "linux" ]; then
        if ! command_exists notify-send; then
            echo ""
            echo "libnotify provides native Linux notifications."
            if prompt_yes_no "Install libnotify?"; then
                if [ "$DRY_RUN" = true ]; then
                    print_info "[DRY RUN] Would install libnotify"
                else
                    # Detect package manager and install
                    if command_exists apt-get; then
                        sudo apt-get install -y libnotify-bin
                        print_success "Installed libnotify"
                    elif command_exists dnf; then
                        sudo dnf install -y libnotify
                        print_success "Installed libnotify"
                    elif command_exists pacman; then
                        sudo pacman -S --noconfirm libnotify
                        print_success "Installed libnotify"
                    else
                        print_warning "Could not detect package manager"
                        echo "Please install libnotify manually for your distribution"
                    fi
                fi
            fi
        else
            print_success "libnotify is already installed"
        fi
    fi
}

# Validate installation
validate_installation() {
    local python_cmd="$1"
    print_info "Validating installation..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would validate installation"
        return 0
    fi
    
    # Check if script exists and is executable
    if [ -x "$INSTALL_DIR/ccnotify.py" ]; then
        # Test the script
        if "$INSTALL_DIR/ccnotify.py" >/dev/null 2>&1; then
            print_success "CCNotify script is working"
        else
            print_warning "Script test returned non-zero exit code"
        fi
    else
        print_error "Script is not executable"
        exit 1
    fi
    
    # Check if settings.json was configured
    if [ -f "$HOME/.claude/settings.json" ]; then
        print_success "Settings file configured"
    else
        print_warning "Settings file not found (will be created on first use)"
    fi
}

# Main installation flow
main() {
    print_header "CCNotify Installation"
    
    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN MODE - No changes will be made"
        echo ""
    fi
    
    # Detect OS
    OS_TYPE=$(detect_os)
    print_info "Detected OS: $OS_TYPE"
    
    if [ "$OS_TYPE" = "unknown" ]; then
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    echo ""
    
    # Check prerequisites
    PYTHON_CMD=$(check_python)
    check_pip "$PYTHON_CMD"
    
    echo ""
    
    # Install dependencies
    install_dependencies "$PYTHON_CMD"
    
    echo ""
    
    # Install files
    install_files
    
    echo ""
    
    # Configure hooks
    configure_hooks "$PYTHON_CMD"
    
    echo ""
    
    # Offer platform-specific tools
    install_platform_tools "$OS_TYPE"
    
    echo ""
    
    # Validate installation
    validate_installation "$PYTHON_CMD"
    
    echo ""
    print_header "Installation Complete!"
    
    if [ "$DRY_RUN" = false ]; then
        echo ""
        print_success "CCNotify has been installed successfully!"
        echo ""
        echo "Next steps:"
        echo "  1. Restart Claude Code or reload your terminal"
        echo "  2. Test with: claude 'after 1 second, echo hello'"
        echo "  3. You should see a desktop notification"
        echo ""
        echo "Logs: $INSTALL_DIR/ccnotify.log"
        echo "Database: $INSTALL_DIR/ccnotify.db"
        echo ""
        echo "To uninstall, run: ./uninstall.sh"
    fi
}

# Run main function
main

