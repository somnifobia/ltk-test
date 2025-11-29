"""
Auto-accept module for automatically accepting match found notifications.
"""

import threading
import time
from core import Rengar
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AutoAccept:
    """Automatically accepts match found notifications."""
    
    def __init__(self):
        """Initialize auto-accept with default settings."""
        self.auto_accept_enabled = False
        self.rengar = Rengar()
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_running = False
        self._lock = threading.Lock()
        logger.info("🎮 AutoAccept initialized")
    
    def toggle_auto_accept(self) -> bool:
        """
        Toggle auto-accept on/off.
        
        Returns:
            New state (True if enabled, False if disabled)
        """
        with self._lock:
            self.auto_accept_enabled = not self.auto_accept_enabled
        
        state = "✅ ON" if self.auto_accept_enabled else "❌ OFF"
        logger.info(f"Auto-accept is now {state}")
        
        if self.auto_accept_enabled:
            self.start_monitor()
        else:
            self.stop_monitor()
        
        return self.auto_accept_enabled
    
    def enable(self) -> None:
        """Enable auto-accept."""
        with self._lock:
            self.auto_accept_enabled = True
        logger.info("✅ Auto-accept enabled")
        self.start_monitor()
    
    def disable(self) -> None:
        """Disable auto-accept."""
        with self._lock:
            self.auto_accept_enabled = False
        logger.info("❌ Auto-accept disabled")
        self.stop_monitor()
    
    def accept_match(self) -> bool:
        """
        Accept the match found notification.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.rengar.lcu_request(
                "POST",
                "/lol-matchmaking/v1/ready-check/accept",
                ""
            )
            
            if response.status_code in [200, 204]:
                logger.info("✅ Match accepted!")
                return True
            else:
                logger.warning(f"⚠️ Failed to accept match: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error accepting match: {e}")
            return False
    
    def decline_match(self) -> bool:
        """
        Decline the match found notification.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.rengar.lcu_request(
                "POST",
                "/lol-matchmaking/v1/ready-check/decline",
                ""
            )
            
            if response.status_code in [200, 204]:
                logger.info("✅ Match declined")
                return True
            else:
                logger.warning(f"⚠️ Failed to decline match: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error declining match: {e}")
            return False
    
    def get_ready_check_state(self) -> Optional[dict]:
        """
        Get current ready check state.
        
        Returns:
            Ready check data or None if not in ready check
        """
        try:
            response = self.rengar.lcu_request(
                "GET",
                "/lol-matchmaking/v1/ready-check",
                ""
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception:
            return None
    
    def monitor_queue(self) -> None:
        """Monitor queue for match found notifications."""
        logger.info("👀 Queue monitor started")
        last_state = None
        consecutive_errors = 0
        max_errors = 5
        
        while self.is_running:
            try:
                if not self.auto_accept_enabled:
                    time.sleep(1)
                    continue
                
                # Check search state
                response = self.rengar.lcu_request(
                    "GET",
                    "/lol-lobby/v2/lobby/matchmaking/search-state",
                    ""
                )
                
                if response.status_code == 200:
                    match_data = response.json()
                    search_state = match_data.get("searchState", "")
                    
                    # Match found
                    if search_state == "Found" and last_state != "Found":
                        logger.info("🎯 Match found! Auto-accepting...")
                        self.accept_match()
                    
                    last_state = search_state
                    consecutive_errors = 0
                    
                elif response.status_code == 404:
                    # Not in queue, reset state
                    last_state = None
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= max_errors:
                        logger.error("❌ Too many consecutive errors, stopping monitor")
                        self.is_running = False
                        break
                
                time.sleep(0.5)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"⚠️ Error in queue monitor: {e}")
                
                if consecutive_errors >= max_errors:
                    logger.error("❌ Too many consecutive errors, stopping monitor")
                    self.is_running = False
                    break
                
                time.sleep(2)
        
        logger.info("🛑 Queue monitor stopped")
    
    def start_monitor(self) -> None:
        """Start the queue monitoring thread."""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.is_running = True
            self.monitor_thread = threading.Thread(
                target=self.monitor_queue,
                daemon=True,
                name="AutoAcceptMonitor"
            )
            self.monitor_thread.start()
            logger.info("▶️ Monitor thread started")
    
    def stop_monitor(self) -> None:
        """Stop the queue monitoring thread."""
        self.is_running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        logger.info("⏹️ Monitor thread stopped")
    
    def get_status(self) -> dict:
        """
        Get current auto-accept status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "enabled": self.auto_accept_enabled,
            "monitor_running": self.is_running,
            "thread_alive": self.monitor_thread.is_alive() if self.monitor_thread else False
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_monitor()