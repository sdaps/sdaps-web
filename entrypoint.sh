#!/bin/bash

screen -dmS celeryWorker bash -c "python -m celery -A sdaps_web worker -E"
python manage.py runserver 0.0.0.0:8080
