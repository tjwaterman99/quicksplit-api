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

Migrate and seed the database.

```
docker-compose exec web flask db upgrade
docker-compose exec web flask seed all
```

### Upgrading a development environment

If you're upgrading the database from a specific version, you may need to run specific seeding commands, as the `flask seed all` command assumes the database has no existing data.

To upgrade a specific version, locate the current revision of the database.

```
docker-compose exec web flask db current
```

Then, pass that version to the command `flask seed revision --up` command.

```
docker-compose exec web flask seed $REVISION --up
```

You should also be able to remove the data for the revision by using `--down`.

```
docker-compose exec web flask seed $REVISION --down
```

### Listening to Stripe webhooks

The application's billing behavior depends on listening to webhooks that Stripe will send. In production, those webhooks get sent to the api.quicksplit.io url, but in development we can use the stripe CLI to forward those events to the app running on localhost.

Install the cli to forward the events.

```
brew install stripe/stripe-cli/stripe
```

Log in if necessary.

```
stripe login
```

Forward the stripe events to the `/webhooks/stripe` route.

```
stripe listen -f http://127.0.0.1:5000/webhooks/stripe
```

## Testing

Run the tests from inside a docker container.

```
docker-compose exec web pytest tests
```

## Deploying

This repository manages releases for both the web api and the CLI.

### API releases

Pushes to master will automatically deploy the `www` build to Netlify and the `api` to Heroku. The Heroku deploy will also automatically run the schema migrations, but will not automatically run any data migrations.

Use the `flask db seed` command to run a specific data migration.

```
heroku run flask db seed $REVISION
```

Note that it can be dangerous to run multiple schema migrations (ie pushes to master) if the later schema migrations assume that a data migration has occurred.

### CLI releases

All releases are completely managed through the Github release feature.

Creating a new release tag will trigger a Github action and deploy the CLI to PyPI. The version of the release on PyPI will be the same as the created tag, since the `setup.py` file uses that value for setting the package's version.
