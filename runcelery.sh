cd excelplay-dalalbull/excelplay_dalalbull
echo Starting celery
celery -A excelplay_dalalbull worker -l info -B
