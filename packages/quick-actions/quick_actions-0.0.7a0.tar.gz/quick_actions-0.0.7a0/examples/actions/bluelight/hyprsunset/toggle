#!/usr/bin/env bash

TOGGLE_KEY="/me/leswell/hyprsunset-toggle"


# Check the current state using dconf
if [ "$(dconf read "$TOGGLE_KEY")" == "true" ]; then
    dconf write "$TOGGLE_KEY" "false"
    killall hyprsunset
else
    dconf write "$TOGGLE_KEY" "true"
    hyprsunset -t 5000
fi
