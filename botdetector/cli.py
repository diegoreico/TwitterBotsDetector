import click
from dotenv import load_dotenv
from botdetector.commands import create_http_api


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    load_dotenv('.env')
    print('main command')
    if ctx is None:
        ctx.echo('An action should be specified. Try --help to check the options')


@main.command()
def train():
    load_dotenv('.env')
    print('train command')

@main.command()
def api():
    load_dotenv('.env')
    create_http_api()
    print('api command')


