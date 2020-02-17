FROM python:3.7-slim

ENV PORT=5000

RUN pip install flask \
								flask-sqlalchemy \
								flask-migrate \
								flask-restful \
								flask-shell-ipython \
								psycopg2-binary \
								pytest \
								gunicorn \
								requests

COPY ./app /app
COPY ./tests /tests
COPY ./migrations /migrations

CMD gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT
