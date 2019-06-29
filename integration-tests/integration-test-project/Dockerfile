FROM python:3.6

WORKDIR /integration-tests

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD test-scripts ./test-scripts

CMD pytest
