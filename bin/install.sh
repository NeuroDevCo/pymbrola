#!/usr/bin/env bash
set -euo pipefail  # Fail on errors, unset variables, and pipeline errors

# Configuration
REPO="numediart/MBROLA"
VOICES_REPO="numediart/MBROLA-voices"
DEST="/usr/bin/mbrola"
VOICES_DEST="/usr/share/mbrola"
TEMP_DIR=$(mktemp -d)
TRAP_EXIT() { rm -rf "$TEMP_DIR"; }
trap TRAP_EXIT EXIT INT TERM

# Function to fetch latest release
get_latest_release() {
    local repo=$1
    local release
    release=$(curl -sSf "https://api.github.com/repos/${repo}/releases/latest" | \
              jq -r '.tag_name' 2>/dev/null)
    if [[ -z "$release" ]]; then
        echo "Error: Failed to fetch latest release for ${repo}" >&2
        exit 1
    fi
    echo "$release"
}

# Function to prompt for confirmation
confirm_action() {
    local prompt="$1"
    local default=${2:-n}
    local response
    read -r -p "${prompt} [Y/n] " response
    case "$response" in
        [Yy]*) return 0 ;;
        "")    [[ "$default" == "y" ]] && return 0 || return 1 ;;
        [Nn]*) return 1 ;;
        *)     echo "Please answer yes [Y] or no [N]." >&2; confirm_action "$prompt" "$default" ;;
    esac
}

# Check if `jq` is installed
if ! command -v jq &>/dev/null; then
    echo "Error: 'jq' is required but not installed. Install it with your package manager." >&2
    exit 1
fi

# Get latest MBROLA release
RELEASE=$(get_latest_release "$REPO")
echo "Fetching latest MBROLA release: $RELEASE"

# Check if MBROLA already exists
if [[ -f "$DEST" ]]; then
    if ! confirm_action "$DEST already exists. Do you want to replace the current installation?"; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Download and extract MBROLA
FNAME="mbrola-${RELEASE}.tar.gz"
echo "Downloading MBROLA ${RELEASE}..."
curl -sSfL --retry 3 "https://github.com/${REPO}/archive/refs/tags/${RELEASE}.tar.gz" -o "$TEMP_DIR/$FNAME" || {
    echo "Error: Failed to download MBROLA release." >&2
    exit 1
}
tar -xzf "$TEMP_DIR/$FNAME" -C "$TEMP_DIR" || {
    echo "Error: Failed to extract MBROLA archive." >&2
    exit 1
}

# Compile and install MBROLA
cd "$TEMP_DIR/MBROLA-${RELEASE}"
if ! make; then
    echo "Error: Failed to compile MBROLA." >&2
    exit 1
fi
sudo cp Bin/mbrola "$DEST" || {
    echo "Error: Failed to install MBROLA binary." >&2
    exit 1
}

# Download voices
# Fetch the default branch name for the voices repository
DEFAULT_BRANCH=$(curl -sSf "https://api.github.com/repos/${VOICES_REPO}" | jq -r '.default_branch')
if [[ -z "$DEFAULT_BRANCH" ]]; then
    echo "Error: Failed to fetch default branch for ${VOICES_REPO}." >&2
    exit 1
fi

# Download voices using curl with progress bar (using the correct branch)
echo "Downloading MBROLA voices..."
VOICES_ARCHIVE="voices-${DEFAULT_BRANCH}.tar.gz"
curl -L --progress-meter \
    "https://codeload.github.com/${VOICES_REPO}/tar.gz/${DEFAULT_BRANCH}" \
    -o "$TEMP_DIR/$VOICES_ARCHIVE" || {
    echo "Error: Failed to download MBROLA voices." >&2
    exit 1
}

# Verify the file is a valid gzip archive
if ! gzip -t "$TEMP_DIR/$VOICES_ARCHIVE"; then
    echo "Error: Downloaded file is not a valid gzip archive." >&2
    rm -f "$TEMP_DIR/$VOICES_ARCHIVE"
    exit 1
fi

# Extract the voices
tar -xzf "$TEMP_DIR/$VOICES_ARCHIVE" -C "$TEMP_DIR" || {
    echo "Error: Failed to extract MBROLA voices archive." >&2
    exit 1
}

# Copy voices to destination
VOICES_SRC="$TEMP_DIR/$(basename "$VOICES_REPO" .git)-${DEFAULT_BRANCH}"
if [[ -d "$VOICES_DEST" ]]; then
    if ! confirm_action "$VOICES_DEST already exists. Do you want to replace the current voices?"; then
        echo "Skipping voice installation."
    else
        sudo rm -rf "$VOICES_DEST"
        sudo cp -r "$VOICES_SRC/data" "$VOICES_DEST" || {
            echo "Error: Failed to install voices." >&2
            exit 1
        }
    fi
else
    sudo cp -r "$VOICES_SRC/data" "$VOICES_DEST" || {
        echo "Error: Failed to install voices." >&2
        exit 1
    }
fi

echo "Installation successful!"