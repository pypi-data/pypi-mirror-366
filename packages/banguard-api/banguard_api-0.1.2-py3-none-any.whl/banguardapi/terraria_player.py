from dataclasses import dataclass
from typing import Optional

@dataclass
class TerrariaPlayer:
    id: str
    latest_name: str
    terraria_uuid: str
    discord_id: Optional[int] = None
    discord_account_name: Optional[str] = None

    def __str__(self):
        return self.latest_name

    def __repr__(self):
        return self.__str__()

    def has_connected(self) -> bool:
        return bool(self.discord_id)
