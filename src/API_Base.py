import requests

class BaseAPI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
    
    def _request(self, endpoint, params):
        """Requête générique à l'API YouTube"""
        params['key'] = self.api_key
        response = requests.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()