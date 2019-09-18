cd excelplay-dalalbull/excelplay_dalalbull
echo Starting celery
pip install kombu==4.3.0
celery -A excelplay_dalalbull worker -l info -B
