#Requires -RunAsAdministrator

<#
.SYNOPSIS
Installs common open-source forensic tools for PDF/Image analysis on Windows.

.DESCRIPTION
Uses Winget and/or Chocolatey, pip, and gem to install tools like ImageMagick,
Mediainfo, Steghide, peepdf, zsteg, origami, etc. Also clones Didier Stevens' Suite.

.NOTES
- Run this script as Administrator.
- Requires an active internet connection.
- Assumes Git, Python3/pip, Ruby/gem are installed or attempts to install them.
- Manual installation might be needed for some tools (e.g., StegDetect).
- Ensure installed tools are in your system PATH.
- Choose whether to use Winget, Chocolatey, or both by commenting/uncommenting sections.
#>

# --- Configuration ---
$useWinget = $true
$useChoco = $true # Set to $false if you don't have/want Chocolatey
$installDidierTools = $true
$didierStevensDir = "$HOME\Documents\tools\DidierStevensSuite" # Adjust path as needed

# --- Helper Functions ---
function Write-Info ($message) { Write-Host "INFO: $message" -ForegroundColor Cyan }
function Write-Warn ($message) { Write-Host "WARN: $message" -ForegroundColor Yellow }
function Write-Error ($message) { Write-Host "ERROR: $message" -ForegroundColor Red }

# Function to check if a command exists
function Test-CommandExists ($command) {
    return [bool](Get-Command $command -ErrorAction SilentlyContinue)
}

# Function to run installer commands
function Invoke-InstallerCommand ($command, $arguments) {
    Write-Host "Executing: $command $arguments"
    try {
        Start-Process -FilePath $command -ArgumentList $arguments -Wait -NoNewWindow -ErrorAction Stop
        Write-Host "`tSuccessfully executed." -ForegroundColor Green
    } catch {
        Write-Warn "`tCommand failed: $($_.Exception.Message)"
    }
}


Write-Info "Starting forensic tools installation..."

# --- Check/Install Prerequisites ---

# Git
if (-not (Test-CommandExists git)) {
    Write-Info "Git not found. Attempting installation..."
    if ($useWinget -and (Test-CommandExists winget)) {
        winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
    } elseif ($useChoco -and (Test-CommandExists choco)) {
        choco install git -y
    } else {
        Write-Warn "Cannot automatically install Git. Please install it manually from https://git-scm.com/download/win"
    }
    if (-not (Test-CommandExists git)) { Write-Error "Git installation failed or requires manual setup (e.g., adding to PATH). Exiting."; exit 1 }
}

# Python 3 / pip
if (-not (Test-CommandExists python) -or -not (Test-CommandExists pip)) {
    Write-Info "Python 3 / pip not found. Attempting installation..."
     if ($useWinget -and (Test-CommandExists winget)) {
        # Ensure PATH is updated by installer if possible
        winget install --id Python.Python.3 -e --accept-source-agreements --accept-package-agreements --scope machine --override '/quiet InstallAllUsers=1 PrependPath=1'
    } elseif ($useChoco -and (Test-CommandExists choco)) {
         choco install python --params "'/InstallDir:C:\Python3 /AddToPath'" -y # Check params for specific versions
    } else {
        Write-Warn "Cannot automatically install Python. Please install it manually from https://www.python.org/downloads/windows/"
    }
    Write-Warn "Python/pip installation might require restarting PowerShell/Terminal for PATH changes to take effect."
    if (-not (Test-CommandExists python) -or -not (Test-CommandExists pip)) { Write-Error "Python/pip installation failed or requires manual PATH setup. Exiting."; exit 1 }
}

# Ruby / gem
if (-not (Test-CommandExists ruby) -or -not (Test-CommandExists gem)) {
    Write-Info "Ruby / gem not found. Attempting installation..."
     if ($useWinget -and (Test-CommandExists winget)) {
        # Installs Ruby with DevKit, which is usually needed for gems
        winget install --id RubyInstallerTeam.RubyWithDevKit -e --accept-source-agreements --accept-package-agreements
    } elseif ($useChoco -and (Test-CommandExists choco)) {
         choco install ruby -y
    } else {
        Write-Warn "Cannot automatically install Ruby. Please install it manually from https://rubyinstaller.org/downloads/"
    }
     Write-Warn "Ruby/gem installation might require restarting PowerShell/Terminal for PATH changes to take effect."
    if (-not (Test-CommandExists ruby) -or -not (Test-CommandExists gem)) { Write-Error "Ruby/gem installation failed or requires manual PATH setup. Exiting."; exit 1 }
}


# --- Install with Winget ---
if ($useWinget) {
    Write-Info "Attempting installations via Winget..."
    if (-not (Test-CommandExists winget)) {
        Write-Warn "Winget command not found. Skipping Winget installations."
    } else {
        $wingetPackages = @(
            # Tool Name                 Winget ID
            @{ Name = "ImageMagick";    ID = "ImageMagick.ImageMagick" },
            @{ Name = "MediaInfo CLI";  ID = "MediaArea.MediaInfo.CLI" },
            @{ Name = "ExifTool";       ID = "OliverBetz.ExifTool" },
            @{ Name = "QPDF";           ID = "qpdf.qpdf" },
            @{ Name = "MuPDF";          ID = "ArtifexSoftware.MuPDF" } # Provides mutool
            # Add more winget package IDs here if found
        )
        foreach ($pkg in $wingetPackages) {
            Write-Info "Installing $($pkg.Name) via Winget..."
            winget install --id $pkg.ID -e --accept-source-agreements --accept-package-agreements
        }
        # Sysinternals Strings (Optional)
        Write-Info "Installing Sysinternals Strings via Winget (Optional)..."
        winget install --id Microsoft.Sysinternals.Strings -e --accept-source-agreements --accept-package-agreements
    }
}

# --- Install with Chocolatey ---
if ($useChoco) {
    Write-Info "Attempting installations via Chocolatey..."
    if (-not (Test-CommandExists choco)) {
        Write-Warn "Chocolatey command (choco) not found. Skipping Chocolatey installations. You can install it from https://chocolatey.org/install"
    } else {
        $chocoPackages = @(
            "imagemagick.app",   # Or just 'imagemagick' for older versions
            "mediainfo-cli",     # CLI version
            "steghide",
            "exiftool",
            "qpdf",
            "mupdf"              # Provides mutool
            # "file"             # Provides the 'file' command
            # Add more choco package IDs here if found
        )
        Write-Info "Installing/Upgrading Chocolatey packages: $($chocoPackages -join ', ')"
        foreach ($pkg in $chocoPackages) {
             choco install $pkg -y
        }
    }
}

# --- Install Python packages via pip ---
Write-Info "Installing Python tools via pip..."
if (-not (Test-CommandExists pip)) {
     Write-Error "pip command not found. Please ensure Python is installed correctly and pip is in PATH."
} else {
    $pipPackages = @(
        "peepdf"
        # "oletools" # Alternative for pdfid.py
    )
    foreach ($pkg in $pipPackages) {
        Write-Info "Installing $pkg via pip..."
        pip install --upgrade $pkg
    }
}

# --- Install Ruby packages via gem ---
Write-Info "Installing Ruby tools via gem..."
if (-not (Test-CommandExists gem)) {
    Write-Error "gem command not found. Please ensure Ruby is installed correctly and gem is in PATH."
} else {
    $gemPackages = @(
        "origami-pdf",
        "zsteg"
    )
     foreach ($pkg in $gemPackages) {
        Write-Info "Installing $pkg via gem..."
        gem install $pkg
    }
}

# --- Install Didier Stevens Suite via Git ---
if ($installDidierTools) {
    Write-Info "Installing Didier Stevens Suite via Git..."
    if (-not (Test-CommandExists git)) {
        Write-Error "Git is not installed. Cannot clone Didier Stevens Suite."
    } else {
        if (Test-Path -Path $didierStevensDir -PathType Container) {
            Write-Warn "Directory $didierStevensDir already exists. Skipping clone."
        } else {
            Write-Info "Cloning Didier Stevens Suite to $didierStevensDir..."
            # Ensure parent directory exists
            $parentDir = Split-Path -Path $didierStevensDir -Parent
            if (-not (Test-Path -Path $parentDir -PathType Container)) {
                New-Item -ItemType Directory -Force -Path $parentDir | Out-Null
            }
            git clone https://github.com/DidierStevens/DidierStevensSuite.git $didierStevensDir
            if ($LASTEXITCODE -eq 0) {
                 Write-Info "Successfully cloned Didier Stevens Suite."
                 Write-Warn "IMPORTANT: Add $didierStevensDir to your PATH environment variable or call scripts like pdfid.py using the full path (e.g., python '$didierStevensDir\pdfid.py')."
            } else {
                Write-Error "Failed to clone Didier Stevens Suite."
            }
        }
    }
}

# --- Final Checks & Notes ---
Write-Info "Checking installation status for some common tools..."
Test-CommandExists pdfinfo -ErrorAction SilentlyContinue -OutVariable hasPdfInfo | Out-Null; if (-not $hasPdfInfo) { Write-Warn "pdfinfo (from Poppler) not found. Install Poppler manually (e.g., via choco install poppler, or download)." }
Test-CommandExists exiftool -ErrorAction SilentlyContinue -OutVariable hasExiftool | Out-Null; if (-not $hasExiftool) { Write-Warn "Exiftool not found. Installation might have failed or requires PATH update." }
Test-CommandExists qpdf -ErrorAction SilentlyContinue -OutVariable hasQpdf | Out-Null; if (-not $hasQpdf) { Write-Warn "QPDF not found. Installation might have failed or requires PATH update." }
Test-CommandExists mutool -ErrorAction SilentlyContinue -OutVariable hasMutool | Out-Null; if (-not $hasMutool) { Write-Warn "Mutool not found. Installation might have failed or requires PATH update." }


Write-Info "Installation script finished."
Write-Warn "Please verify installations. You may need to RESTART PowerShell/Terminal for PATH changes to take effect."
Write-Warn "Tools like StegDetect are difficult to install on Windows and may require manual steps (like using WSL or Cygwin)."
