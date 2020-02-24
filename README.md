# Quick Split

The developer tool for fast, simple A/B tests.

- [Homepage](https://quizzical-mahavira-ad9464.netlify.com/)
- [API](https://api.quicksplit.io)
- [CLI](https://pypi.org/project/quicksplit/)

## Development

Start the docker services.

```
docker-compose up --detach
```

Seed the database.

```
docker-compose exec web flask db upgrade
```

You can create a test user with the CLI that gets installed in the web container.

```
docker-compose exec web quicksplit register \
  --email [youremail@gmail.com] \
  --password [notsecure]
```

## Testing

Run the tests from inside a docker container.

```
docker-compose exec web pytest tests
```
