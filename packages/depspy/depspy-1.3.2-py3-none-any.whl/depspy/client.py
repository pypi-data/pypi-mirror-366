import aiohttp
import asyncio
import time
from typing import Optional, Dict, Any, Union, List
from .models import *
from .exceptions import *
from .version import __version__
import re
from functools import wraps
import logging

logger = logging.getLogger("depspy")

def validate_nickname(nickname: str) -> bool:
    if not nickname or not isinstance(nickname, str):
        return False
    if len(nickname) < 3 or len(nickname) > 32:
        return False
    if not re.match(r"^[a-zA-Z0-9_]+$", nickname):
        return False
    return True

def validate_server_id(server_id: int) -> bool:
    return isinstance(server_id, int) and server_id > 0

def validate_fraction_id(fraction_id: Union[int, str]) -> bool:
    if isinstance(fraction_id, int):
        return fraction_id > 0
    elif isinstance(fraction_id, str):
        return len(fraction_id) > 0
    return False

def validate_fam_id(fam_id: int) -> bool:
    return isinstance(fam_id, int) and fam_id > 0

def cache_decorator(ttl: int = 300):
    def decorator(func):
        cache = {}
        
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl:
                    return result
            
            result = await func(self, *args, **kwargs)
            cache[cache_key] = (result, current_time)
            return result
            
        return wrapper
    return decorator

class DepsClient:
    def __init__(
        self,
        api_key: str,
        corporate_key: bool = False,
        base_url: str = "https://api.depscian.tech/v2",
        timeout: int = 30,
        max_retries: int = 3,
        cache_ttl: int = 300,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        log_level: int = logging.INFO
    ):
        if not api_key:
            raise InvalidAPIKeyError()
            
        self.api_key = api_key
        self.corporate_key = corporate_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.setLevel(log_level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def _ensure_session(self):
        if not self._session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(verify_ssl=self.verify_ssl)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": f"DepsAPIPy/{__version__}"
        }
        if self.corporate_key:
            headers["X-Corporate-Key"] = "true"
        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        await self._ensure_session()
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Making request to {url} (attempt {attempt + 1}/{self.max_retries})")
                
                async with self._session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    proxy=self.proxy
                ) as response:
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 1))
                        logger.warning(f"Rate limit exceeded, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue

                    data = await response.json()
                    logger.debug(f"Response from {url}: {data}")

                    if response.status == 401:
                        if "expired" in str(data).lower():
                            raise ExpiredAPIKeyError(
                                data.get("error_code", "EXPIRED_API_KEY"),
                                data.get("error_message", "API key has expired"),
                                data.get("error_id")
                            )
                        raise UnauthorizedError(
                            data.get("error_code", "UNAUTHORIZED"),
                            data.get("error_message", "Unauthorized"),
                            data.get("error_id")
                        )
                    elif response.status == 429:
                        raise RateLimitError(
                            data.get("error_code", "RATE_LIMIT_EXCEEDED"),
                            data.get("error_message", "Rate limit exceeded"),
                            data.get("error_id")
                        )
                    elif response.status == 404:
                        if "PLAYER_NOT_FOUND" in str(data):
                            raise PlayerNotFoundError(
                                data.get("error_code", "PLAYER_NOT_FOUND"),
                                data.get("error_message", "Player not found"),
                                data.get("error_id")
                            )
                        raise ServerNotFoundError(
                            data.get("error_code", "SERVER_NOT_FOUND"),
                            data.get("error_message", "Server not found"),
                            data.get("error_id")
                        )
                    elif response.status == 503:
                        raise MaintenanceError(
                            data.get("error_code", "MAINTENANCE_ERROR"),
                            data.get("error_message", "API is under maintenance"),
                            data.get("error_id")
                        )
                    elif response.status >= 400:
                        raise APIError(
                            data.get("error_code", "API_ERROR"),
                            data.get("error_message", "API error occurred"),
                            data.get("error_id")
                        )

                    return data

            except aiohttp.ClientError as e:
                if isinstance(e, aiohttp.ClientTimeout):
                    raise TimeoutError("TIMEOUT_ERROR", str(e))
                elif isinstance(e, aiohttp.ClientProxyConnectionError):
                    raise ProxyError("PROXY_ERROR", str(e))
                elif isinstance(e, aiohttp.ClientSSLError):
                    raise SSLError("SSL_ERROR", str(e))
                elif isinstance(e, aiohttp.ClientConnectorError):
                    raise DNSResolutionError("DNS_RESOLUTION_ERROR", str(e))
                
                if attempt == self.max_retries - 1:
                    raise ConnectionError("CONNECTION_ERROR", str(e))
                await asyncio.sleep(2 ** attempt)

    @cache_decorator(ttl=300)
    async def get_player(self, nickname: str, server_id: int) -> Player:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        data = await self._make_request(
            "GET",
            "player/find",
            params={"nickname": nickname, "serverId": server_id}
        )
        return Player(**data)

    @cache_decorator(ttl=60)
    async def get_interviews(self, server_id: int) -> Interviews:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        data = await self._make_request(
            "GET",
            "sobes",
            params={"serverId": server_id}
        )
        return Interviews(**data)

    @cache_decorator(ttl=30)
    async def get_online_players(self, server_id: int) -> OnlinePlayers:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        data = await self._make_request(
            "GET",
            "online",
            params={"serverId": server_id}
        )
        return OnlinePlayers(**data)

    @cache_decorator(ttl=300)
    async def get_fractions(self, server_id: int) -> Fractions:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        data = await self._make_request(
            "GET",
            "fractions",
            params={"serverId": server_id}
        )
        return Fractions(**data)

    @cache_decorator(ttl=30)
    async def get_fraction_online(
        self,
        server_id: int,
        fraction_id: str
    ) -> OnlinePlayers:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
        if not validate_fraction_id(fraction_id):
            raise InvalidFractionIDError()
            
        data = await self._make_request(
            "GET",
            "fraction",
            params={"serverId": server_id, "fractionId": fraction_id}
        )
        return OnlinePlayers(**data)

    @cache_decorator(ttl=300)
    async def get_admins(self, server_id: int) -> Admins:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        data = await self._make_request(
            "GET",
            "admins",
            params={"serverId": server_id}
        )
        return Admins(**data)

    @cache_decorator(ttl=60)
    async def get_status(self) -> Status:
        data = await self._make_request("GET", "status")
        return Status(**data)

    async def get_server_info(self, server_id: int) -> Server:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        data = await self._make_request(
            "GET",
            f"server/{server_id}"
        )
        return Server(**data)

    async def get_online_count(self, server_id: int) -> int:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        online = await self.get_online_players(server_id)
        return len(online.data)

    async def get_fraction_members_count(self, server_id: int, fraction_id: str) -> int:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
        if not validate_fraction_id(fraction_id):
            raise InvalidFractionIDError()
            
        fraction_online = await self.get_fraction_online(server_id, fraction_id)
        return len(fraction_online.data)

    async def is_player_online(self, nickname: str, server_id: int) -> bool:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        online = await self.get_online_players(server_id)
        return any(player.name == nickname for player in online.data.values())

    async def get_player_level(self, nickname: str, server_id: int) -> int:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        player = await self.get_player(nickname, server_id)
        return player.level.level

    async def get_player_money(self, nickname: str, server_id: int) -> Money:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        player = await self.get_player(nickname, server_id)
        return player.money

    async def get_player_organization(self, nickname: str, server_id: int) -> Optional[Organization]:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        player = await self.get_player(nickname, server_id)
        return player.organization

    async def get_player_property(self, nickname: str, server_id: int) -> Property:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        player = await self.get_player(nickname, server_id)
        return player.property

    async def get_player_vip_info(self, nickname: str, server_id: int) -> VIPInfo:
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
            
        player = await self.get_player(nickname, server_id)
        return player.vip_info 
    
    async def get_fraction_id_name(self, value: Union[int, str]) -> Union[int, str]:
        fractions = {
            1: "Полиция ЛС",
            2: "RCSD",
            3: "FBI",
            4: "Полиция SF",
            5: "Больница LS",
            6: "Правительство",
            7: "Тюрьма Строгого режима LV",
            8: "Больница SF",
            9: "Лицензеры",
            10: "Radio LS",
            11: "Grove Street",
            12: "Vagos Family",
            13: "East Side Ballas",
            14: "Varrios Los Aztecas",
            15: "The Rifa Gang",
            16: "Russian Mafia",
            17: "Yakuza",
            18: "La Cosa Nostra",
            19: "Warlock MC",
            20: "Армия LS",
            22: "Больница LV",
            23: "Полиция LV",
            24: "TV студия LV",
            25: "Night Wolves",
            26: "TV студия SF",
            27: "Армия SF",
            29: "Страховая компания",
            30: "Tierra Robada Bikers",
            31: "Больница Jefferson",
            32: "Пожарный Департамент"
        }
            
        if isinstance(value, int):
            return fractions.get(value, "Unknown")
        elif isinstance(value, str):
            for id, name in fractions.items():
                if name.lower() == value.lower():
                    return id
            return 0
        else:
            raise TypeError("Value must be int or str")
        
    async def list_fractions(self) -> Dict[int, str]:
        fractions = {
            1: "Полиция ЛС",
            2: "RCSD",
            3: "FBI",
            4: "Полиция SF",
            5: "Больница LS",
            6: "Правительство",
            7: "Тюрьма Строгого режима LV",
            8: "Больница SF",
            9: "Лицензеры",
            10: "Radio LS",
            11: "Grove Street",
            12: "Vagos Family",
            13: "East Side Ballas",
            14: "Varrios Los Aztecas",
            15: "The Rifa Gang",
            16: "Russian Mafia",
            17: "Yakuza",
            18: "La Cosa Nostra",
            19: "Warlock MC",
            20: "Армия LS",
            22: "Больница LV",
            23: "Полиция LV",
            24: "TV студия LV",
            25: "Night Wolves",
            26: "TV студия SF",
            27: "Армия SF",
            29: "Страховая компания",
            30: "Tierra Robada Bikers",
            31: "Больница Jefferson",
            32: "Пожарный Департамент"
        }
        return fractions
    
    @cache_decorator(ttl=60)
    async def get_map(self, server_id: int) -> MapResponse:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()

        data = await self._make_request(
            "GET",
            "map",
            params={"serverId": server_id}
        )
        return MapResponse(**data)

    @cache_decorator(ttl=60)
    async def get_ghetto(self, server_id: int) -> GhettoResponse:
        data = await self._make_request(
            "GET",
            "ghetto",
            params={"serverId": server_id}
        )
        return GhettoResponse(**data)

    @cache_decorator(ttl=30)
    async def get_leaders(self, server_id: int) -> LeadersResponse:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()

        data = await self._make_request(
            "GET",
            "leaders",
            params={"serverId": server_id}
        )
        return LeadersResponse(**data)

    @cache_decorator(ttl=30)
    async def get_subleaders(self, server_id: int) -> SubleadersResponse:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()

        data = await self._make_request(
            "GET",
            "subleaders",
            params={"serverId": server_id}
        )
        return SubleadersResponse(**data)

    @cache_decorator(ttl=120)
    async def get_families(self, server_id: int) -> FamilyListResponse:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
        
        data = await self._make_request(
            "GET",
            "families",
            params={"serverId": server_id}
        )
        return FamilyListResponse(**data)

    @cache_decorator(ttl=120)
    async def get_family(self, server_id: int, fam_id: int) -> FamilyResponse:
        if not validate_server_id(server_id):
            raise InvalidServerIDError()
        if not validate_fam_id(fam_id):
            raise InvalidFamIDError()
            
        data = await self._make_request(
            "GET",
            "family",
            params={"serverId": server_id, "famId": fam_id}
        )
        return FamilyResponse(**data)

    async def track_player_online(self, nickname: str, server_id: int, callback, check_interval: int = 90):
        if not validate_nickname(nickname):
            raise InvalidNicknameError()
        if not validate_server_id(server_id):
            raise InvalidServerIDError()

        async def check_player_online():
            while True:
                try:
                    online = await self.get_online_players(server_id)
                    if any(player.name == nickname for player in online.data.values()):
                        await callback()
                        break
                except Exception as e:
                    logger.error(f"Ошибка трекинга игрока {nickname}: {e}")
                    break
                await asyncio.sleep(check_interval)

        asyncio.create_task(check_player_online())