FROM python:3

RUN apt-get update && apt-get install -y make
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV FLASK_APP app.py
CMD ["make", "run"]
