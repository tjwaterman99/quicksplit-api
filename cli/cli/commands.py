import json
import click
import os
import sys


from cli.config import Config
from cli.client import Client, StagingClient
from cli.printers import Printer


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
@click.argument('name', required=True)
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
@click.option('--staging', is_flag=True, required=False, default=False)
@click.pass_context
def experiments(ctx, staging):
    """
    List active experiments
    """

    if staging:
        with StagingClient(ctx.obj) as client:
            resp = client.get('/experiments')
    else:
        resp = ctx.obj.get('/experiments')
    if resp.ok:
        Printer(resp.json()['data'],
                order=['name', 'subjects_counter', 'active', 'full'],
                rename={'subjects_counter': 'subjects'}
        ).echo()
    else:
        print("Failed to load experiments.")


@base.command()
@click.argument('experiment', required=True)
@click.pass_context
def start(ctx, experiment):
    """
    Start a stopped experiment
    """

    resp = ctx.obj.post('/activate', json={'experiment': experiment})
    if resp.ok:
        print(f"Started experiment {resp.json()['data']['name']}")
    elif resp.status_code == 404:
        print("Couldn't find that experiment. Please check its name.")
    else:
        print("Starting experiment failed. Please try again.")


@base.command()
@click.argument('experiment', required=True)
@click.pass_context
def stop(ctx, experiment):
    """
    Stop an active experiment
    """

    resp = ctx.obj.post('/deactivate', json={'experiment': experiment})
    if resp.ok:
        print(f"Stopped experiment {resp.json()['data']['name']}")
    elif resp.status_code == 404:
        print("Couldn't find that experiment. Please check its name.")
    else:
        print("Stopping experiment failed. Please try again.")


@base.command()
@click.argument('experiment', required=True)
@click.option('--staging', required=False, default=False, is_flag=True)
@click.pass_context
def results(ctx, experiment, staging):
    """
    Print the results of an experimence
    """

    if staging:
        with StagingClient(ctx.obj) as client:
            resp = client.get('/results', json={'experiment': experiment})
    else:
        resp = ctx.obj.get('/results', json={'experiment': experiment})
    if resp.ok:
        Printer(resp.json()['data']['table']).echo()
    elif resp.status_code == 404:
        print("Couldn't find that experiment. Please check its name.")
    elif resp.status_code == 403:
        print("Access denied. Please log in.")
    elif resp.status_code == 400:
        print("Experiment has not received any events. Please confirm your logging is working.")
    else:
        print("An unexpected error occured. Please try again later.")


@base.command()
@click.option('--staging', default=False, is_flag=True)
@click.pass_context
def recent(ctx, staging):
    """
    Display recent exposure and conversion events
    """

    if staging:
        with StagingClient(ctx.obj) as client:
            resp = client.get('/recent')
    else:
        resp = ctx.obj.get(f'/recent')
    if resp.ok:
        Printer(resp.json()['data'],
                order=['type', 'experiment', 'subject', 'cohort', 'value', 'updated_at'],
                rename={'updated_at': 'last seen'}
        ).echo()
    else:
        print(resp.status_code)


@base.command()
@click.argument("log", type=click.Choice(['exposure', 'conversion']))
@click.option('--subject', '-s', required=True)
@click.option('--experiment', '-e', required=True)
@click.option('--cohort', '-c', required=True)
@click.option('--value', '-v', required=False)
@click.option('--staging', required=False, is_flag=True, default=False)
@click.pass_context
def log(ctx, log, subject, experiment, cohort, value, staging):
    """
    Create a new exposure or conversion event
    """

    if value and (log == 'exposure'):
        print("Value is not a valid argument when logging an exposure.")

    json = {
        'experiment': experiment,
        'cohort': cohort,
        'subject': subject,
        'value': value
    }

    if staging:
        with StagingClient(ctx.obj) as client:
            resp = client.post(f'/{log}s', json=json)
    else:
        resp = ctx.obj.post(f'/{log}s', json=json)
    print(resp.status_code)


@base.command()
@click.option('--current', is_flag=True, default=False)
@click.pass_context
def tokens(ctx, current):
    """
    Print the set of available tokens
    """

    if current:
        print(ctx.obj.config.token)
        return
    resp = ctx.obj.get('/tokens')
    if resp.ok:
        Printer(resp.json()['data'], order=['value', 'private', 'environment']).echo()
    elif resp.status_code == 403:
        print("Please log in to access tokens")
    else:
        print("An unknown error occured. Please try again later")
