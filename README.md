# Quick Split

The developer tool for fast, simple A/B tests.

- [Homepage](https://www.quicksplit.io/)
- [API](https://api.quicksplit.io)
- [CLI](https://pypi.org/project/quicksplit/)
- [Strategy](https://docs.google.com/document/d/14eRby5gIR1EO34UlIYWJHo872wBYPtGcp5op8uScp50/edit)
- [Roadmap](https://docs.google.com/document/d/1hDR0D_x5KTq0KHubmEOkesaTK_H2FkPqP6lx9cx0gaY/edit#)
- [Funnel](https://docs.google.com/spreadsheets/d/10Yfp1TJahbu0AgK6nwYBVWmQQYqD9kGv7Jnimgyy7wA/edit#gid=0)

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
