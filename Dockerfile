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
								requests \
								pandas \
								statsmodels \
								researchpy \
								terminaltables \
								funcy==1.14 \
								flask-cors==3.0.8

COPY ./app /app
COPY ./tests /tests
COPY ./migrations /migrations
COPY ./cli /cli
COPY ./cli/setup.py /setup.py

RUN pip install --editable .

CMD gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT
