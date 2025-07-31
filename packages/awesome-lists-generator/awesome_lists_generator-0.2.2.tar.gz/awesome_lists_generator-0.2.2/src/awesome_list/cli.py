import logging 
import sys 

import click 

log = logging.getLogger(__name__)


@click.group 
@click.version_option(package_name='awesome-list-generator')
def cli() -> None:
    # log to sys out
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO,
        stream=sys.stdout,
    )

@click.command("generate")
@click.argument("path", type=click.Path(exists=True))
@click.option("--debug", is_flag=True)
def generate(path: str, debug: bool) -> None:
    """Generates an awsome-list markdown page from a yaml file."""
    from awesome_list import generator

    generator.generate_markdown(path, debug)

cli.add_command(generate)
