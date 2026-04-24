class PlaylistDataNormalizer:
    def __init__(self):
        self.flatten_data = {'kind' : [], 'etag' : [], 'id' : [], 'publishedAt' : [],
                        'channelId' : [], 'title' : [], 'description' : [], 'url' : [],
                        'channelTitle' : [], 'playlistId' : [], 'position' : [],
                        'kind' : [], 'videoId' : [], 'videoOwnerChannelTitle' : [], 'videoOwnerChannelId' : []}
    def __call__(self, data):
        for v in data['items']:
            if v['snippet']['title'] == "Private video" or v['snippet']['title'] == "Deleted video":
                continue
            self.flatten_data['kind'].append(v['kind'])
            self.flatten_data['etag'].append(v['etag'])
            self.flatten_data['id'].append(v['id'])
            self.flatten_data['publishedAt'].append(v['snippet']['publishedAt'])
            self.flatten_data['channelId'].append(v['snippet']['channelId'])
            self.flatten_data['title'].append(v['snippet']['title'])
            self.flatten_data['description'].append(v['snippet']['description'])
            self.flatten_data['url'].append(v['snippet']['thumbnails']['high']['url'])
            self.flatten_data['channelTitle'].append(v['snippet']['channelTitle'])
            self.flatten_data['playlistId'].append(v['snippet']['playlistId'])
            self.flatten_data['position'].append(v['snippet']['position'])
            self.flatten_data['kind'].append(v['snippet']['resourceId']['kind'])
            self.flatten_data['videoId'].append(v['snippet']['resourceId']['videoId'])
            self.flatten_data['videoOwnerChannelTitle'].append(v['snippet']['videoOwnerChannelTitle'])
            self.flatten_data['videoOwnerChannelId'].append(v['snippet']['videoOwnerChannelId'])

    def get_flatten_data(self):
        return self.flatten_data

    def get_number_of_videos(self):
        return len(self.flatten_data['id'])

    def __str__(self):
        text = ', '.join(self.flatten_data.keys()) + '\n'
        for i in range(len(self.flatten_data['id'])):
            text += ','.join(['"' + str(self.flatten_data[key][i]).replace(f'\n', f'\/nr')+ '"' for key in self.flatten_data.keys()]) + '\n'
        return text

    def get_header_and_data(self):
        header = list(self.flatten_data.keys())
        data = []
        for i in range(len(self.flatten_data['id'])):
            data.append(tuple(self.flatten_data[key][i] for key in self.flatten_data.keys()))
        return header, data