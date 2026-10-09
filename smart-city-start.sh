#!/usr/bin/env bash

alacritty -e bash -lc 'docker compose up --build; exec bash' &

alacritty -e bash -lc 'cloudflared tunnel --url http://localhost:8000; exec bash' &

alacritty -e bash -lc 'cloudflared tunnel --url http://localhost:8501; exec bash' &

wait
