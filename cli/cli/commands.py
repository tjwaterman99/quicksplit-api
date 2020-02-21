import json
import click
import os
import sys


from cli.config import Config
from cli.client import Client, StagingClient
from cli.printers import Printer


class ResponseErrorHandler(object):
    def __init__(self, response):
        self.response = response

    @property
    def ok(self):
        if self.response.ok:
            return True
        else:
            try:
                message = self.response.json().get('message')
            except Exception as exc:
                message = "A client error occured. Please try again later."
            print(message + f' [code={self.response.status_code}]')
            return False


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
    if ResponseErrorHandler(resp).ok:
        ctx.obj.login(email, password)
        print(f"Created new account for {email}")


@base.command()
@click.option('--email', required=True)
@click.option('--password', required=True)
@click.pass_context
def login(ctx, email, password):
    """
    Log in to quicksplit.io
    """

    resp = ctx.obj.login(email=email, password=password)
    if ResponseErrorHandler(resp).ok:
        print("Successfully logged in.")


@base.command()
@click.pass_context
def whoami(ctx):
    """
    Print the email address of the current account
    """

    resp = ctx.obj.get('/user')
    if ResponseErrorHandler(resp).ok:
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
    if ResponseErrorHandler(resp).ok:
        print(f"Successfully created new experiment {name}")


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
    if ResponseErrorHandler(resp).ok:
        Printer(resp.json()['data'],
                order=['name', 'subjects_counter', 'active', 'full'],
                rename={'subjects_counter': 'subjects'}
        ).echo()


@base.command()
@click.argument('experiment', required=True)
@click.pass_context
def start(ctx, experiment):
    """
    Start a stopped experiment
    """

    resp = ctx.obj.post('/activate', json={'experiment': experiment})
    if ResponseErrorHandler(resp).ok:
        print(f"Started experiment {resp.json()['data']['name']}")



@base.command()
@click.argument('experiment', required=True)
@click.pass_context
def stop(ctx, experiment):
    """
    Stop an active experiment
    """

    resp = ctx.obj.post('/deactivate', json={'experiment': experiment})
    if ResponseErrorHandler(resp).ok:
        print(f"Stopped experiment {resp.json()['data']['name']}")


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
    if ResponseErrorHandler(resp).ok:
        Printer(resp.json()['data']['table']).echo()


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
    if ResponseErrorHandler(resp).ok:
        Printer(resp.json()['data'],
                order=['type', 'experiment', 'subject', 'cohort', 'value', 'updated_at'],
                rename={'updated_at': 'last seen'}
        ).echo()


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
    if ResponseErrorHandler(resp).ok:
        pass


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
    if ResponseErrorHandler(resp).ok:
        Printer(resp.json()['data'], order=['value', 'private', 'environment']).echo()
