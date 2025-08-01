from dataclasses import dataclass
from typing import Optional
from .server import Server
from .terraria_player import TerrariaPlayer


@dataclass
class Ban:
    id: int
    player: TerrariaPlayer
    category: str
    server: Optional[Server] = None

    def __str__(self):
        return f"Ban(player={self.player}, server={self.server}, category={self.category})"

    def __repr__(self):
        return self.__str__()
