"""
JStudio API Client for Python

This module provides the main client class for interacting with JStudio's API.
"""

import time
import requests
from typing import Dict, Any, Optional, Union


class JStudioApiError(Exception):
    """Exception raised for JStudio API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, data: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        self.retry_after = self.data.get('retryAfter')


class JStudioClient:
    """
    JStudio API Client
    
    Provides access to JStudio's API endpoints including stocks, weather, items, and calculator.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.joshlei.com", 
                 timeout: int = 30, retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize JStudio client.
        
        Args:
            api_key (str): Your JStudio API key (must start with 'js_')
            base_url (str): API base URL
            timeout (int): Request timeout in seconds
            retries (int): Number of retry attempts
            retry_delay (float): Delay between retries in seconds
        """
        if not api_key:
            raise ValueError("JStudio API key is required")
            
        if not api_key.startswith('js_'):
            raise ValueError("Invalid JStudio key format. API key should start with 'js_'")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        
        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'JStudio-Python-SDK/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            params (dict): Query parameters
            json_data (dict): JSON body data
            
        Returns:
            dict: Response JSON data
            
        Raises:
            JStudioApiError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None
        
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=self.timeout
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', self.retry_delay))
                    if attempt < self.retries:
                        time.sleep(retry_after)
                        continue
                    raise JStudioApiError(
                        "Rate limit exceeded",
                        status_code=429,
                        data={'retryAfter': retry_after}
                    )
                
                # Handle other HTTP errors
                if not response.ok:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    raise JStudioApiError(
                        f"HTTP {response.status_code}: {response.reason}",
                        status_code=response.status_code,
                        data=error_data
                    )
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                break
        
        # If we get here, all retries failed
        raise JStudioApiError(f"Request failed after {self.retries + 1} attempts: {last_error}")
    
    def get_stock(self) -> Dict[str, Any]:
        """Get all stock data."""
        return self._make_request('GET', '/api/stock')
    
    def get_weather(self) -> Dict[str, Any]:
        """Get weather data."""
        return self._make_request('GET', '/api/weather')
    
    def get_info(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Get item information."""
        return self._make_request('GET', '/api/info', params=params)
    
    def get_item_info(self, item_id: str) -> Dict[str, Any]:
        """Get specific item information."""
        return self._make_request('GET', f'/api/info/{item_id}')
    
    def calculate(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Use the calculator API."""
        if params:
            return self._make_request('POST', '/api/calculator', json_data=params)
        return self._make_request('GET', '/api/calculator')
    
    def get_image_url(self, item_id: str) -> str:
        """Get image URL for an item."""
        return f"{self.base_url}/api/images/{item_id}"
    
    # Convenient property-like access (similar to JavaScript version)
    @property
    def stocks(self):
        """Stock-related API methods."""
        class StockAPI:
            def __init__(self, client):
                self.client = client
            
            def all(self):
                return self.client.get_stock()
            
            async def seeds(self):
                stock_data = self.client.get_stock()
                return stock_data.get('seed_stock', [])
            
            def gear(self):
                stock_data = self.client.get_stock()
                return stock_data.get('gear_stock', [])
            
            def eggs(self):
                stock_data = self.client.get_stock()
                return stock_data.get('egg_stock', [])
            
            def cosmetics(self):
                stock_data = self.client.get_stock()
                return stock_data.get('cosmetic_stock', [])
            
            def event_shop(self):
                stock_data = self.client.get_stock()
                return stock_data.get('eventshop_stock', [])
            
            def traveling_merchant(self):
                stock_data = self.client.get_stock()
                return stock_data.get('travelingmerchant_stock', [])
        
        return StockAPI(self)
    
    @property
    def weather(self):
        """Weather-related API methods."""
        class WeatherAPI:
            def __init__(self, client):
                self.client = client
            
            def all(self):
                return self.client.get_weather()
            
            def active(self):
                weather_data = self.client.get_weather()
                return [w for w in weather_data.get('weather', []) if w.get('active')]
        
        return WeatherAPI(self)
    
    @property
    def items(self):
        """Item-related API methods."""
        class ItemAPI:
            def __init__(self, client):
                self.client = client
            
            def all(self, item_type=None):
                params = {'type': item_type} if item_type else None
                return self.client.get_info(params)
            
            def get(self, item_id):
                return self.client.get_item_info(item_id)
            
            def seeds(self):
                return self.client.get_info({'type': 'seed'})
            
            def gear(self):
                return self.client.get_info({'type': 'gear'})
            
            def eggs(self):
                return self.client.get_info({'type': 'egg'})
            
            def cosmetics(self):
                return self.client.get_info({'type': 'cosmetic'})
            
            def events(self):
                return self.client.get_info({'type': 'event'})
            
            def pets(self):
                return self.client.get_info({'type': 'pet'})
            
            def seedpacks(self):
                return self.client.get_info({'type': 'seedpack'})
            
            def weather(self):
                return self.client.get_info({'type': 'weather'})
        
        return ItemAPI(self)
    
    @property
    def calculator(self):
        """Calculator-related API methods."""
        class CalculatorAPI:
            def __init__(self, client):
                self.client = client
            
            def calculate(self, params):
                return self.client.calculate(params)
            
            def get_all_data(self):
                return self.client.calculate()
        
        return CalculatorAPI(self)
    
    @property
    def images(self):
        """Image-related API methods."""
        class ImageAPI:
            def __init__(self, client):
                self.client = client
            
            def get_url(self, item_id):
                return self.client.get_image_url(item_id)
        
        return ImageAPI(self)
