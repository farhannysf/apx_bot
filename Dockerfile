FROM python:3.7

WORKDIR /app

RUN set -eux \
  && apt-get update 

RUN pip install requests

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

ENV PORT=1337 GOOGLE_APPLICATION_CREDENTIALS="key.json"

EXPOSE 1337

CMD ["python", "main.py", "prod"]