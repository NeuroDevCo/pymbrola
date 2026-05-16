#!/usr/bin/env bash
#
# MBROLA and MBROLA-voices installer
# Usage: ./script.sh [OPTIONS]

set -euo pipefail

# --- Configuration ---
readonly REPO="numediart/MBROLA"
readonly VOICES_REPO="numediart/MBROLA-voices"
readonly DEST="/usr/bin/mbrola"
readonly VOICES_DEST="/usr/share/mbrola"
readonly TEMP_DIR="$(mktemp -d)"
TRAP_EXIT() {
    rm -rf "${TEMP_DIR}"
}
trap TRAP_EXIT EXIT INT TERM

# --- Defaults ---
VOICE=()

# --- Functions ---

# Download a specific MBROLA voice
download_voice() {
    local voice="${1}"
    local voices_repo_dir="${TEMP_DIR}/MBROLA-voices-${voice}"
    local voice_src

    echo "Downloading MBROLA voice '${voice}'..."

    if ! command -v git &>/dev/null; then
        echo "Error: 'git' is required but not installed." >&2
        exit 1
    fi

    git clone --depth 1 --filter=blob:none --sparse "https://github.com/${VOICES_REPO}.git" "${voices_repo_dir}" || {
        echo "Error: Failed to clone MBROLA-voices repository." >&2
        exit 1
    }

    (
        cd "${voices_repo_dir}" || exit 1
        git sparse-checkout init --cone
        git sparse-checkout set "data/${voice}" || {
            echo "Error: Failed to sparse-checkout voice '${voice}'." >&2
            exit 1
        }
    )

    voice_src="${voices_repo_dir}/data/${voice}"
    if [[ ! -d "${voice_src}" ]]; then
        echo "Error: Voice '${voice}' not found in the repository." >&2
        exit 1
    fi

    if [[ -d "${VOICES_DEST}" ]]; then
        cp -r "${voice_src}" "${VOICES_DEST}/" || {
            echo "Error: Failed to install voice '${voice}'." >&2
            exit 1
        }
    else
        mkdir -p "${VOICES_DEST}"
        cp -r "${voice_src}" "${VOICES_DEST}/" || {
            echo "Error: Failed to install voice '${voice}'." >&2
            exit 1
        }
    fi
}

# Fetch the latest release tag from a GitHub repo
get_latest_release() {
    local repo="${1}"
    local release

    release=$(curl -sSf "https://api.github.com/repos/${repo}/releases/latest" | jq -r '.tag_name' 2>/dev/null)
    if [[ -z "${release}" ]]; then
        echo "Error: Failed to fetch latest release for ${repo}." >&2
        exit 1
    fi
    echo "${release}"
}

# Prompt for user confirmation
confirm_action() {
    local prompt="${1}"
    local default="${2:-n}"
    local response

    read -r -p "${prompt} [Y/n] " response
    case "${response}" in
        [Yy]*) return 0 ;;
        "")    [[ "${default}" == "y" ]] && return 0 || return 1 ;;
        [Nn]*) return 1 ;;
        *)
            echo "Please answer yes [Y] or no [N]." >&2
            confirm_action "${prompt}" "${default}"
            ;;
    esac
}

# --- Main Script ---

# Check if running as root
if [[ ${EUID} -ne 0 ]]; then
    echo "Error: This script must be run as root (use sudo)." >&2
    exit 1
fi

# Check if jq is installed
if ! command -v jq &>/dev/null; then
    echo "Error: 'jq' is required but not installed." >&2
    exit 1
fi

# Parse command-line arguments
while [[ ${#} -gt 0 ]]; do
    case "${1}" in
        -v|--voice)
            shift
            while [[ ${#} -gt 0 && "${1:-}" != -* ]]; do
                VOICE+=("${1}")
                shift
            done
            ;;
        -h|--help)
            echo "Usage: ${0} [OPTIONS]"
            echo "Options:"
            echo "  -v, --voice VOICE1 [VOICE2 ...]   Specify one or more MBROLA voices to download (e.g., 'it4 fr4')"
            echo "                                       Use 'all' to download all voices."
            echo "                                       If not specified, no voices are downloaded."
            echo "  -h, --help                          Show this help message"
            exit 0
            ;;
        *)
            echo "Error: Unknown option '${1}'." >&2
            exit 1
            ;;
    esac
done

# Get latest MBROLA release
RELEASE=$(get_latest_release "${REPO}")
echo "Fetching latest MBROLA release: ${RELEASE}"

# Check if MBROLA already exists
if [[ -f "${DEST}" ]]; then
    if ! confirm_action "${DEST} already exists. Do you want to replace the current installation?"; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Download and extract MBROLA
FNAME="mbrola-${RELEASE}.tar.gz"
echo "Downloading MBROLA ${RELEASE}..."
curl -sSfL --retry 3 "https://github.com/${REPO}/archive/refs/tags/${RELEASE}.tar.gz" -o "${TEMP_DIR}/${FNAME}" || {
    echo "Error: Failed to download MBROLA release." >&2
    exit 1
}
tar -xzf "${TEMP_DIR}/${FNAME}" -C "${TEMP_DIR}" || {
    echo "Error: Failed to extract MBROLA archive." >&2
    exit 1
}

# Compile and install MBROLA
cd "${TEMP_DIR}/MBROLA-${RELEASE}" || exit 1
if ! make; then
    echo "Error: Failed to compile MBROLA." >&2
    exit 1
fi
mv Bin/mbrola "${DEST}" || {
    echo "Error: Failed to install MBROLA binary." >&2
    exit 1
}

# Handle voice download
if [[ ${#VOICE[@]} -gt 0 ]]; then
    DEFAULT_BRANCH=$(curl -sSf "https://api.github.com/repos/${VOICES_REPO}" | jq -r '.default_branch')
    if [[ -z "${DEFAULT_BRANCH}" ]]; then
        echo "Error: Failed to fetch default branch for ${VOICES_REPO}." >&2
        exit 1
    fi

    # Check if "all" is specified
    if [[ " ${VOICE[*]} " == *" all "* ]]; then
        if [[ ${#VOICE[@]} -gt 1 ]]; then
            echo "Error: Cannot specify 'all' with other voices." >&2
            exit 1
        fi

        # Download all voices
        echo "Downloading all MBROLA voices..."
        VOICES_ARCHIVE="voices-${DEFAULT_BRANCH}.tar.gz"
        curl -L --progress-meter \
            "https://codeload.github.com/${VOICES_REPO}/tar.gz/${DEFAULT_BRANCH}" \
            -o "${TEMP_DIR}/${VOICES_ARCHIVE}" || {
            echo "Error: Failed to download MBROLA voices." >&2
            exit 1
        }

        if ! gzip -t "${TEMP_DIR}/${VOICES_ARCHIVE}"; then
            echo "Error: Downloaded file is not a valid gzip archive." >&2
            rm -f "${TEMP_DIR}/${VOICES_ARCHIVE}"
            exit 1
        fi

        tar -xzf "${TEMP_DIR}/${VOICES_ARCHIVE}" -C "${TEMP_DIR}" || {
            echo "Error: Failed to extract MBROLA voices archive." >&2
            exit 1
        }

        VOICES_SRC="${TEMP_DIR}/$(basename "${VOICES_REPO}" .git)-${DEFAULT_BRANCH}"

        if [[ -d "${VOICES_DEST}" ]]; then
            if ! confirm_action "${VOICES_DEST} already exists. Do you want to replace the current voices?"; then
                echo "Skipping voice installation."
            else
                rm -rf "${VOICES_DEST}"
                mkdir -p "${VOICES_DEST}"
                cp -r "${VOICES_SRC}/data"/. "${VOICES_DEST}/" || {
                    echo "Error: Failed to install voices." >&2
                    exit 1
                }
            fi
        else
            mkdir -p "${VOICES_DEST}"
            cp -r "${VOICES_SRC}/data"/. "${VOICES_DEST}/" || {
                echo "Error: Failed to install voices." >&2
                exit 1
            }
        fi
    else
        # Download each specified voice
        for voice in "${VOICE[@]}"; do
            download_voice "${voice}"
        done
    fi
else
    echo "No voice specified. Skipping voice installation."
fi

echo "Installation successful!"
exit 0