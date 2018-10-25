#!/bin/bash
cd excelplay-dalalbull/excelplay_dalalbull
echo Running Daphne
daphne -b 0.0.0.0 -p 8003 excelplay_dalalbull.asgi:application