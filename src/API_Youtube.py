import logging


from API_Base import BaseAPI

    
class Mid_level_API(BaseAPI):
    def __init__(self, api_key):
        super().__init__(api_key, "https://www.googleapis.com/youtube/v3")

    def get_channel_id(self, username):
        params = {
            'part': 'id',
            'forHandle': username
        }
        result = self._request('channels', params)
        return result['items'][0]['id'] if result else result
    
    def get_playlist_id(self, channel_id):
        params = {
            'part': 'contentDetails',
            'id': channel_id
        }
        result = self._request('channels', params)
        return result
    
    def get_uploads_playlist_id(self, channel_id):
        playlist_id = self.get_playlist_id(channel_id)
        try :
            return playlist_id['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        except KeyError:
            logging.error(f"Error: No uploads playlist found for channel ID {channel_id}")
            return None

    def get_videos_by_playlist(self, playlist_id, page_token=None, max_results=10):
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': max_results
        }
        if page_token:
            params['pageToken'] = page_token
        return self._request('playlistItems', params)

    def return_video_from_playlist(self, playlist_id, max_output_length=None, max_results=50):
        from JSON_Youtube_Playlist import PlaylistDataNormalizer
        data_normalizer = PlaylistDataNormalizer()
        next_page_token = None
        page_count = 0
        while True:
            result = self.get_videos_by_playlist(playlist_id, page_token=next_page_token, max_results=max_results)
            logging.info(f"Récupération de la page {next_page_token} pour la playlist ID '{playlist_id}' : {data_normalizer.get_number_of_videos()} vidéos")
            data_normalizer(result)
            next_page_token = result.get('nextPageToken')
            if (max_output_length and data_normalizer.get_number_of_videos() >= max_output_length) or not next_page_token: break
            page_count += 1
        return data_normalizer, page_count

    def get_user_uploads(self, username):
        channel_id = self.get_channel_id(username)
        logging.info(f"Récupération de l'ID de la chaîne pour le nom d'utilisateur '{username}' : {channel_id}")
        uploads_playlist_id = self.get_uploads_playlist_id(channel_id)
        return uploads_playlist_id

class High_level_API(Mid_level_API):
    def get_all_videos(self, search, type = 'USER', max_results = 50, max_output_length=None):
        if type == 'USER': id = self.get_user_uploads(search)
        if type == 'PLAYLIST': id = search
        data, page_count = self.return_video_from_playlist(id, max_output_length, max_results)
        logging.info(f"Récupéré {data.get_number_of_videos()} vidéos en {page_count} pages")
        return data