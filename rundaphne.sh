#!/bin/bash
cd excelplay-dalalbull/excelplay_dalalbull
echo Running Daphne
pip install channels daphne==2.2.5
daphne -b 0.0.0.0 -p 8003 excelplay_dalalbull.asgi:application
