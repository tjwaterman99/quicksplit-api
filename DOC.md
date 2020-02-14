# Quick Split

The quick, simple way to run experiments on your product.

## Get started

Install the CLI, which requires having `pip` installed with Python 3.6+

```
pip --version
```

You should see version information similar to the following.

```
pip 19.3.1 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)
```

Install the CLI.

```
pip install quicksplit
```

The CLI provides commands for registering  an account and managing your experiments.

```
split register
```

You'll be prompted for a username (email) and password.

After confirming your email, you can create an experiment.

```
split experiments create --name homepage-test
```

The CLI will print confirmation information about your experiment.

```
{
	active: true,
	name: "homepage-test",
	...
}
```

## Routes

`/experiments` GET, POST
`/experiments/:experiment_id` GET, PUT
`/experiments/:experiment_id/results` GET
`/exposures` POST
`/conversions` POST
`/users` GET
