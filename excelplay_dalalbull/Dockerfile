FROM python:3.6
 ENV PYTHONUNBUFFERED 1
 RUN mkdir -p /excelplay/excelplay-dalalbull
 WORKDIR /excelplay/excelplay-dalalbull
 ADD requirements.txt /excelplay/excelplay-dalalbull/
 RUN pip install -r requirements.txt
 ADD . /excelplay/excelplay-dalalbull