from rich.prompt import Prompt
from pathlib import Path
from ...utils.console import console_manager
from ...widgets.list_selector import ListSelector

def prompt_project_selection(projects: list[tuple[str, Path]]) -> tuple[str, Path] | None:
   """Displays list of found Django projects and prompts user to select one.
   Returns selected project name and path tuple, or None if no projects."""
   if not projects:
       return None
       
   choices = [(p[0], p[1]) for p in projects]
   
   console_manager.console.print("\nDid you mean one of these projects?")
   selector = ListSelector(choices)
   return selector.select()