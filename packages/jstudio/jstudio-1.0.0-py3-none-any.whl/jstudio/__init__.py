"""
JStudio Python SDK

Official Python SDK for JStudio's API & WebSocket services.
Fast, reliable API for real-time data from Various Games (Roblox).
"""

from .client import JStudioClient, JStudioApiError

__version__ = "1.0.0"
__author__ = "JStudio"
__email__ = "contact@joshlei.com"

def connect(api_key, **kwargs):
    """
    Connect to JStudio API with your API key.
    
    Args:
        api_key (str): Your JStudio API key (starts with 'js_')
        **kwargs: Additional configuration options
        
    Returns:
        JStudioClient: Connected client instance
        
    Example:
        >>> import jstudio
        >>> client = jstudio.connect('js_your_api_key_here')
        >>> stocks = client.stocks.all()
    """
    return JStudioClient(api_key, **kwargs)

__all__ = ['connect', 'JStudioClient', 'JStudioApiError']
