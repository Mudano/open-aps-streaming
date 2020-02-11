FROM python:3.6

WORKDIR /open-humans-etl

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD ./entrypoint.sh
