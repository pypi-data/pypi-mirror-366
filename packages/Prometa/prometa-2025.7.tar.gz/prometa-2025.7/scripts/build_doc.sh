#!/usr/bin/env bash
set -euo pipefail

SELF=$(readlink -f "${BASH_SOURCE[0]}")
DIR=${SELF%/*/*}

cd -- "$DIR"

function show_help()
{
  cat << HELP
USAGE

  ${0##*/} [-h] [-v]

OPTIONS

  -h
    Show this help message and exit.

  -v
    Use a Python virtual environment to build the documentation.

HELP
  exit "$1"
}

in_venv=false
while getopts "hv" opt
do
  case "$opt" in
    h) show_help 0 ;;
    v) in_venv=true ;;
    *) show_help 1 ;;
  esac
done

if command -v uv >/dev/null 2>&1
then
  found_uv=true
  pip_cmd=(uv pip)
else
  found_uv=false
  pip_cmd=(pip)
fi

if "$in_venv"
then
  if "$found_uv"
  then
    uv venv venv
    source venv/bin/activate
  else
    python -m venv venv
    source venv/bin/activate
    pip install -U pip
  fi
fi

"${pip_cmd[@]}" install -U -r doc/requirements.txt
sphinx-apidoc -o doc/source -f -H "API Documentation" ./src
sphinx-build -b html doc/source public
# Run again to fix cross-references.
sphinx-build -b html doc/source public
