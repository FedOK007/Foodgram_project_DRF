FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY ../ ./

RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]