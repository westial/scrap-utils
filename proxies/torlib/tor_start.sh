#!/bin/bash

set -e

TOR_CONTROL_PORT="$1"
TOR_SOCKS_PORT="$2"
DATA_DIR_ROOT="$3"
EXIT_NODES="$4"

DATA_DIR="$DATA_DIR_ROOT/data$TOR_CONTROL_PORT"
EXIT_NODES_OPTION=""

if [ ! $TOR_CONTROL_PORT ] || [ $TOR_CONTROL_PORT -lt 1 ] \
        || [ $TOR_CONTROL_PORT = "-h" ] || [ $TOR_CONTROL_PORT = "--help" ]; then
    echo "Usage:        ./tor_start.sh CONTROL_PORT SOCKS_PORT DATA_DIR_ROOT"
    echo "Example:      ./tor_start.sh 15000 9050 /tmp/data/us"
    exit 0
fi

if [ ! $TOR_SOCKS_PORT ] || [ $TOR_SOCKS_PORT -lt 1 ]; then
    echo "Please supply a socks port"
    exit 1
fi

if [ ! "$DATA_DIR_ROOT" ] || [ ! -d "$DATA_DIR_ROOT" ]; then
    echo "Please supply a valid data directory root which will contain the data"
    exit 1
fi

if [ "$EXIT_NODES" ]; then
    EXIT_NODES_OPTION=" --ExitNodes $EXIT_NODES"
fi

if [ ! -d "$DATA_DIR" ]; then
    mkdir "$DATA_DIR"
fi

# Take into account that authentication for the control port is disabled. Must be used in secure and controlled environments
echo "Running: tor --RunAsDaemon 1 --CookieAuthentication 0 --HashedControlPassword \"\" --ControlPort $TOR_CONTROL_PORT --PidFile tor$TOR_CONTROL_PORT.pid --SocksPort $TOR_SOCKS_PORT --DataDirectory $DATA_DIR $EXIT_NODES_OPTION"

tor --RunAsDaemon 1 --CookieAuthentication 0 --HashedControlPassword "" \
    --ControlPort $TOR_CONTROL_PORT --PidFile tor$TOR_CONTROL_PORT.pid \
    --SocksPort $TOR_SOCKS_PORT --DataDirectory $DATA_DIR $EXIT_NODES_OPTION
