#!/bin/bash
#
# CCNotify Uninstallation Script for Unix-like systems (macOS/Linux)
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
SILENT_MODE=false
DRY_RUN=false
KEEP_DATA=false

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
        --keep-data)
            KEEP_DATA=true
            shift
            ;;
        -h|--help)
            echo "CCNotify Uninstallation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -s, --silent     Silent mode (non-interactive)"
            echo "  --dry-run        Show what would be done without making changes"
            echo "  --keep-data      Keep log files and database"
            echo "  -h, --help       Show this help message"
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Find Python command
find_python() {
    if command_exists python3; then
        echo "python3"
    elif command_exists python; then
        echo "python"
    else
        echo ""
    fi
}

# Remove hooks from settings.json
remove_hooks() {
    local python_cmd="$1"
    print_info "Removing CCNotify hooks from settings.json..."
    
    if [ -z "$python_cmd" ]; then
        print_warning "Python not found, cannot remove hooks automatically"
        print_info "Please manually remove CCNotify hooks from ~/.claude/settings.json"
        return 1
    fi
    
    if [ ! -f "$INSTALL_DIR/install_helper.py" ]; then
        print_warning "install_helper.py not found, cannot remove hooks automatically"
        print_info "Please manually remove CCNotify hooks from ~/.claude/settings.json"
        return 1
    fi
    
    if [ "$DRY_RUN" = true ]; then
        $python_cmd "$INSTALL_DIR/install_helper.py" uninstall --dry-run
    else
        if $python_cmd "$INSTALL_DIR/install_helper.py" uninstall; then
            print_success "Hooks removed successfully"
        else
            print_warning "Failed to remove hooks automatically"
            print_info "Please manually remove CCNotify hooks from ~/.claude/settings.json"
        fi
    fi
}

# Remove installation files
remove_files() {
    print_info "Removing CCNotify files..."
    
    if [ ! -d "$INSTALL_DIR" ]; then
        print_info "Installation directory not found, nothing to remove"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would remove directory: $INSTALL_DIR"
        if [ "$KEEP_DATA" = true ]; then
            print_info "[DRY RUN] Would keep: ccnotify.log, ccnotify.db"
        fi
        return 0
    fi
    
    if [ "$KEEP_DATA" = true ]; then
        # Remove only script files, keep data
        local files_to_remove=("ccnotify.py" "install_helper.py")
        for file in "${files_to_remove[@]}"; do
            if [ -f "$INSTALL_DIR/$file" ]; then
                rm "$INSTALL_DIR/$file"
                print_success "Removed $file"
            fi
        done
        
        # Check if directory is now empty (except for data files)
        local remaining_files=$(ls -A "$INSTALL_DIR" 2>/dev/null | grep -v -E '(ccnotify\.log|ccnotify\.db)' | wc -l)
        if [ "$remaining_files" -eq 0 ]; then
            print_success "Removed script files (kept data files)"
            print_info "Data files preserved in: $INSTALL_DIR"
        fi
    else
        # Remove entire directory
        rm -rf "$INSTALL_DIR"
        print_success "Removed installation directory: $INSTALL_DIR"
    fi
}

# Optional: Remove Python dependencies
remove_dependencies() {
    local python_cmd="$1"
    
    if [ "$SILENT_MODE" = true ]; then
        return 0  # Skip in silent mode
    fi
    
    if [ -z "$python_cmd" ]; then
        return 0  # Skip if Python not found
    fi
    
    echo ""
    if prompt_yes_no "Remove Python dependency (plyer)?"; then
        if [ "$DRY_RUN" = true ]; then
            print_info "[DRY RUN] Would run: $python_cmd -m pip uninstall -y plyer"
        else
            if $python_cmd -m pip uninstall -y plyer >/dev/null 2>&1; then
                print_success "Removed plyer"
            else
                print_warning "Failed to remove plyer (may not be installed)"
            fi
        fi
    fi
}

# Main uninstallation flow
main() {
    print_header "CCNotify Uninstallation"
    
    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN MODE - No changes will be made"
        echo ""
    fi
    
    # Confirm uninstallation
    if [ "$SILENT_MODE" = false ] && [ "$DRY_RUN" = false ]; then
        echo ""
        if ! prompt_yes_no "Are you sure you want to uninstall CCNotify?"; then
            echo "Uninstallation cancelled"
            exit 0
        fi
        echo ""
    fi
    
    # Find Python
    PYTHON_CMD=$(find_python)
    if [ -n "$PYTHON_CMD" ]; then
        print_info "Found Python: $PYTHON_CMD"
    else
        print_warning "Python not found"
    fi
    
    echo ""
    
    # Remove hooks
    remove_hooks "$PYTHON_CMD"
    
    echo ""
    
    # Remove files
    remove_files
    
    # Optional: Remove dependencies
    if [ -n "$PYTHON_CMD" ]; then
        remove_dependencies "$PYTHON_CMD"
    fi
    
    echo ""
    print_header "Uninstallation Complete!"
    
    if [ "$DRY_RUN" = false ]; then
        echo ""
        print_success "CCNotify has been uninstalled"
        
        if [ "$KEEP_DATA" = true ]; then
            echo ""
            print_info "Data files were preserved in: $INSTALL_DIR"
            echo "To remove them manually, run:"
            echo "  rm -rf $INSTALL_DIR"
        fi
        
        echo ""
        echo "Thank you for using CCNotify!"
    fi
}

# Run main function
main

