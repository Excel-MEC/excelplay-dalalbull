#!/bin/bash

python excelplay-dalalbull/excelplay_dalalbull/manage.py makemigrations && \
	python excelplay-dalalbull/excelplay_dalalbull/manage.py migrate
cd excelplay-dalalbull/excelplay_dalalbull
gunicorn excelplay_dalalbull.wsgi --bind 0.0.0.0:8002
daphne -b 0.0.0.0 -p 8003 excelplay_dalalbull.asgi:application
