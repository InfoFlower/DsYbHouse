import json
import os
def save_json(data, filename):
    try :
        with open(filename, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving JSON to {filename}: {e}")

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# DATA STRUCTURE FUNCTION
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
            print(v['etag'])
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
    
class SingleLayerDataNormalizer :
    def __init__(self):
        self.i=0
        self.flatten_data = {'Z_tech_index' : []}

    def __call__(self, data, sub_key= 'results'):
        if data : 
            if sub_key in data:
                print(f"Processing {len(data[sub_key])} items in {sub_key}...")
                for item in data[sub_key]:
                    for k, v in item.items():
                        if k in self.flatten_data:
                            self.flatten_data[k].append(v)
                        else:
                            print(f"Adding new key '{k}' to flatten_data.")
                            self.flatten_data[k] = [v]
                    self.i += 1
                    self.flatten_data['Z_tech_index'].append(self.i)

        return None

    def get_flatten_data(self):
        return self.flatten_data

    def get_number_of_videos(self):
        return len(self.flatten_data['Z_tech_index'])

    def __str__(self):
        text = ', '.join('"'+key+'"' for key in self.flatten_data.keys()) + '\n'
        for i in range(len(self.flatten_data['Z_tech_index'])):
            text += ','.join(['"' + str(self.flatten_data[key][i]).replace('"', '')+ '"' if len(self.flatten_data[key]) > i else '""' for key in self.flatten_data.keys()]) + '\n'
        return text

    def get_header_and_data(self):
        header = list(self.flatten_data.keys())
        data = []
        for i in range(len(self.flatten_data['Z_tech_index'])):
            data.append(tuple(self.flatten_data[key][i] if len(self.flatten_data[key]) > i else None for key in self.flatten_data.keys()))
        return header, data

if __name__ == "__main__":
    normalizer = SingleLayerDataNormalizer()
    for i in os.listdir('src/py_data'):
        if i.endswith('.json'):
            print(f"Processing path ===  'src/py_data/{i}' ===")
            playlist_data = load_json(f'src/py_data/{i}')
            normalizer(playlist_data)
            print(f"Number of items processed: {normalizer.get_number_of_videos()}")
    with open('discogs_data.csv', 'w', encoding='utf-8') as f:f.write(str(normalizer))