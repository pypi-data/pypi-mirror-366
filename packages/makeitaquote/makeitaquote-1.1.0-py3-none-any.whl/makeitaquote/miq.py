import requests
from typing import Optional, Any, Dict
from .config import BETA_API_URL
from .utils import remove_markdown


class MiQ:
    """
    The MiQ class for creating Discord-style quote images using the beta API.
    """
    
    def __init__(self):
        self.format = {
            "text": "",
            "avatar": None,
            "username": "",
            "display_name": "",
            "color": False,
            "watermark": ""
        }
    
    def set_text(self, text: str, format_text: bool = False) -> 'MiQ':
        if not isinstance(text, str):
            raise TypeError("Text must be string")
        processed_text = remove_markdown(text) if format_text else text
        self.format["text"] = processed_text
        return self
    
    def set_avatar(self, avatar: Optional[str]) -> 'MiQ':
        if avatar is not None and not isinstance(avatar, str):
            raise TypeError("Avatar must be string or None")
        self.format["avatar"] = avatar
        return self
    
    def set_username(self, username: str) -> 'MiQ':
        if not isinstance(username, str):
            raise TypeError("Username must be string")
        self.format["username"] = username
        return self
    
    def set_displayname(self, display_name: str) -> 'MiQ':
        if not isinstance(display_name, str):
            raise TypeError("Display name must be string")
        self.format["display_name"] = display_name
        return self
    
    def set_color(self, color: bool = False) -> 'MiQ':
        if not isinstance(color, bool):
            raise TypeError("Color must be boolean")
        self.format["color"] = color
        return self
    
    def set_watermark(self, watermark: str) -> 'MiQ':
        if not isinstance(watermark, str):
            raise TypeError("Watermark must be string")
        self.format["watermark"] = watermark
        return self
    
    def set_from_message(self, message: Any, format_text: bool = False) -> 'MiQ':
        self.set_text(message.content, format_text)
        
        if hasattr(message, 'member') and message.member:
            avatar_url = message.member.display_avatar.url
        else:
            avatar_url = message.author.display_avatar.url
        self.set_avatar(avatar_url)
        
        if hasattr(message.author, 'discriminator') and message.author.discriminator != '0':
            username = f"{message.author.name}#{message.author.discriminator}"
        else:
            username = message.author.name
        self.set_username(username)
        
        if hasattr(message, 'member') and message.member:
            display_name = message.member.display_name
        elif hasattr(message.author, 'global_name') and message.author.global_name:
            display_name = message.author.global_name
        else:
            display_name = message.author.name
        self.set_displayname(display_name)
        
        return self
    
    def generate_beta(self) -> bytes:
        """Generate quote using beta API."""
        if not self.format["text"]:
            raise ValueError("Text is required")
        
        try:
            response = requests.post(BETA_API_URL, json=self.format)
            response.raise_for_status()
            return response.content
            
        except requests.RequestException as error:
            raise requests.RequestException(f"Failed to generate quote: {str(error)}")
    
    def get_format(self) -> Dict[str, Any]:
        return self.format.copy()
