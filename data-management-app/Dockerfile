FROM python:3.6

WORKDIR /downloader
ADD wait-for-it.sh .

RUN mkdir setup
ADD setup/requirements.txt ./setup/
RUN pip install -r setup/requirements.txt

ADD . .

CMD python -u run_downloader.py
