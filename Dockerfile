FROM alpine:3.12.1
EXPOSE 8000
WORKDIR /usr/src/app

RUN apk add --no-cache \
        uwsgi-python3 \
        python3 \
	py3-pip

COPY . .

RUN pip3 install -r requirements.txt

ENV FLASK_APP app
ENV FLASK_ENV production

STOPSIGNAL SIGINT
CMD exec uwsgi --http-socket 0.0.0.0:8000 \
               --processes 4 \
               --uid uwsgi \
               --buffer-size 65535 \
               --plugins python3 \
               --wsgi app.wsgi:application \
               --touch-reload app/wsgi.py
