#!/bin/bash

python excelplay_dalalbull/manage.py makemigrations && \
	python excelplay-dalalbull/manage.py migrate
cd excelplay-dalalbull/excelplay_dalalbull
gunicorn excelplay_dalalbull.wsgi --bind 0.0.0.0:8002
daphne -b 0.0.0.0 -p 8002 excelplay_dalalbull.asgi:application
