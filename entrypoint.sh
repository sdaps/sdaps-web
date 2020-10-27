#!/bin/bash

usermod -u $USERID app

screen -dmS celeryWorker bash -c "python -m celery -A sdaps_web worker -E"
screen -dmS svelteBundler bash -c "yarn && yarn dev"
python manage.py runserver 0.0.0.0:8080
