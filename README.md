
## Development

Start the docker services.

```
docker-compose up --detach
```

## Testing

Run the tests from inside a docker container.

```
docker-compose run --rm web pytest tests/
```

## Deploying
