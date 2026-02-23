#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

on_error() {
  local exit_code=$?
  local line_no=$1
  echo "Error: command failed on line ${line_no} with exit code ${exit_code}." >&2
  exit "${exit_code}"
}
trap 'on_error ${LINENO}' ERR

# Function to download and install a wheel from GitHub releases
# Usage: download_and_install_wheel <github_repo> <package_name> <version_tag> [wheel_name_prefix]
# Example: download_and_install_wheel "yayfalafels/homebudget" "homebudget" "v2.0.6" "homebudget"
# Example: download_and_install_wheel "taylorhickem/sqlite-gsheet" "sqlite-gsheet" "2.0.0" "sqlite_gsheet"
download_and_install_wheel() {
  local gh_repo=$1
  local package_name=$2
  local version_tag=$3  # Can be "v2.0.0" or "2.0.0" depending on the repo
  local wheel_name_prefix=${4:-$package_name}
  # Extract version without "v" prefix for wheel filename
  local version=${version_tag#v}
  local wheel_file="${wheel_name_prefix}-${version}-py3-none-any.whl"
  local download_url="https://github.com/${gh_repo}/releases/download/${version_tag}/${wheel_file}"
  
  echo "INFO: Processing package: ${package_name} (version ${version})"
  
  # Clean up any existing wheel files for this package
  echo "INFO: Cleaning up any existing ${package_name} wheel files..."
  rm -f "${wheel_name_prefix}-"*.whl 2>/dev/null || true
  
  # Download with retries
  local max_retries=3
  local retry_count=0
  while [ $retry_count -lt $max_retries ]; do
    echo "INFO: Download attempt $((retry_count + 1))/$max_retries from: ${download_url}"
    
    if curl -L -f -o "$wheel_file" "$download_url"; then
      break
    else
      retry_count=$((retry_count + 1))
      if [ $retry_count -lt $max_retries ]; then
        echo "WARN: Download failed, retrying in 2 seconds..."
        sleep 2
      fi
    fi
  done
  
  if [ $retry_count -eq $max_retries ]; then
    echo "ERROR: Failed to download ${package_name} wheel after $max_retries attempts." >&2
    echo "ERROR: URL: ${download_url}" >&2
    echo "ERROR: Check that version tag ${version_tag} is valid and accessible." >&2
    return 1
  fi
  
  # Validate downloaded file exists
  if [[ ! -f "$wheel_file" ]]; then
    echo "ERROR: Wheel file was not created after download: ${wheel_file}" >&2
    return 1
  fi
  
  # Check file size (wheel files should be at least 10KB)
  local file_size=$(stat -f%z "$wheel_file" 2>/dev/null || stat -c%s "$wheel_file" 2>/dev/null || echo 0)
  if [ "$file_size" -lt 10000 ]; then
    echo "ERROR: Downloaded wheel file is suspiciously small (${file_size} bytes). File may be corrupted." >&2
    rm -f "$wheel_file"
    return 1
  fi
  
  echo "INFO: Successfully downloaded: ${wheel_file} ($(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo "${file_size} bytes"))"
  
  # Install the wheel
  echo "INFO: Installing ${package_name} package..."
  if ! python -m pip install "$wheel_file"; then
    echo "ERROR: Failed to install ${package_name}: ${wheel_file}" >&2
    return 1
  fi
  echo "INFO: ${package_name} installed successfully"
  
  return 0
}

# Function to ensure Python is available
# Uses PYTHONVERSION variable (default: 12 for Python 3.12)
# Downloads and installs if not found
ensure_python() {
  local python_exe=""
  local python_cmd="python3.${PYTHONVERSION}"
  local python_version="3.${PYTHONVERSION}"
  
  # Try to find python${PYTHONVERSION} or python.exe from installation
  echo "INFO: Checking for Python ${python_version}..." >&2
  
  # Check common locations
  if command -v "${python_cmd}" &> /dev/null; then
    python_exe="${python_cmd}"
    echo "INFO: Found ${python_cmd} in PATH" >&2
  fi
  
  # If Python not found, prepare to download and install
  if [[ -z "$python_exe" ]]; then
    echo "WARN: Python ${python_version} not found in PATH" >&2
    echo "INFO: Downloading Python ${python_version} installer..." >&2
    
    local python_full_version="${python_version}.0"
    local installer_url="https://www.python.org/ftp/python/${python_full_version}/python-${python_full_version}-amd64.exe"
    local installer_file="python-${python_full_version}-amd64.exe"
    
    if ! curl -L -f -o "$installer_file" "$installer_url"; then
      echo "ERROR: Failed to download Python ${python_version} installer from: ${installer_url}" >&2
      return 1
    fi
    echo "INFO: Downloaded Python ${python_version} installer" >&2
    
    echo "INFO: Installing Python ${python_version} (this may require admin privileges)..." >&2
    # Install Python with options for all users and add to PATH
    if ! "./$installer_file" /quiet InstallAllUsers=1 PrependPath=1; then
      echo "ERROR: Failed to install Python ${python_version}. You may need to run this as Administrator." >&2
      echo "ERROR: Installer file: ${installer_file}" >&2
      return 1
    fi
    echo "INFO: Python ${python_version} installed successfully" >&2
    
    # Clean up installer
    rm -f "$installer_file"
    
    # Try to find it again
    if command -v "${python_cmd}" &> /dev/null; then
      python_exe="${python_cmd}"
    elif command -v py &> /dev/null && py -3.${PYTHONVERSION} --version &> /dev/null; then
      python_exe="py -3.${PYTHONVERSION}"
    else
      echo "ERROR: Python ${python_version} installation completed but executable not found in PATH" >&2
      return 1
    fi
  fi
  
  echo "$python_exe"
  return 0
}

# Python version configuration
PYTHONVERSION="${PYTHONVERSION:-12}"

repo_root="$(git rev-parse --show-toplevel)"
env_file="${ENV_FILE:-${repo_root}/.env}"
ENV_PATH="env/Scripts"
HB_WRAPPER="homebudget"
SQLGSHEET="sqlite-gsheet"
HB_WRAPPER_GH_REPO="yayfalafels/$HB_WRAPPER"
SQLGSHEET_GH_REPO="taylorhickem/$SQLGSHEET"
HB_WRAPPER_VERSION="${HB_WRAPPER_VERSION:-v2.0.6}"
SQLGSHEET_VERSION="${SQLGSHEET_VERSION:-v2.0.1}"

echo "INFO: Starting setup process..."
echo "INFO: Repository root: ${repo_root}"

# Check environment file
echo "INFO: Checking for environment configuration file..."
if [[ ! -f "${env_file}" ]]; then
  echo "ERROR: Missing ${env_file}." >&2
  echo "ERROR: Create it with the following variables:" >&2
  echo "  - GIT_USER_NAME" >&2
  echo "  - GIT_USER_EMAIL" >&2
  echo "  - GIT_CRED_USERNAME" >&2
  echo "  - HB_WRAPPER_VERSION" >&2
  echo "  - SQLGSHEET_VERSION" >&2
  exit 1
fi
echo "INFO: Environment file found: ${env_file}"

# Source environment variables
set -a
# shellcheck disable=SC1090
if ! source "${env_file}"; then
  echo "ERROR: Failed to source environment file: ${env_file}" >&2
  exit 1
fi
set +a
echo "INFO: Environment variables loaded successfully"

# Ensure version tags have correct format
# Both homebudget and sqlite-gsheet use v-prefixed tags
if [[ ! "$HB_WRAPPER_VERSION" =~ ^v ]]; then
  HB_WRAPPER_VERSION="v${HB_WRAPPER_VERSION}"
  echo "INFO: Normalized homebudget version to: ${HB_WRAPPER_VERSION}"
fi

if [[ ! "$SQLGSHEET_VERSION" =~ ^v ]]; then
  SQLGSHEET_VERSION="v${SQLGSHEET_VERSION}"
  echo "INFO: Normalized sqlite-gsheet version to: ${SQLGSHEET_VERSION}"
fi

# Ensure Python is available
echo "INFO: Ensuring Python 3.${PYTHONVERSION} is available..."
if ! PYTHON_EXE=$(ensure_python); then
  exit 1
fi
echo "INFO: Using Python: $PYTHON_EXE"

# Create or verify virtual environment
echo "INFO: Checking virtual environment..."
if [[ ! -d "${repo_root}/env" ]]; then
  echo "INFO: Creating Python 3.${PYTHONVERSION} virtual environment at: ${repo_root}/env"
  if ! $PYTHON_EXE -m venv "${repo_root}/env"; then
    echo "ERROR: Failed to create virtual environment at: ${repo_root}/env" >&2
    exit 1
  fi
  echo "INFO: Virtual environment created successfully"
else
  echo "INFO: Virtual environment already exists at: ${repo_root}/env"
fi

# Activate virtual environment and install packages
echo "INFO: Activating virtual environment..."
if ! source "${repo_root}/${ENV_PATH}/activate"; then
  echo "ERROR: Failed to activate virtual environment at: ${repo_root}/${ENV_PATH}/activate" >&2
  exit 1
fi
echo "INFO: Virtual environment activated"

echo "INFO: Upgrading pip..."
if ! python -m pip install --upgrade pip; then
  echo "WARN: pip upgrade failed (known Windows issue), continuing with current pip version" >&2
fi
echo "INFO: pip is ready"

# Download and install wheels
if ! download_and_install_wheel "$HB_WRAPPER_GH_REPO" "$HB_WRAPPER" "$HB_WRAPPER_VERSION" "homebudget"; then
  exit 1
fi

if ! download_and_install_wheel "$SQLGSHEET_GH_REPO" "$SQLGSHEET" "$SQLGSHEET_VERSION" "sqlite_gsheet"; then
  exit 1
fi

echo "INFO: Setup completed successfully!"
