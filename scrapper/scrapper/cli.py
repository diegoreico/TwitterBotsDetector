import click
import logging
from dotenv import load_dotenv

from scrapper.usecases.ScrapTweetsFromFile import ScrapTweetsFromFile

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):

    if ctx is not None:
        click.echo("An action should be specified. Try --help to check the options")


@main.command("hello")
def hello():
    """ Says hello (wave) """

    logging.info("hello")


@main.command("scrap")
@click.option("-f", "--file")
@click.option("-u", "--user-id")
@click.option("-U", "--user-name")
def scrap(file, user_id, user_name):
    """ gets twitter info from given parameters """

    logging.info("invoking scrap command")

    if not file is None:
        usecase = ScrapTweetsFromFile(file)
        usecase.execute()

    elif not user_id is None:
        # todo: scrap from user id
        pass
    elif not user_name is None:
        # todo: screao from user name
        pass
    else:
        logging.warn("you should provide one option")


if __name__ == "__main__":
    # execute only if run as a script
    print("MAIN")
