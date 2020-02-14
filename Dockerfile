FROM python:3.7-slim

ENV PORT=5000

RUN pip install flask sqlalchemy pytest gunicorn

COPY ./app /app
COPY ./tests /tests

CMD gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT
