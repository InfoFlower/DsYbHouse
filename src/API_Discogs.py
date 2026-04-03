from unittest import result

from API_Base import BaseAPI
import time

class Mid_level_API(BaseAPI):
    def __init__(self, api_key):
        super().__init__(api_key, "https://api.discogs.com/database")

    def get_release_id(self, q, title=None, artist=None):
        def wrapper(params, attempt=1, max_retries=3):
            try : 
                result = self._request('search', params)
            except Exception as e:
                print(f"Attempt {attempt} failed with error: {e}, number of retries left: {max_retries - attempt}")
                if attempt <= max_retries:
                    time.sleep(2 ** attempt)
                    result = wrapper(params, attempt + 1)
                else:
                    result = None
            return result
        params = {
            'q': q,
            'release_title': title,
            'artist': artist,
            'type': 'release'
        }
        return wrapper(params)