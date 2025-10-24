#
# CCNotify Uninstallation Script for Windows
# https://github.com/dazuiba/CCNotify
#

[CmdletBinding()]
param(
    [switch]$Silent,
    [switch]$DryRun,
    [switch]$KeepData,
    [switch]$Help
)

# Configuration
$InstallDir = Join-Path $env:USERPROFILE ".claude\ccnotify"
$ErrorActionPreference = "Stop"

# Show help
if ($Help) {
    Write-Host "CCNotify Uninstallation Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\uninstall.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Silent      Silent mode (non-interactive)"
    Write-Host "  -DryRun      Show what would be done without making changes"
    Write-Host "  -KeepData    Keep log files and database"
    Write-Host "  -Help        Show this help message"
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

# Find Python command
function Find-Python {
    try {
        $null = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return "python"
        }
    }
    catch {
        # Try python3
    }
    
    try {
        $null = & python3 --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return "python3"
        }
    }
    catch {
        # Python not found
    }
    
    return $null
}

# Remove hooks from settings.json
function Remove-Hooks {
    param([string]$PythonCmd)
    
    Write-Info "Removing CCNotify hooks from settings.json..."
    
    if (-not $PythonCmd) {
        Write-Warning "Python not found, cannot remove hooks automatically"
        Write-Info "Please manually remove CCNotify hooks from $env:USERPROFILE\.claude\settings.json"
        return
    }
    
    $helperScript = Join-Path $InstallDir "install_helper.py"
    if (-not (Test-Path $helperScript)) {
        Write-Warning "install_helper.py not found, cannot remove hooks automatically"
        Write-Info "Please manually remove CCNotify hooks from $env:USERPROFILE\.claude\settings.json"
        return
    }
    
    try {
        if ($DryRun) {
            & $PythonCmd $helperScript uninstall --dry-run
        }
        else {
            & $PythonCmd $helperScript uninstall
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Hooks removed successfully"
            }
            else {
                throw "Hook removal failed"
            }
        }
    }
    catch {
        Write-Warning "Failed to remove hooks automatically"
        Write-Info "Please manually remove CCNotify hooks from $env:USERPROFILE\.claude\settings.json"
    }
}

# Remove installation files
function Remove-Files {
    Write-Info "Removing CCNotify files..."
    
    if (-not (Test-Path $InstallDir)) {
        Write-Info "Installation directory not found, nothing to remove"
        return
    }
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would remove directory: $InstallDir"
        if ($KeepData) {
            Write-Info "[DRY RUN] Would keep: ccnotify.log, ccnotify.db"
        }
        return
    }
    
    if ($KeepData) {
        # Remove only script files, keep data
        $filesToRemove = @("ccnotify.py", "install_helper.py")
        foreach ($file in $filesToRemove) {
            $filePath = Join-Path $InstallDir $file
            if (Test-Path $filePath) {
                Remove-Item $filePath -Force
                Write-Success "Removed $file"
            }
        }
        
        # Check if directory has only data files left
        $remainingFiles = Get-ChildItem $InstallDir | Where-Object { 
            $_.Name -notmatch '(ccnotify\.log|ccnotify\.db)' 
        }
        
        if ($remainingFiles.Count -eq 0) {
            Write-Success "Removed script files (kept data files)"
            Write-Info "Data files preserved in: $InstallDir"
        }
    }
    else {
        # Remove entire directory
        Remove-Item $InstallDir -Recurse -Force
        Write-Success "Removed installation directory: $InstallDir"
    }
}

# Optional: Remove Python dependencies
function Remove-Dependencies {
    param([string]$PythonCmd)
    
    if ($Silent) {
        return  # Skip in silent mode
    }
    
    if (-not $PythonCmd) {
        return  # Skip if Python not found
    }
    
    Write-Host ""
    if (Prompt-YesNo "Remove Python dependency (plyer)?") {
        if ($DryRun) {
            Write-Info "[DRY RUN] Would run: $PythonCmd -m pip uninstall -y plyer"
        }
        else {
            try {
                & $PythonCmd -m pip uninstall -y plyer 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Removed plyer"
                }
                else {
                    Write-Warning "Failed to remove plyer (may not be installed)"
                }
            }
            catch {
                Write-Warning "Failed to remove plyer (may not be installed)"
            }
        }
    }
}

# Main uninstallation flow
function Main {
    Write-Header "CCNotify Uninstallation"
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No changes will be made"
        Write-Host ""
    }
    
    # Confirm uninstallation
    if (-not $Silent -and -not $DryRun) {
        Write-Host ""
        if (-not (Prompt-YesNo "Are you sure you want to uninstall CCNotify?")) {
            Write-Host "Uninstallation cancelled"
            exit 0
        }
        Write-Host ""
    }
    
    # Find Python
    $pythonCmd = Find-Python
    if ($pythonCmd) {
        Write-Info "Found Python: $pythonCmd"
    }
    else {
        Write-Warning "Python not found"
    }
    
    Write-Host ""
    
    # Remove hooks
    Remove-Hooks $pythonCmd
    
    Write-Host ""
    
    # Remove files
    Remove-Files
    
    # Optional: Remove dependencies
    if ($pythonCmd) {
        Remove-Dependencies $pythonCmd
    }
    
    Write-Host ""
    Write-Header "Uninstallation Complete!"
    
    if (-not $DryRun) {
        Write-Host ""
        Write-Success "CCNotify has been uninstalled"
        
        if ($KeepData) {
            Write-Host ""
            Write-Info "Data files were preserved in: $InstallDir"
            Write-Host "To remove them manually, run:"
            Write-Host "  Remove-Item -Recurse -Force `"$InstallDir`""
        }
        
        Write-Host ""
        Write-Host "Thank you for using CCNotify!"
    }
}

# Run main function
try {
    Main
}
catch {
    Write-Host ""
    Write-ErrorMsg "Uninstallation failed: $_"
    exit 1
}

