from dataclasses import dataclass
from datetime import datetime
from .terraria_player import TerrariaPlayer

@dataclass
class ConnectionCode:
    """
    Represents a BanGuard Discord-Terraria connection code.
    """
    code: str
    player: TerrariaPlayer
    expiration_timestamp: datetime
    used: bool = False

    def __str__(self):
        return str(self.code)

    def __repr__(self):
        return self.__str__()

    def is_expired(self) -> bool:
        """
        Checks if the connection code is expired.

        :return: True if expired, False otherwise.
        """
        return self.expiration_timestamp < datetime.now()
