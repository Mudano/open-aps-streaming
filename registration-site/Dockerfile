FROM python:3.6

WORKDIR /registration-site

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD ./entrypoint.sh
