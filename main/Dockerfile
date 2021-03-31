FROM registry1.dso.mil/ironbank/opensource/python/python38:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

ENV GOOGLE_APPLICATION_CREDENTIALS="key.json"

CMD ["python", "main.py", "prod"]