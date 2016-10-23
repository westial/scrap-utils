#!/bin/bash

set -e

TOR_CONTROL_PORT="$1"
TOR_SOCKS_PORT="$2"
DATA_DIR="$3"

if [ ! $TOR_CONTROL_PORT ] || [ $TOR_CONTROL_PORT -lt 1 ] \
        || [ ! $TOR_SOCKS_PORT ] || [ $TOR_SOCKS_PORT -lt 1 ] \
        || [ ! "$DATA_DIR" ] || [ -d "$DATA_DIR" ]; then
    echo "Please supply a control and socks port and a valid data directory"
    echo "Example: ./tor_start.sh 15000 9050 /tmp/data/us"
    exit 1
fi

# Take into account that authentication for the control port is disabled. Must be used in secure and controlled environments
echo "Running: tor --RunAsDaemon 1 --CookieAuthentication 0 --HashedControlPassword \"\" --ControlPort $TOR_CONTROL_PORT --PidFile tor$TOR_CONTROL_PORT.pid --SocksPort $TOR_SOCKS_PORT --DataDirectory $DATA_DIR"

tor --RunAsDaemon 1 --CookieAuthentication 0 --HashedControlPassword "" --ControlPort $TOR_CONTROL_PORT --PidFile tor$TOR_CONTROL_PORT.pid --SocksPort $TOR_SOCKS_PORT --DataDirectory $DATA_DIR
done
