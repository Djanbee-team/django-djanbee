import click
from .commands import LaunchContainer, SetupContainer, ConfigureContainer
from .core import AppContainer


@click.group()
def cli():
    """Djanbee deployment tool"""
    pass


@cli.command()
# TODO: Add option for manual path
def launch(path=""):
    """Launch Django server deployment"""
    try:
        app = AppContainer.get_instance()
        container = LaunchContainer.create(app)
        container.manager.launch_project(path)
    except Exception as e:
        print(f"Error: {e}")


@cli.command()
# TODO add commands to specify which env and functionallity for multiple envs
def setup():
    """Setup Django project environment"""
    try:
        app = AppContainer.get_instance()
        container = SetupContainer.create(app)
        container.manager.setup_project()
    except Exception as e:
        print(f"Error: {e}")


@cli.command()
@click.option("-d", "--database", is_flag=True, help="Configure database")
@click.option("-s", "--settings", is_flag=True, help="Configure settings")
@click.argument("path", default="")
def configure(database: bool, settings: bool, path: str):
    """Configure Django project and dependencies"""
    try:
        app = AppContainer.get_instance()
        container = ConfigureContainer.create(app)

        container.configure_project(database=database, settings=settings)
    except Exception as e:
        print(f"Error {e}")


if __name__ == "__main__":
    cli()
