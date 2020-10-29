#!/bin/bash

rm -rf /tmp/logs && mkdir -p /tmp/logs

screen -L -Logfile /tmp/logs/celery.log -dmS celeryWorker bash -c "python -m celery -A sdaps_web worker -E"
screen -S celeryWorker -X colon "logfile flush 0^M"
# screen -L -Logfile /tmp/logs/svelte.log -dmS svelteBundler bash -c "yarn && yarn dev"
python manage.py runserver 0.0.0.0:8080
