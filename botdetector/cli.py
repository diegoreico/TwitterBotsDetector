import click
from dotenv import load_dotenv

from botdetector.commands import train_ratings_autoencoder

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    load_dotenv('.env')
    if ctx is None:
        ctx.echo('An action should be specified. Try --help to check the options')


