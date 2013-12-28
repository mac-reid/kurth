#!/bin/bash

PIPE=$1

while true; do
    sh -c "$(< $PIPE)"
done
