from .os_manager import OSManager
from .django_manager import DjangoManager

# Create instances
os_manager = OSManager()
django_manager = DjangoManager()

# Only allow importing the instances
__all__ = ['os_manager', 'django_manager']