"""
Composio tool configuration wrapper for clean API.
"""

from typing import List, Optional


class Composio:
    """
    Simple wrapper for Composio tool configuration.
    
    Usage:
        tools = Composio("TWITTER", "GITHUB", "GMAIL")
        agent = Agent(OpenAIProvider(), tools, billing="user")
    """
    
    def __init__(self, *toolkits: str, auth_file: str = "src/config/composio-tools.txt"):
        """
        Initialize Composio configuration.
        
        Args:
            *toolkits: Variable number of toolkit names (e.g., "TWITTER", "GITHUB")
            auth_file: Path to auth config file (default: "composio-tools.txt")
        """
        self.toolkits = list(toolkits)
        self.auth_file = auth_file
        self.provider_name = "composio"
    
    def __repr__(self) -> str:
        toolkits_str = ", ".join(self.toolkits)
        return f"Composio({toolkits_str})"
    
    def get_toolkits(self) -> List[str]:
        """Get list of configured toolkits."""
        return self.toolkits
    
    def get_auth_file(self) -> str:
        """Get path to auth config file."""
        return self.auth_file