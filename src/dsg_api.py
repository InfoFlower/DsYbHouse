from BaseApi import BaseAPI
import time

class Mid_level_API(BaseAPI):
    def __init__(self, api_key):
        super().__init__(api_key, "https://api.discogs.com/database")

    def get_release_id(self, q, title=None, artist=None):
        params = {
            'q': q,
            'release_title': title,
            'artist': artist,
            'type': 'release'
        }
        try : 
            result = self._request('search', params)
        except Exception as e:
            attempt = 1
            time.sleep(2 ** attempt)
            print(f"Error fetching release ID for {q}: {e}")
            result = None
        return result

if __name__ == "__main__":
    from methods import db_manager
    from json_handling import save_json
    conn = db_manager()
    api_key = "NONE"
    api = Mid_level_API(api_key)
    header, data = conn.read_db(query="select title from music;")
    for i in data:
        releases = api.get_release_id(q=i[0])
        save_json(releases, f"C:/Users/lenovo/Desktop/HomeLab/HOUSIFY/src/py_data/{i[0]}.json")