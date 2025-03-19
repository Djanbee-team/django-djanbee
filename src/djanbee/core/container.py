from dataclasses import dataclass
from typing import Optional
from ..managers import (
    OSManager,
    DjangoManager,
    ConsoleManager,
    DatabaseManager,
    ServerManager,
)


@dataclass
class AppContainer:
    """Singleton container for shared tools"""

    os_manager: "OSManager"
    django_manager: "DjangoManager"
    console_manager: "ConsoleManager"
    database_manager: "DatabaseManager"
    server_manager: "ServerManager"

    _instance: Optional["AppContainer"] = None

    @classmethod
    def get_instance(cls) -> "AppContainer":
        if cls._instance is None:
            os_manager = OSManager()
            console_manager = ConsoleManager()

            cls._instance = cls(
                os_manager=os_manager,
                console_manager=console_manager,
                django_manager=DjangoManager(os_manager, console_manager),
                database_manager=DatabaseManager(os_manager),
                server_manager=ServerManager(os_manager, console_manager),
            )
        return cls._instance
