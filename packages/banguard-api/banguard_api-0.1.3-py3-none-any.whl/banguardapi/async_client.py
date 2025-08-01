import aiohttp

from .ban import Ban
from .connection_code import ConnectionCode
from .exceptions import *
from .terraria_player import TerrariaPlayer


class Client:
    BASE_URL = "https://banguard.uk/api/"

    def __init__(self, token: str, check_token: bool = True):
        self._token = token
        self._session = None  # Will be initialized in async context

        self._headers = {"Authorization": self._token}
        self._check_token = check_token

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self._headers)
        if self._check_token:
            if not await self.is_token_valid():
                await self._session.close()
                raise AuthenticationError("Invalid token provided.")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()

    async def _request(self, method: str, endpoint: str, **kwargs):
        """Helper method to send async requests and handle errors."""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with self._session.request(method, url, timeout=10, **kwargs) as response:
                if response.status >= 400:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get("error", await response.text())
                    except Exception:
                        error_msg = await response.text()

                    if response.status == 400:
                        raise BadRequestError(error_msg)
                    elif response.status == 401:
                        raise AuthenticationError(error_msg)
                    elif response.status == 403:
                        raise PermissionDeniedError(error_msg)
                    elif response.status == 404:
                        raise NotFoundError(error_msg)
                    elif response.status == 429:
                        raise RateLimitError(error_msg)
                    elif 500 <= response.status < 600:
                        raise ServerError(error_msg)
                    else:
                        raise APIError(error_msg)

                try:
                    data = await response.json()
                except Exception:
                    raise InvalidResponseError("Invalid JSON response from the server.")

                if isinstance(data, dict) and "error" in data:
                    raise APIError(data["error"])

                return data

        except aiohttp.ClientError as e:
            raise APIError(f"Network error: {e}")

    async def is_token_valid(self) -> bool:
        """Return True if the token is valid, False otherwise."""
        data = await self._request("GET", "check-token")
        return data.get("valid", False)

    async def get_ban_count(self) -> int:
        """Fetch ban count from the BanGuard API"""
        data = await self._request("GET", "ban-count")
        return data.get("ban_count", 0)

    async def ban_player(self, player: TerrariaPlayer, category: str) -> Ban:
        """Ban a player"""
        json_data = {
            "player_uuid": player.terraria_uuid,
            "category": category,
        }
        response = await self._request("POST", "ban-player", data=json_data)
        return Ban(response["ban"]["id"], player, category)

    async def unban_player(self, ban: Ban) -> None:
        """Unban a player"""
        json_data = {
            "ban_id": ban.id,
        }
        try:
            await self._request("POST", "unban-player", data=json_data)
        except NotFoundError as e:
            raise PlayerNotFoundError(str(e)) from e

    async def get_player(self, player_uuid: str) -> TerrariaPlayer:
        """Fetch a player from the API"""
        json_data = {
            "player_uuid": player_uuid,
        }
        try:
            response = await self._request("POST", "get-player", data=json_data)
        except NotFoundError as e:
            raise PlayerNotFoundError(str(e)) from e
        return TerrariaPlayer(
            response["player"]["id"],
            response["player"]["latest_name"],
            player_uuid,
            discord_id=response["player"]["discord_id"],
            discord_account_name=response["player"]["discord_account_name"],
        )

    async def new_connection_code(self, player: TerrariaPlayer) -> ConnectionCode:
        """Create a new connection code for a player"""
        json_data = {
            "player_uuid": player.terraria_uuid,
        }
        response = await self._request("POST", "new-connection-code", data=json_data)
        return ConnectionCode(response["code"], player, response["expiration_time"])

    async def check_connection_code(self, code: str) -> bool:
        response = await self._request("GET", "check-code", params={"code": code})
        return bool(response["valid"])

    async def get_ban_categories(self) -> list:
        """Fetch the list of ban categories from the API"""
        data = await self._request("GET", "ban-category-list")
        return data["ban_categories"]
