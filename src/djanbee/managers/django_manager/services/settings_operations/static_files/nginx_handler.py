from pathlib import Path
from typing import Tuple, Dict, Optional, Union, List, Any, cast

from .base_handler import StaticFilesHandler
from ...settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ...venv_service import DjangoEnvironmentService


class NginxHandler(StaticFilesHandler):
    """Handler for configuring Nginx static files in Django"""

    def handle(self) -> bool:
        """
        Configure Django settings for Nginx static files handling
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        # Configure basic static file settings using parent class methods
        static_url = self.settings_service.find_in_settings("STATIC_URL", default="")
        print(static_url)
        new_url = self.display.input_static_url(static_url)
        
        if new_url is None:
            return None
        
        if not super().setup_static_url(new_url):
            return False
        
        if not super().setup_static_root():
            return False
        
        if not super().setup_staticfiles_dirs("Nginx"):
            return False
        
        # Configure media settings if needed
        if not self.setup_media_settings():
            return False
        
        # Provide guidance on Nginx configuration
        self.display_nginx_configuration_instructions()
        
        return True

    def setup_media_settings(self) -> bool:
        """
        Configure MEDIA_URL and MEDIA_ROOT settings
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Configure MEDIA_URL
        media_url = self.settings_service.find_in_settings("MEDIA_URL")
        if media_url != "/media/":
            self.display.print_progress_media_url()
            result = self.settings_service.edit_settings("MEDIA_URL", "/media/")
            success = result[0] if isinstance(result, tuple) else result
            if not success:
                return False
        
        # Configure MEDIA_ROOT
        media_root = self.settings_service.find_in_settings("MEDIA_ROOT")
        if not media_root:
            self.display.print_progress_media_root()
            
            # Ensure os is imported
            has_os = self.settings_service.is_library_imported("os")
            if not has_os:
                self.settings_service.add_library_import("os")
                self.display.print_progress_media_root_add_os()
            
            # Set MEDIA_ROOT
            result = self.settings_service.replace_settings(
                "MEDIA_ROOT", "os.path.join(BASE_DIR, 'media')"
            )
            if not result[0]:
                return False
        
        self.display.success_progress_media_settings()
        return True

    def display_nginx_configuration_instructions(self) -> None:
        """Display instructions for configuring Nginx to serve static files"""
        static_url = cast(str, self.settings_service.find_in_settings("STATIC_URL", "/static/"))
        static_root = cast(str, self.settings_service.find_in_settings("STATIC_ROOT", "staticfiles"))
        media_url = cast(str, self.settings_service.find_in_settings("MEDIA_URL", "/media/"))
        media_root = cast(str, self.settings_service.find_in_settings("MEDIA_ROOT", "media"))
        
        self.display.print_nginx_instructions(
            static_url=static_url,
            static_root=static_root,
            media_url=media_url,
            media_root=media_root
        )

    def generate_nginx_config(self, server_name: str, 
                             static_url: str = "/static/", 
                             media_url: str = "/media/") -> str:
        """
        Generate a sample Nginx configuration for the Django project
        
        Args:
            server_name: The server name (domain) for the Nginx configuration
            static_url: The URL path for static files (from STATIC_URL)
            media_url: The URL path for media files (from MEDIA_URL)
            
        Returns:
            str: A sample Nginx configuration
        """
        # Get project settings to generate accurate paths
        static_root = self.settings_service.find_in_settings("STATIC_ROOT", "staticfiles")
        media_root = self.settings_service.find_in_settings("MEDIA_ROOT", "media")
        
        # Convert OS path join expressions to actual paths if needed
        static_root_path = "staticfiles"  # Default fallback
        if isinstance(static_root, str):
            if "os.path.join" in static_root:
                # Extract just the last part from the os.path.join expression
                import re
                match = re.search(r"'([^']+)'(?:\s*\))?$", static_root)
                if match:
                    static_root_path = match.group(1)
            else:
                static_root_path = static_root
        
        media_root_path = "media"  # Default fallback
        if isinstance(media_root, str):
            if "os.path.join" in media_root:
                # Extract just the last part from the os.path.join expression
                import re
                match = re.search(r"'([^']+)'(?:\s*\))?$", media_root)
                if match:
                    media_root_path = match.group(1)
            else:
                media_root_path = media_root
        
        # Generate the configuration
        nginx_config = f"""
server {{
    listen 80;
    server_name {server_name};

    location {static_url} {{
        alias /path/to/your/project/{static_root_path}/;
    }}

    location {media_url} {{
        alias /path/to/your/project/{media_root_path}/;
    }}

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""
        return nginx_config