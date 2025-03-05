import click
from .managers import os_manager, django_manager
from .utils.console import console_manager
from . import commands


@click.group()
def cli():
    """Djanbee deployment tool"""
    pass

@cli.command()
#TODO: Add option for manual path
def launch(path = ""):
    """Launch Django server deployment"""
    
    commands.launch.display_splash_screen()

    try:
        #Get current dir
        if not path:
            os_manager.get_dir()
        else:
            os_manager.set_dir(path)

        #Scan directory for django project
        if not os_manager.search_folder(django_manager.is_django_project):

            #Scan subdirectories for django projects
            projects = os_manager.search_subfolders(django_manager.is_django_project)
            #Exit if no child projects
            if not projects:
                console_manager.print_warning_critical("No django projects found")
                return
            
            #Offer found django projects
            console_manager.print_warning_critical("Djagno project not found in this folder")
            selected_project = commands.launch.prompt_project_selection(projects)
            os_manager.set_dir(selected_project[1])

            console_manager.print_success(f"Opening {selected_project[0]} in {path}")

            
        print("PROJECT FOUND IN", os_manager.get_dir())
        
    except Exception as e:
        console_manager.print_error(e)

@cli.command()
#TODO add commands to specify which env and functionallity for multiple envs
def setup():
    console_manager.print_lookup("Searching for virtual environment")

    active_env = os_manager.get_active_venv()
    envs = os_manager.search_folder(commands.setup.is_venv)
    if not active_env:
        console_manager.print_warning_critical("No active virtual environment")
    print(active_env)

    return
    if not active_env:
        console_manager.print_warning_critical("No virtual environments found")
        console_manager.print_question("Do you wish to set up an environment")
        response = input().strip().lower()
        if response in ['y', 'yes']:
            envs = commands.setup.create_environment()
        else:
            print("setup cancelled")
            return

    if len(envs) > 1:
        #TODO Handle multiple environments
        console_manager.print_warning_critical("More than one environment TODO")
        return

    env_name, env_path, _ = envs[0]
    console_manager.print_lookup(f"Found virtual environment: {env_name}")

    console_manager.print_lookup("Looking for requirements")
    requirements = os_manager.search_folder(commands.setup.has_requirements)
    if not requirements:
        requirements = os_manager.search_subfolders(commands.setup.has_requirements)
        if not requirements:
            console_manager.print_warning_critical("No requirements found")
            console_manager.print_question("Do you wish to extract requirements")
            response = input().strip().lower()
            if response in ['y', 'yes']:
                envs = commands.setup.create_environment()
            else:
                print("setup cancelled")
                return



        
    



if __name__ == '__main__':
    cli()
