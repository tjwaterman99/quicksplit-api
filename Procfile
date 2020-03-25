web: gunicorn 'app:create_app()' --workers 2 --threads 8 --bind 0.0.0.0:$PORT --log-level INFO
worker: flask worker run

# Only used in development.
stripe: stripe listen -f http://127.0.0.1:5000/webhooks/stripe
