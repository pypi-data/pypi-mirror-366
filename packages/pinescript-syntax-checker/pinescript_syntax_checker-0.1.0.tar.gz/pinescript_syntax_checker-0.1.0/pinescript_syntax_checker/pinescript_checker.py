import httpx
import json
import argparse
from pathlib import Path
import sys

class PineScriptChecker:
    def __init__(self, username="admin"):
        self.username = username
        self.api_url = f"https://pine-facade.tradingview.com/pine-facade/translate_light?user_name={username}&v=3"
        self.headers = {
            'Referer': 'https://www.tradingview.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'DNT': '1',
        }

    async def check_syntax(self, pine_code):
        """
        Check PineScript code syntax
        
        Args:
            pine_code (str): PineScript source code
            
        Returns:
            dict: Dictionary containing check results
        """
        try:
            # Build multipart form data
            files = self._build_multipart_data(pine_code)
            
            # Send request using httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    files=files,
                    headers=self.headers,
                    timeout=10.0
                )
                # Parse response
                result = response.json()
                return result
            
        except httpx.RequestError as e:
            return {
                'success': False,
                'error': f'Network request failed: {str(e)}',
                'errors': []
            }

    def _build_multipart_data(self, pine_code, boundary=None):
        """Build multipart form data - using standard format"""
        # Using httpx files parameter is more reliable
        return {
            'source': (None, pine_code)
        }


