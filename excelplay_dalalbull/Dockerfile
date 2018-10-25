FROM python:3.6
 ENV PYTHONUNBUFFERED 1
 RUN mkdir -p /excelplay/excelplay_dalalbull
 WORKDIR /excelplay/excelplay_dalalbull
 ADD requirements.txt /excelplay/excelplay_dalalbull/
 RUN pip install -r requirements.txt
 RUN pip install git+git://github.com/traintraveler/redis-leaderboard.git
 ADD . /excelplay/excelplay_dalalbull