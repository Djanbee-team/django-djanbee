from pathlib import Path

class DjangoManager:
    @staticmethod
    def is_django_project(path: Path) -> bool:
        """Validate if directory is a Django project"""
        required_files = ['manage.py']
        optional_files = ['requirements.txt', 'Pipfile']
        if not path.is_dir():
            return False

        has_manage_py = any(file.name == 'manage.py' for file in path.iterdir())

        if not has_manage_py:
            return False
          
        manage_content = path.joinpath('manage.py').read_text()
        return 'django' in manage_content.lower()
    
    @staticmethod
    def find_django_projects(search_path: Path) -> list[tuple[str, Path]]:
        """Find all Django projects in the given directory path"""
        projects = []
        
        for folder in search_path.iterdir():
            if folder.is_dir() and DjangoManager.is_django_project(folder):
                projects.append((folder.name, folder))
                
        return projects