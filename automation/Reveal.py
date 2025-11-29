"""
Lobby Reveal module for League of Legends.
Reveals lobby information and opens Porofessor for match analysis.
"""

import webbrowser
import logging
from typing import Optional, List, Dict
from core import Rengar

logger = logging.getLogger(__name__)


class ChampionSelectNotFoundError(Exception):
    """Raised when champion select session is not found."""
    pass


class LobbyReveal:
    """Manages lobby reveal functionality."""
    
    # Region mappings
    REGION_MAP = {
        "br1": "br1",
        "eun1": "eun1",
        "euw1": "euw1",
        "jp1": "jp1",
        "kr": "kr",
        "la1": "la1",
        "la2": "la2",
        "na1": "na1",
        "oc1": "oc1",
        "tr1": "tr1",
        "ru": "ru",
        "ph2": "ph2",
        "sg2": "sg2",
        "th2": "th2",
        "tw2": "tw2",
        "vn2": "vn2"
    }
    
    def __init__(self):
        """Initialize lobby reveal with Rengar instance."""
        self.rengar = Rengar()
    
    def get_region(self) -> str:
        """
        Get current region from client.
        
        Returns:
            Region code (e.g., "br1", "na1")
        """
        try:
            response = self.rengar.lcu_request("GET", "/riotclient/region-locale", "")
            
            if response.status_code == 200:
                data = response.json()
                region = data.get("webRegion", "")
                
                if region:
                    logger.info(f"🌍 Region detected: {region}")
                    return region
                else:
                    logger.warning("⚠️ Region not found in response")
            else:
                logger.warning(f"⚠️ Failed to get region: {response.status_code}")
                
        except Exception as e:
            logger.error(f"⚠️ Error getting region: {e}")
        
        # Default fallback
        logger.info("ℹ️ Using default region: br1")
        return "br1"
    
    def is_in_champion_select(self) -> bool:
        """
        Check if currently in champion select.
        
        Returns:
            True if in champion select, False otherwise
        """
        try:
            response = self.rengar.lcu_request("GET", "/lol-champ-select/v1/session", "")
            return response.status_code == 200 and "RPC_ERROR" not in response.text
        except Exception:
            return False
    
    def get_players_normal_lobby(self, champ_select_data: dict) -> List[str]:
        """
        Get players from normal (non-ranked) lobby.
        
        Args:
            champ_select_data: Champion select session data
            
        Returns:
            List of player name#tag strings
        """
        players = []
        
        if "myTeam" not in champ_select_data:
            logger.warning("⚠️ Team data not available")
            return players
        
        logger.info("🔓 Normal lobby detected - using direct method")
        
        for player in champ_select_data["myTeam"]:
            summoner_id = player.get("summonerId")
            
            if not summoner_id or summoner_id == "0":
                continue
            
            try:
                response = self.rengar.lcu_request(
                    "GET",
                    f"/lol-summoner/v1/summoners/{summoner_id}",
                    ""
                )
                
                if response.status_code == 200:
                    data = response.json()
                    game_name = data.get("gameName", "")
                    tag_line = data.get("tagLine", "")
                    
                    if game_name and tag_line:
                        player_name = f"{game_name}%23{tag_line}"
                        players.append(player_name)
                        logger.info(f"✅ Player found: {game_name}#{tag_line}")
                else:
                    logger.warning(f"⚠️ Failed to get summoner {summoner_id}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"⚠️ Error processing summoner {summoner_id}: {e}")
        
        return players
    
    def get_players_ranked_lobby(self) -> List[str]:
        """
        Get players from ranked lobby using chat API.
        
        Returns:
            List of player name#tag strings
        """
        players = []
        
        logger.info("🔒 Ranked lobby detected - using chat API")
        
        try:
            response = self.rengar.riot_request("GET", "/chat/v5/participants", "")
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Failed to get participants: {response.status_code}")
                return players
            
            data = response.json()
            
            if "participants" not in data:
                logger.warning("⚠️ No participants data in response")
                return players
            
            for participant in data["participants"]:
                cid = participant.get("cid", "")
                
                # Only include champ-select participants
                if "champ-select" not in cid:
                    continue
                
                game_name = participant.get("game_name", "")
                game_tag = participant.get("game_tag", "")
                
                if game_name and game_tag:
                    player_name = f"{game_name}%23{game_tag}"
                    players.append(player_name)
                    logger.info(f"✅ Player found: {game_name}#{game_tag}")
            
            if not players:
                logger.warning("⚠️ No players found via chat API")
                
        except Exception as e:
            logger.error(f"❌ Error getting ranked lobby players: {e}")
        
        return players
    
    def is_ranked_lobby(self, champ_select_data: dict) -> bool:
        """
        Determine if current lobby is ranked.
        
        Args:
            champ_select_data: Champion select session data
            
        Returns:
            True if ranked lobby, False otherwise
        """
        if "myTeam" not in champ_select_data:
            return False
        
        for player in champ_select_data["myTeam"]:
            if player.get("nameVisibilityType") == "HIDDEN":
                return True
        
        return False
    
    def reveal(self) -> Optional[str]:
        """
        Reveal lobby and open Porofessor.
        
        Returns:
            Porofessor URL or None if failed
        """
        try:
            # Check if in champion select
            if not self.is_in_champion_select():
                logger.error("❌ You are not in champion select")
                return None
            
            # Get champion select data
            response = self.rengar.lcu_request("GET", "/lol-champ-select/v1/session", "")
            
            if response.status_code != 200:
                logger.error("❌ Failed to get champion select data")
                return None
            
            champ_select_data = response.json()
            
            # Determine lobby type and get players
            if self.is_ranked_lobby(champ_select_data):
                players = self.get_players_ranked_lobby()
            else:
                players = self.get_players_normal_lobby(champ_select_data)
            
            if not players:
                logger.error("❌ No players found in lobby")
                return None
            
            # Get region
            region = self.get_region()
            
            if not region:
                logger.error("❌ Could not determine region")
                return None
            
            # Build Porofessor URL
            players_str = ",".join(players)
            url = f"https://porofessor.gg/pregame/{region}/{players_str}"
            
            logger.info(f"\n🚀 Opening Porofessor...")
            logger.info(f"📊 Found {len(players)} player(s)")
            logger.info(f"🔗 URL: {url}\n")
            
            # Open in browser
            webbrowser.open(url)
            return url
            
        except ChampionSelectNotFoundError:
            logger.error("❌ Champion select not found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in Lobby Reveal: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_lobby_info(self) -> Optional[Dict]:
        """
        Get detailed lobby information without opening browser.
        
        Returns:
            Dictionary with lobby information or None if failed
        """
        try:
            if not self.is_in_champion_select():
                return None
            
            response = self.rengar.lcu_request("GET", "/lol-champ-select/v1/session", "")
            
            if response.status_code != 200:
                return None
            
            champ_select_data = response.json()
            is_ranked = self.is_ranked_lobby(champ_select_data)
            
            if is_ranked:
                players = self.get_players_ranked_lobby()
            else:
                players = self.get_players_normal_lobby(champ_select_data)
            
            region = self.get_region()
            
            return {
                "players": [p.replace("%23", "#") for p in players],
                "player_count": len(players),
                "region": region,
                "is_ranked": is_ranked,
                "url": f"https://porofessor.gg/pregame/{region}/{','.join(players)}" if players else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting lobby info: {e}")
            return None


# Legacy function for backwards compatibility
def reveal() -> Optional[str]:
    """
    Legacy reveal function.
    
    Returns:
        Porofessor URL or None if failed
    """
    lobby_reveal = LobbyReveal()
    return lobby_reveal.reveal()


def open_porofessor() -> Optional[str]:
    """
    Open Porofessor for current lobby.
    
    Returns:
        Porofessor URL or None if failed
    """
    return reveal()