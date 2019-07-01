FROM python:3.6

WORKDIR /registration-site
ADD wait-for-it.sh .

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD python manage.py runserver 0.0.0.0:8000
