import sys
    
sys.path.append('src_web/src')
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


    def get_all_data(self, release_id, no_key=True):
        memory_base_url = self.base_url
        self.base_url = "https://api.discogs.com/releases"
        try:
            result = self._request(release_id, {}, no_key=no_key)
            self.base_url = memory_base_url
            return result
        except Exception as e:
            print(f"Failed to get all data for release ID {release_id} with error: {e}")
            self.base_url = memory_base_url
            return None