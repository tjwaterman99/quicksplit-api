import click
import os
import sys


from cli.config import Config
from cli.client import Client


@click.group()
@click.pass_context
def base(ctx):
    """
    CLI for managing Quick Split A/B tests
    """

    if '.' not in sys.path:
        sys.path.append('.')
    config = Config()
    client = Client(config)
    ctx.obj = client


@base.command()
@click.option('--email', required=True)
@click.option('--password', required=True)
@click.pass_context
def register(ctx, email, password):
    """
    Create a new account on quicksplit.io
    """

    resp = ctx.obj.register(email, password)
    if resp.ok:
        ctx.obj.login(email, password)
        print(f"Created new account for {email}")
    else:
        print("Failed to create new account. Please try a different email.")


@base.command()
@click.option('--email', required=True)
@click.option('--password', required=True)
@click.pass_context
def login(ctx, email, password):
    """
    Log in to quicksplit.io
    """

    resp = ctx.obj.login(email=email, password=password)
    if resp.ok:
        print("Successfully logged in.")
    else:
        print("Invalid email/password combination.")


@base.command()
@click.pass_context
def token(ctx):
    """
    Print the current authentication token in use
    """

    print(ctx.obj.config.token)


@base.command()
@click.pass_context
def whoami(ctx):
    """
    Print the email address of the current account
    """

    resp = ctx.obj.get('/user')
    if resp.ok:
        print(resp.json()['data']['email'])


@base.command()
@click.pass_context
def config(ctx):
    """
    Print configuration information used by the client
    """

    print(ctx.obj.config)


@base.command()
@click.option('--name', required=True)
@click.pass_context
def create(ctx, name):
    """
    Create a new experiment
    """

    resp = ctx.obj.post('/experiments', json={'name': name})
    if resp.ok:
        print(resp.json()['data'])
    else:
        print("Creating experiment failed. Please try a different name.")


@base.command()
@click.pass_context
def experiments(ctx):
    """
    List active experiments
    """

    resp = ctx.obj.get('/experiments')
    if resp.ok:
        print(resp.json()['data'])
    else:
        print("Failed to load experiments.")


@base.command()
@click.option('--name', required=True)
@click.pass_context
def start(ctx, name):
    """
    Start a stopped experiment
    """

    resp = ctx.obj.post('/activate', json={'experiment': name})
    if resp.ok:
        print(f"Started experiment {resp.json()['data']['name']}")
    elif resp.status_code == 404:
        print("Couldn't find that experiment. Please check its name.")
    else:
        print("Starting experiment failed. Please try again.")


@base.command()
@click.option('--name', required=True)
@click.pass_context
def stop(ctx, name):
    """
    Stop an active experiment
    """

    resp = ctx.obj.post('/deactivate', json={'experiment': name})
    if resp.ok:
        print(f"Stopped experiment {resp.json()['data']['name']}")
    elif resp.status_code == 404:
        print("Couldn't find that experiment. Please check its name.")
    else:
        print("Stopping experiment failed. Please try again.")
