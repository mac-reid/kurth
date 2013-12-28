#!/bin/bash

# A very hacky method of starting running a new terminal that will infinitely
# read from a certain pipe. We can send commands to start the kurth.py
# server across the pipe and this wil run it.

# Currently uses awesome hard coded paths.

cd ..

if [ ! -p startserver ]; then
    mkfifo startserver
fi

DIR=/home/mareid/kurth/kurth

gnome-terminal --working-directory=$DIR --window-with-profile=Solarized \
               --command="$DIR/tests/loop_on_pipe.sh $DIR/startserver"
