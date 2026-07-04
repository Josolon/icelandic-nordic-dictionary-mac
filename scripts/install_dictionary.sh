#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"
DDK_BIN="/Applications/XcodeAdditionalTools/Utilities/DictionaryDevelopmentKit/bin/build_dict.sh"
DDK_BIN_SPACED="/Applications/Additional Tools for Xcode/Utilities/DictionaryDevelopmentKit/bin/build_dict.sh"

echo "[1/5] Checking platform"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS only."
  exit 1
fi

echo "[2/5] Checking DictionaryDevelopmentKit"
if [[ ! -x "${DDK_BIN}" ]]; then
  echo "Missing DictionaryDevelopmentKit build tool: ${DDK_BIN}"
  if [[ -x "${DDK_BIN_SPACED}" ]]; then
    echo "Detected Xcode tools in a path with spaces."
    echo "Rename it so build tools use a space-free path:"
    echo "  sudo mv \"/Applications/Additional Tools for Xcode\" \"/Applications/XcodeAdditionalTools\""
  else
    echo "Install Xcode Additional Tools and try again."
  fi
  exit 1
fi

echo "[3/5] Checking ISLEX source data"
if [[ ! -f "${REPO_ROOT}/data/ISLEX_dictionary_2023-12.xml" ]]; then
  echo "Missing data/ISLEX_dictionary_2023-12.xml"
  echo "Download it (CC BY-NC-ND 4.0, personal non-commercial use only) from:"
  echo "  https://repository.clarin.is/repository/xmlui/handle/20.500.12537/319"
  echo "and unzip ISLEX_dictionary_2023-12.xml.zip into data/."
  exit 1
fi

echo "[4/5] Creating virtual environment (if needed) and installing islenska"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi
"${PYTHON_BIN}" -m pip install --quiet --upgrade pip
"${PYTHON_BIN}" -m pip install --quiet islenska

echo "[5/5] Building and installing all 12 ISLEX bundles (with BÍN morphology)"
cd "${REPO_ROOT}"
"${PYTHON_BIN}" scripts/build_dict.py --all
make install

echo "Done. Open Dictionary.app Settings and enable the language pairs you want."
