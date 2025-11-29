"""
Core module for League of Legends Client API interactions.
Provides authentication and request handling for both LCU and Riot Client APIs.
"""

import psutil
import requests
import base64
import json
import urllib3
from time import sleep
from typing import Optional, Tuple, Dict
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LeagueClientNotFoundError(Exception):
    """Raised when League Client process is not found."""
    pass


class Rengar:
    """
    Main class for interacting with League of Legends Client APIs.
    Handles authentication and requests to both LCU and Riot Client.
    """
    
    def __init__(self, auto_retry: bool = True, max_retries: int = 3):
        """
        Initialize Rengar with client credentials.
        
        Args:
            auto_retry: Automatically retry failed requests
            max_retries: Maximum number of retry attempts
        """
        self.auto_retry = auto_retry
        self.max_retries = max_retries
        self._update_all_credentials()
        
    def _update_all_credentials(self) -> None:
        """Update both League and Riot client credentials."""
        try:
            self.update_league_credentials()
            self.update_riot_credentials()
            logger.info("✅ Credentials updated successfully")
        except LeagueClientNotFoundError as e:
            logger.error(f"❌ {e}")
            raise
    
    @staticmethod
    def find_league_client_credentials() -> Tuple[Optional[str], Optional[str]]:
        """
        Find League Client port and authentication token.
        
        Returns:
            Tuple of (port, token) or (None, None) if not found
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'LeagueClientUx.exe':
                    cmdline = proc.info['cmdline']
                    port = None
                    token = None
                    
                    for arg in cmdline:
                        if arg.startswith('--app-port='):
                            port = arg.split('=', 1)[1]
                        elif arg.startswith('--remoting-auth-token='):
                            token = arg.split('=', 1)[1]
                    
                    if port and token:
                        return port, token
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return None, None
    
    @staticmethod
    def find_riot_client_credentials() -> Tuple[Optional[str], Optional[str]]:
        """
        Find Riot Client port and authentication token.
        
        Returns:
            Tuple of (port, token) or (None, None) if not found
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'LeagueClientUx' in proc.info['name']:
                    cmdline = proc.info['cmdline']
                    port = None
                    token = None
                    
                    for arg in cmdline:
                        if '--riotclient-auth-token=' in arg:
                            token = arg.split('=', 1)[1]
                        elif '--riotclient-app-port=' in arg:
                            port = arg.split('=', 1)[1]
                    
                    if port and token:
                        return port, token
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return None, None
    
    @staticmethod
    def wait_for_league_client(timeout: int = 60, check_interval: float = 0.5) -> Tuple[str, str]:
        """
        Wait for League Client to start.
        
        Args:
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            Tuple of (port, token)
            
        Raises:
            LeagueClientNotFoundError: If client is not found within timeout
        """
        elapsed = 0
        logger.info("⏳ Waiting for League Client...")
        
        while elapsed < timeout:
            port, token = Rengar.find_league_client_credentials()
            if port and token:
                logger.info("✅ League Client found!")
                return port, token
            sleep(check_interval)
            elapsed += check_interval
        
        raise LeagueClientNotFoundError(
            f"League Client not found after {timeout} seconds"
        )
    
    def update_league_credentials(self) -> None:
        """Update League Client credentials and headers."""
        self.leaguePort, self.leagueToken = self.find_league_client_credentials()
        
        if not self.leaguePort or not self.leagueToken:
            raise LeagueClientNotFoundError(
                "League Client is not running. Please start the client first."
            )
        
        self.leagueUrl = f'https://127.0.0.1:{self.leaguePort}'
        auth = base64.b64encode(f'riot:{self.leagueToken}'.encode()).decode()
        self.leagueHeaders = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json'
        }
    
    def update_riot_credentials(self) -> None:
        """Update Riot Client credentials and headers."""
        self.riotPort, self.riotToken = self.find_riot_client_credentials()
        
        if not self.riotPort or not self.riotToken:
            logger.warning("⚠️ Riot Client credentials not found")
            return
        
        self.riotUrl = f'https://127.0.0.1:{self.riotPort}'
        auth = base64.b64encode(f'riot:{self.riotToken}'.encode()).decode()
        self.riotHeaders = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json'
        }
    
    def lcu_request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Dict] = None,
        timeout: int = 10
    ) -> requests.Response:
        """
        Make a request to the League Client API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path
            body: Request body data
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            ValueError: If method is invalid
            requests.RequestException: If request fails after retries
        """
        method = method.upper()
        url = f'{self.leagueUrl}{endpoint}'
        
        if body:
            body = json.dumps(body)
        
        for attempt in range(self.max_retries if self.auto_retry else 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.leagueHeaders,
                    data=body,
                    verify=False,
                    timeout=timeout
                )
                return response
                
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️ Connection failed, retrying... ({attempt + 1}/{self.max_retries})")
                    self.update_league_credentials()
                    sleep(1)
                else:
                    logger.error("❌ Max retries reached for LCU request")
                    raise
                    
            except requests.exceptions.Timeout:
                logger.error(f"❌ Request timeout after {timeout}s")
                raise
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in LCU request: {e}")
                raise
    
    def riot_request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Dict] = None,
        timeout: int = 10
    ) -> requests.Response:
        """
        Make a request to the Riot Client API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path
            body: Request body data
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            ValueError: If method is invalid
            requests.RequestException: If request fails after retries
        """
        method = method.upper()
        url = f'{self.riotUrl}{endpoint}'
        
        if body:
            body = json.dumps(body)
        
        for attempt in range(self.max_retries if self.auto_retry else 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.riotHeaders,
                    data=body,
                    verify=False,
                    timeout=timeout
                )
                return response
                
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️ Connection failed, retrying... ({attempt + 1}/{self.max_retries})")
                    self.update_riot_credentials()
                    sleep(1)
                else:
                    logger.error("❌ Max retries reached for Riot request")
                    raise
                    
            except requests.exceptions.Timeout:
                logger.error(f"❌ Request timeout after {timeout}s")
                raise
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in Riot request: {e}")
                raise
    
    def get_summoner_info(self) -> Optional[Dict]:
        """
        Get current summoner information.
        
        Returns:
            Summoner data dict or None if failed
        """
        try:
            response = self.lcu_request("GET", "/lol-summoner/v1/current-summoner")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get summoner info: {e}")
        return None
    
    def is_in_game(self) -> bool:
        """
        Check if player is currently in game.
        
        Returns:
            True if in game, False otherwise
        """
        try:
            response = self.lcu_request("GET", "/lol-gameflow/v1/gameflow-phase")
            if response.status_code == 200:
                phase = response.json()
                return phase in ["InProgress", "WaitingForStats", "PreEndOfGame", "EndOfGame"]
        except Exception:
            pass
        return False
    
    def get_gameflow_phase(self) -> Optional[str]:
        """
        Get current gameflow phase.
        
        Returns:
            Phase string or None if failed
        """
        try:
            response = self.lcu_request("GET", "/lol-gameflow/v1/gameflow-phase")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get gameflow phase: {e}")
        return None