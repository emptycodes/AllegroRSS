FROM python:3-slim

LABEL maintainer="contact@empty.codes"

LABEL name="AllegroRSS"
EXPOSE 80

WORKDIR /app
COPY . /app

VOLUME ["/app/secrets"]

RUN python3 -m pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:80"]
