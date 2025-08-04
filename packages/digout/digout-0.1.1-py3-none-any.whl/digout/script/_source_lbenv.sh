#!/usr/bin/env bash
# Usage: _source_lbenv.sh <command>
# This script sources the LbEnv script from the specified path
# and then executes the provided command.

# Set up the environment for the script
set -euo pipefail

log() {
    # Log messages to stderr
    # Usage: log "message"

    if [[ -z "$1" ]]; then
        echo "[DEBUG] No log message provided." 1>&2
        exit 1
    fi

    echo "[DEBUG] $1" 1>&2
}

# Get the command to run.
command=("$@")

# Remove the line arguments (`lbEnv` seems to see them)
set --

lbenv_script="/cvmfs/lhcb.cern.ch/lib/LbEnv"

if [[ -f "$lbenv_script" ]]; then
    log "Sourcing LbEnv script at '${lbenv_script}'."
    set +u # disable 'set -u' for this script in particular
    # shellcheck source=/cvmfs/lhcb.cern.ch/lib/LbEnv
    source "${lbenv_script}"
    set -u # re-enable 'set -u'
else
    log "LbEnv script not found at '${lbenv_script}'. The file won't be sourced."
fi

# Execute the command
log "Executing command: ${command[*]}"
"${command[@]}"
