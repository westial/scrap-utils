#!/bin/bash

TOR_CONTROL_PORT="$1"
EXPECT_SCRIPT_DIR=`dirname $0`

if [ ! $TOR_CONTROL_PORT ] || [ $TOR_CONTROL_PORT -lt 1 ]; then
    echo "Please supply an instance incremental id"
    echo "Example: ./tor_reload_torrc.sh 15001"
    exit 1
fi

"$EXPECT_SCRIPT_DIR/tor_reload_torrc.exp" $TOR_CONTROL_PORT