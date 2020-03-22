# Quick Split

The developer tool for fast, simple A/B tests.

- [Homepage](https://www.quicksplit.io/)
- [API](https://api.quicksplit.io)
- [CLI](https://pypi.org/project/quicksplit/)

## Development

The instructions below are for MacOS. We use a Python virtual environment set up and a local installation of Postgres.

### Installing postgres

Install postgres with Brew.

```
brew install postgresql
```

Start postgres.

```
brew services start postgresql
```

Connect to postgres.

```
psql -U postgres
```

Create a new development database and user for the application.

```sql
CREATE USER "quicksplit" WITH CREATEDB PASSWORD 'password';
CREATE DATABASE "quicksplit-dev" WITH OWNER "quicksplit";
```

### Installing Python and `virtualenv`

```
brew install pyenv
pyenv install 3.7.6
```

Configure your shell to always initialize pyenv. This will modify your path to use the versions of Python that pyenv installs.

```
echo 'eval "$(pyenv init -)"' >> ~/.bashrc  # or ~/.zshrc
```

Confirm that your `python` executable has been installed correctly.

```
which python  # -> /Users/$USER/.pyenv/shims/python
python --version  # -> Python 3.7.6
```

Install `virtualenv` and upgrade `pip`.

```
pip install --upgrade virtualenv pip
```

Create a virtual environment.

```
virtualenv venv
```

Install the Python dependencies.

```
venv/bin/pip install -r requirements.txt
```

You should now be able to start the development web server.

```
venv/bin/flask run
```

Confirm that the application is running successfully.

```
curl http://127.0.0.1:5000

{
	"data": {
		"healthy": true
	},
	"status_code": 200
}
```

### Running migrations

Upgrade to the latest database schema.

```
venv/bin/flask db upgrade
```

Run the seeding commands.

```
venv/bin/flask seed all
```

### Upgrading a development environment

If you're upgrading the database from a specific version, you may need to run specific seeding commands, as the `flask seed all` command assumes the database is being built from scratch.

To upgrade a specific version, locate the current revision of your database.

```
venv/bin/flask db current
```

Then, pass that version to the command `flask seed revision --up` command.

```
venv/bin/flask seed $REVISION --up
```

You should also be able to remove the data for the revision by using `--down`.

```
venv/bin/flask seed $REVISION --down
```

### Configuring billing during development

The application's billing behavior depends on listening to webhooks that Stripe will send. In production, those webhooks get sent to the https://api.quicksplit.io domain, but in development we can use the stripe CLI to forward those events to the local app.

Install the stripe-cli to forward the events.

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

Run the tests. The `test_api.py` collections require the api to be running locally in order to pass.

```
venv/bin/pytest
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
