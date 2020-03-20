import json
import click
import os
import sys
import getpass

from cli.config import Config
from cli.client import Client, StagingClient
from cli.printers import Printer


config = Config()
client = Client(config)


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
    ctx.obj = client


@base.command()
@click.option('--email', required=False)
@click.option('--password', required=False)
@click.pass_context
def register(ctx, email, password):
    """
    Create a new account on quicksplit.io
    """

    # ask for password again if not using the flag
    ctx.obj.track(name="register")
    reconfirm_password = password == None

    email = email or input("Email: ")
    password = password or getpass.getpass("Password: ")
    if reconfirm_password:
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match.")
            return

    resp = ctx.obj.register(email, password)
    if ResponseErrorHandler(resp).ok:
        ctx.obj.login(email, password)
        print(f"Created new account for {email}")


@base.command()
@click.option('--email', required=False)
@click.option('--password', required=False)
@click.pass_context
def login(ctx, email, password):
    """
    Log in to quicksplit.io
    """

    ctx.obj.track(name="login")
    email = email or input("Email: ")
    password = password or getpass.getpass("Password: ")

    resp = ctx.obj.login(email=email, password=password)
    if ResponseErrorHandler(resp).ok:
        print("Successfully logged in.")


@base.command()
@click.pass_context
def logout(ctx):
    """
    Log out of quicksplit.io
    """

    ctx.obj.track(name="logout")
    ctx.obj.config.token = None
    ctx.obj.config.dump_config()


@base.command()
@click.pass_context
def whoami(ctx):
    """
    Print the email address of the current account
    """

    ctx.obj.track(name="whoami")
    resp = ctx.obj.get('/user')
    if ResponseErrorHandler(resp).ok:
        print(resp.json()['data']['email'])


@base.command()
@click.pass_context
def config(ctx):
    """
    Print configuration information used by the client
    """

    ctx.obj.track(name="config")
    print(ctx.obj.config)


@base.command()
@click.argument('name', required=True)
@click.pass_context
def create(ctx, name):
    """
    Create a new experiment
    """

    ctx.obj.track(name="create", data={'experiment': name})
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

    ctx.obj.track(name="experiments")
    if staging:
        with StagingClient(ctx.obj) as client:
            resp = client.get('/experiments')
    else:
        resp = ctx.obj.get('/experiments')
    if ResponseErrorHandler(resp).ok:
        data = resp.json()['data']
        Printer(data,
                order=['name', 'subjects_counter', 'active', 'full', 'last_exposure_at'],
                rename={
                    'subjects_counter': 'subjects',
                    'last_exposure_at': 'last exposure',
                },
                empty_data_message="No experiments created yet. \nCreate an experiment with `quicksplit create my-experiment`"
        ).echo()


@base.command()
@click.argument('experiment', required=True)
@click.pass_context
def start(ctx, experiment):
    """
    Start a stopped experiment
    """

    ctx.obj.track(name="start", data={'experiment': experiment})
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

    ctx.obj.track(name="stop", data={'experiment': experiment})
    resp = ctx.obj.post('/deactivate', json={'experiment': experiment})
    if ResponseErrorHandler(resp).ok:
        print(f"Stopped experiment {resp.json()['data']['name']}")


@base.command()
@click.argument('experiment', required=True)
@click.option('--staging', required=False, default=False, is_flag=True)
@click.pass_context
def results(ctx, experiment, staging):
    """
    Print the results of an experiment
    """

    ctx.obj.track(name="results", data={
        'experiment':  experiment,
        'staging':  staging
    })
    if staging:
        environment = "staging"
        with StagingClient(ctx.obj) as client:
            resp = client.post('/results', json={'experiment': experiment})
    else:
        environment = "production"
        resp = ctx.obj.post('/results', json={'experiment': experiment})
    if ResponseErrorHandler(resp).ok:
        data = resp.json()['data']
        table = data['fields']['table']
        Printer(
            table,
            order=['cohort', 'subjects', 'conversion rate', '95% Conf. Interval'],
            empty_data_message=f"No {environment} data collected for experiment {experiment} yet."
        ).echo()
        if data['fields']['significant']:
            print(
                "Congratulations! Your test is statistically significant."
                "You can be confident that the difference in means between"
                "the cohorts is due to the changes you've made, and not due"
                "to random chance."
            )
        else:
            print(
                "Your test is not statistically significant. Either you need"
                " to collect more data, or there is no difference in means"
                " between the cohorts"
            )


@base.command()
@click.option('--staging', default=False, is_flag=True)
@click.pass_context
def recent(ctx, staging):
    """
    Display recent exposure and conversion events
    """

    ctx.obj.track(name="recent")
    if staging:
        environment = "staging"
        with StagingClient(ctx.obj) as client:
            resp = client.get('/recent')
    else:
        environment = "production"
        resp = ctx.obj.get(f'/recent')
    if ResponseErrorHandler(resp).ok:
        data = resp.json()['data']
        Printer(
            data,
            empty_data_message=f"No results received for {environment} environment yet. Please check your logging is working.",
            order=['type', 'experiment', 'subject', 'cohort', 'value', 'last_seen_at'],
            rename={'last_seen_at': 'last seen'}
        ).echo()


@base.command()
@click.argument("log", type=click.Choice(['exposure', 'conversion']))
@click.option('--subject', '-s', required=True)
@click.option('--experiment', '-e', required=True)
@click.option('--cohort', '-c', required=False)
@click.option('--value', '-v', required=False)
@click.option('--staging', required=False, is_flag=True, default=False)
@click.pass_context
def log(ctx, log, subject, experiment, cohort, value, staging):
    """
    Create a new exposure or conversion event
    """

    if value and (log == 'exposure'):
        print("Value is not a valid argument when logging an exposure.")
    if not cohort and (log == 'exposure'):
        print("Can not log an exposure without a cohort.")

    json = {
        'experiment': experiment,
        'subject': subject,
    }

    if log == 'exposure':
        json.update(cohort=cohort)
    else:
        json.update(value=value)

    if staging:
        with StagingClient(ctx.obj) as client:
            resp = client.post(f'/{log}s', json=json)
    else:
        resp = ctx.obj.post(f'/{log}s', json=json)
    if ResponseErrorHandler(resp).ok:
        pass


@base.command()
@click.option('--current', is_flag=True, default=False)
@click.option('--public', is_flag=True, default=False)
@click.option('--private', is_flag=True, default=False)
@click.option('--production', is_flag=True, default=False)
@click.option('--staging', is_flag=True, default=False)
@click.pass_context
def tokens(ctx, current, public, private, production, staging):
    """
    Print the set of available tokens
    """

    ctx.obj.track(name="tokens")
    if current:
        print(ctx.obj.config.token)
        return
    if public and private:
        print("Only one of --public or --private may be used")
        return
    if production and staging:
        print("Only one of --production or --staging may be used")
    resp = ctx.obj.get('/tokens')
    if ResponseErrorHandler(resp).ok:
        data = resp.json()['data']
        if private:
            data = list(filter(lambda x: x['private'] == True, data))
        if public:
            data = list(filter(lambda x: x['private'] == False, data))
        if staging:
            data = list(filter(lambda x: x['environment'] == 'staging', data))
        if production:
            data = list(filter(lambda x: x['environment'] == 'production', data))

        if all([public or private, staging or production]):
            print(data[0]['value'])
        else:
            Printer(data, order=['value', 'private', 'environment']).echo()
