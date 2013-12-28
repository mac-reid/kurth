#!/bin/bash

# We want a new terminal that infinitely reads from a certain pipe. We can
# then send commands over that pipe to run against the server.

# Currently uses awesome hard coded paths.

if ! type sshpass > /dev/null; then
    echo 'sshpass not installed. Cannot run tests.'
    exit 1
fi

if [ ! -p tests ]; then
    mkfifo tests
fi

DIR=/home/mareid/kurth/kurth/

gnome-terminal --working-directory=$DIR --window-with-profile=Solarized \
               --command="$DIR/tests/loop_on_pipe.sh $DIR/tests/tests"
