class SingleLayerDataNormalizer :
    def __init__(self):
        self.i=0
        self.flatten_data = {'Z_tech_index' : []}

    def __call__(self, data, sub_key= 'results', added_key = None, added_value = None):
        if data : 
            if sub_key in data:
                for item in data[sub_key]:
                    for k, v in item.items():
                        if k in self.flatten_data:
                            self.flatten_data[k].append(v)
                        else:
                            self.flatten_data[k] = [v]
                    self.i += 1
                    self.flatten_data['Z_tech_index'].append(self.i)
                    if added_key and added_value:
                        if added_key in self.flatten_data:
                            self.flatten_data[added_key].append(added_value)
                        else:
                            self.flatten_data[added_key] = [added_value]

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
    import os
    from src_backend.src.JSON_Basic import load_json
    normalizer = SingleLayerDataNormalizer()
    for i in os.listdir('src/py_data'):
        if i.endswith('.json'):
            playlist_data = load_json(f'src/py_data/{i}')
            normalizer(playlist_data)
    with open('discogs_data.csv', 'w', encoding='utf-8') as f:f.write(str(normalizer))