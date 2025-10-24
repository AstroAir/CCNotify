#
# CCNotify Automated Installation Script for Windows
# https://github.com/dazuiba/CCNotify
#

[CmdletBinding()]
param(
    [switch]$Silent,
    [switch]$DryRun,
    [switch]$Help
)

# Configuration
$InstallDir = Join-Path $env:USERPROFILE ".claude\ccnotify"
$ScriptDir = $PSScriptRoot
$ErrorActionPreference = "Stop"

# Show help
if ($Help) {
    Write-Host "CCNotify Installation Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Silent     Silent mode (non-interactive)"
    Write-Host "  -DryRun     Show what would be done without making changes"
    Write-Host "  -Help       Show this help message"
    exit 0
}

# Helper functions
function Write-Header {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Prompt-YesNo {
    param([string]$Message)
    
    if ($Silent) {
        return $true  # Default to yes in silent mode
    }
    
    while ($true) {
        $response = Read-Host "$Message (y/n)"
        if ($response -match '^[Yy]') {
            return $true
        }
        elseif ($response -match '^[Nn]') {
            return $false
        }
        Write-Host "Please answer yes or no."
    }
}

# Check if Python is installed
function Test-Python {
    Write-Info "Checking Python installation..."
    
    $pythonCmd = $null
    $pythonVersion = $null
    
    # Try python first, then python3
    try {
        $pythonVersion = & python --version 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "python"
        }
    }
    catch {
        # Python not found, try python3
    }
    
    if (-not $pythonCmd) {
        try {
            $pythonVersion = & python3 --version 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = "python3"
            }
        }
        catch {
            # Python3 not found either
        }
    }
    
    if (-not $pythonCmd) {
        Write-ErrorMsg "Python is not installed or not in PATH"
        Write-Host ""
        Write-Host "Please install Python 3.7 or higher from:"
        Write-Host "  https://www.python.org/downloads/"
        Write-Host ""
        Write-Host "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }
    
    # Parse version
    if ($pythonVersion -match 'Python (\d+)\.(\d+)\.(\d+)') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $versionStr = "$major.$minor.$($matches[3])"
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
            Write-ErrorMsg "Python $versionStr is too old (requires 3.7+)"
            Write-Host "Please install Python 3.7 or higher from:"
            Write-Host "  https://www.python.org/downloads/"
            exit 1
        }
        
        Write-Success "Python $versionStr found ($pythonCmd)"
        return $pythonCmd
    }
    else {
        Write-ErrorMsg "Could not determine Python version"
        exit 1
    }
}

# Check if pip is available
function Test-Pip {
    param([string]$PythonCmd)
    
    Write-Info "Checking pip installation..."
    
    try {
        $null = & $PythonCmd -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "pip is available"
            return $true
        }
    }
    catch {
        # Pip not available
    }
    
    Write-ErrorMsg "pip is not available"
    Write-Host ""
    Write-Host "Please install pip:"
    Write-Host "  $PythonCmd -m ensurepip --upgrade"
    Write-Host ""
    Write-Host "Or reinstall Python with pip included"
    exit 1
}

# Install Python dependencies
function Install-Dependencies {
    param([string]$PythonCmd)
    
    Write-Info "Installing Python dependencies..."
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would install: plyer>=2.0.0"
        return
    }
    
    try {
        $null = & $PythonCmd -m pip install --user "plyer>=2.0.0" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Installed plyer"
        }
        else {
            throw "pip install failed"
        }
    }
    catch {
        Write-ErrorMsg "Failed to install plyer"
        Write-Host "Try manually: $PythonCmd -m pip install --user plyer"
        exit 1
    }
}

# Create installation directory and copy files
function Install-Files {
    Write-Info "Installing CCNotify files..."
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would create directory: $InstallDir"
        Write-Info "[DRY RUN] Would copy: ccnotify.py, install_helper.py"
        return
    }
    
    # Create directory
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        Write-Success "Created directory: $InstallDir"
    }
    else {
        Write-Success "Directory already exists: $InstallDir"
    }
    
    # Copy main script
    $ccnotifyPath = Join-Path $ScriptDir "ccnotify.py"
    if (Test-Path $ccnotifyPath) {
        Copy-Item $ccnotifyPath $InstallDir -Force
        Write-Success "Installed ccnotify.py"
    }
    else {
        Write-ErrorMsg "ccnotify.py not found in $ScriptDir"
        exit 1
    }
    
    # Copy helper script
    $helperPath = Join-Path $ScriptDir "install_helper.py"
    if (Test-Path $helperPath) {
        Copy-Item $helperPath $InstallDir -Force
        Write-Success "Installed install_helper.py"
    }
    else {
        Write-ErrorMsg "install_helper.py not found in $ScriptDir"
        exit 1
    }
}

# Configure Claude hooks
function Set-Hooks {
    param([string]$PythonCmd)
    
    Write-Info "Configuring Claude Code hooks..."
    
    $helperScript = Join-Path $InstallDir "install_helper.py"
    
    try {
        if ($DryRun) {
            & $PythonCmd $helperScript install --dry-run
        }
        else {
            & $PythonCmd $helperScript install
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Hooks configured successfully"
            }
            else {
                throw "Hook configuration failed"
            }
        }
    }
    catch {
        Write-ErrorMsg "Failed to configure hooks"
        exit 1
    }
}

# Validate installation
function Test-Installation {
    param([string]$PythonCmd)
    
    Write-Info "Validating installation..."
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would validate installation"
        return
    }
    
    # Check if script exists
    $scriptPath = Join-Path $InstallDir "ccnotify.py"
    if (Test-Path $scriptPath) {
        # Test the script
        try {
            $null = & $PythonCmd $scriptPath 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "CCNotify script is working"
            }
            else {
                Write-Warning "Script test returned non-zero exit code"
            }
        }
        catch {
            Write-Warning "Could not test script execution"
        }
    }
    else {
        Write-ErrorMsg "Script not found at $scriptPath"
        exit 1
    }
    
    # Check if settings.json was configured
    $settingsPath = Join-Path $env:USERPROFILE ".claude\settings.json"
    if (Test-Path $settingsPath) {
        Write-Success "Settings file configured"
    }
    else {
        Write-Warning "Settings file not found (will be created on first use)"
    }
}

# Main installation flow
function Main {
    Write-Header "CCNotify Installation"
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No changes will be made"
        Write-Host ""
    }
    
    Write-Info "Detected OS: Windows"
    Write-Host ""
    
    # Check prerequisites
    $pythonCmd = Test-Python
    Test-Pip $pythonCmd
    
    Write-Host ""
    
    # Install dependencies
    Install-Dependencies $pythonCmd
    
    Write-Host ""
    
    # Install files
    Install-Files
    
    Write-Host ""
    
    # Configure hooks
    Set-Hooks $pythonCmd
    
    Write-Host ""
    
    # Validate installation
    Test-Installation $pythonCmd
    
    Write-Host ""
    Write-Header "Installation Complete!"
    
    if (-not $DryRun) {
        Write-Host ""
        Write-Success "CCNotify has been installed successfully!"
        Write-Host ""
        Write-Host "Next steps:"
        Write-Host "  1. Restart Claude Code or reload your terminal"
        Write-Host "  2. Test with: claude 'after 1 second, echo hello'"
        Write-Host "  3. You should see a desktop notification"
        Write-Host ""
        Write-Host "Logs: $InstallDir\ccnotify.log"
        Write-Host "Database: $InstallDir\ccnotify.db"
        Write-Host ""
        Write-Host "To uninstall, run: .\uninstall.ps1"
    }
}

# Run main function
try {
    Main
}
catch {
    Write-Host ""
    Write-ErrorMsg "Installation failed: $_"
    exit 1
}

