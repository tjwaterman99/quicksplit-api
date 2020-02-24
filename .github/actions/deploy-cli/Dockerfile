FROM python:3.7-slim

RUN pip install twine setuptools wheel

COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
