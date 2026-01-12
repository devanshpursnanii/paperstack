"""
Quota Management for Session Limits and Cooldowns

Tracks:
- Paper Brain searches (max 3 per session)
- Paper Chat messages (max 5 per session)
- User quota exhaustion (15 min cooldown)
- API quota exhaustion (30 min cooldown)
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class QuotaTracker:
    """Track quota usage and cooldowns for a session."""
    
    # Usage counters
    brain_searches: int = 0
    chat_messages: int = 0
    
    # Cooldown timestamps
    brain_exhausted_at: Optional[datetime] = None
    chat_exhausted_at: Optional[datetime] = None
    api_exhausted_at: Optional[datetime] = None
    
    # Limits
    MAX_BRAIN_SEARCHES: int = 3
    MAX_CHAT_MESSAGES: int = 5
    USER_COOLDOWN_MINUTES: int = 15
    API_COOLDOWN_MINUTES: int = 30
    
    def can_use_brain(self) -> Tuple[bool, int]:
        """
        Check if Paper Brain can be used.
        
        Returns:
            (allowed: bool, minutes_left: int)
        """
        # Check user quota
        if self.brain_searches >= self.MAX_BRAIN_SEARCHES:
            if self.brain_exhausted_at:
                minutes_left = self._get_minutes_remaining(
                    self.brain_exhausted_at, 
                    self.USER_COOLDOWN_MINUTES
                )
                if minutes_left > 0:
                    return False, minutes_left
                else:
                    # Cooldown expired, reset
                    self.brain_exhausted_at = None
                    self.brain_searches = 0
            else:
                # Just hit limit, start cooldown
                self.brain_exhausted_at = datetime.now()
                return False, self.USER_COOLDOWN_MINUTES
        
        # Check API quota
        if self.api_exhausted_at:
            minutes_left = self._get_minutes_remaining(
                self.api_exhausted_at,
                self.API_COOLDOWN_MINUTES
            )
            if minutes_left > 0:
                return False, minutes_left
            else:
                # Cooldown expired
                self.api_exhausted_at = None
        
        return True, 0
    
    def can_use_chat(self) -> Tuple[bool, int]:
        """
        Check if Paper Chat can be used.
        
        Returns:
            (allowed: bool, minutes_left: int)
        """
        # Check user quota
        if self.chat_messages >= self.MAX_CHAT_MESSAGES:
            if self.chat_exhausted_at:
                minutes_left = self._get_minutes_remaining(
                    self.chat_exhausted_at,
                    self.USER_COOLDOWN_MINUTES
                )
                if minutes_left > 0:
                    return False, minutes_left
                else:
                    # Cooldown expired, reset
                    self.chat_exhausted_at = None
                    self.chat_messages = 0
            else:
                # Just hit limit, start cooldown
                self.chat_exhausted_at = datetime.now()
                return False, self.USER_COOLDOWN_MINUTES
        
        # Check API quota
        if self.api_exhausted_at:
            minutes_left = self._get_minutes_remaining(
                self.api_exhausted_at,
                self.API_COOLDOWN_MINUTES
            )
            if minutes_left > 0:
                return False, minutes_left
            else:
                # Cooldown expired
                self.api_exhausted_at = None
        
        return True, 0
    
    def increment_brain(self):
        """Increment Paper Brain search counter."""
        self.brain_searches += 1
    
    def increment_chat(self):
        """Increment Paper Chat message counter."""
        self.chat_messages += 1
    
    def mark_api_exhausted(self):
        """Mark API as exhausted, start 30-minute cooldown."""
        self.api_exhausted_at = datetime.now()
    
    def get_remaining_brain_searches(self) -> int:
        """Get number of Brain searches remaining."""
        return max(0, self.MAX_BRAIN_SEARCHES - self.brain_searches)
    
    def get_remaining_chat_messages(self) -> int:
        """Get number of Chat messages remaining."""
        return max(0, self.MAX_CHAT_MESSAGES - self.chat_messages)
    
    def _get_minutes_remaining(self, exhausted_at: datetime, cooldown_minutes: int) -> int:
        """Calculate minutes remaining in cooldown."""
        elapsed = datetime.now() - exhausted_at
        remaining = timedelta(minutes=cooldown_minutes) - elapsed
        
        if remaining.total_seconds() <= 0:
            return 0
        
        return int(remaining.total_seconds() / 60) + 1  # Round up
    
    def get_status(self) -> dict:
        """Get current quota status as dict."""
        brain_allowed, brain_cooldown = self.can_use_brain()
        chat_allowed, chat_cooldown = self.can_use_chat()
        
        return {
            "brain": {
                "allowed": brain_allowed,
                "searches_used": self.brain_searches,
                "searches_remaining": self.get_remaining_brain_searches(),
                "cooldown_minutes": brain_cooldown if not brain_allowed else 0
            },
            "chat": {
                "allowed": chat_allowed,
                "messages_used": self.chat_messages,
                "messages_remaining": self.get_remaining_chat_messages(),
                "cooldown_minutes": chat_cooldown if not chat_allowed else 0
            },
            "api_exhausted": self.api_exhausted_at is not None
        }
