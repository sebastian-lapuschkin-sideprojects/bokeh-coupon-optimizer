#!/bin/bash
PORT=50000
bokeh serve main.py --port $PORT \
--allow-websocket-origin localhost:$PORT \
--allow-websocket-origin panino:$PORT \
--allow-websocket-origin panino.local:$PORT \
