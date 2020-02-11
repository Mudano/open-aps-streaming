FROM python:3.6

WORKDIR /downloader

RUN mkdir temp_files

RUN mkdir setup
ADD setup/requirements.txt ./setup/
RUN pip install -r setup/requirements.txt

ADD . .

CMD python -u run_downloader.py
