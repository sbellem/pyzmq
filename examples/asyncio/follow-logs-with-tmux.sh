#!/bin/bash

if [ -z $TMUX ]; then
    echo "tmux is not active, will start new session"
    TMUX_CMD="new-session"
else
    echo "tmux is active, will launch into new window"
    TMUX_CMD="new-window"
fi

tmux $TMUX_CMD "docker-compose logs -f sub; sh" \; \
    splitw -h -p 50 "docker-compose logs -f pubrouter; sh" \; \
    selectp -t 0 \; \
    splitw -v -p 50 "docker-compose logs -f dealer; sh"
