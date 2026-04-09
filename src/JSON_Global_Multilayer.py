
class JSON_Global_Multilayer :
    def __init__(self, identifier):
        self.identifier = identifier

    def __normalize_level(self, json_data, table_name = "None"):
        result = {}
        identifier = f"{self.identifier}_main" if f"{self.identifier}_main" in json_data else self.identifier
        result[f"{self.identifier}_main"] = json_data[identifier]
        to_normalize = []
        for k, v in json_data.items() :
            if isinstance(v, dict):
                v[f"{self.identifier}_main"] = json_data[identifier]
                to_normalize.append((k, v))
            elif isinstance(v, list):
                if len(v) > 0 and not isinstance(v[0], dict):
                    result[k] = v
                    
                elif len(v) > 0 and isinstance(v[0], dict):
                    inverted_json = self.invert_json(v)
                    inverted_json[f"{self.identifier}_main"] = [json_data[identifier]]*len(v)
                    to_normalize.append((k, inverted_json))
            else :
                result[k] = v
        return {'table_name': table_name, 'json_data': result}, to_normalize
    
    def invert_json(self, json_data):
        dict_of_list = {}
        for item in json_data:
            for key, value in item.items():
                if key not in dict_of_list:
                    dict_of_list[key] = []
                dict_of_list[key].append(value)
        return dict_of_list

    def final_normalization(self, json_data):
        for i in json_data:
            if isinstance(json_data[i], list) and len(json_data[i]) == 1:
                json_data[i] = json_data[i][0]
            if isinstance(json_data[i], dict):
                json_data[i] = self.final_normalization(json_data[i])
        return json_data

    def walker(self, json_data, table_name = "None"):
        relationnal_db = {}
        
        if isinstance(json_data, dict):
            unit_table, to_normalize = self.__normalize_level(json_data, table_name)
            relationnal_db[unit_table['table_name']] = unit_table['json_data']
            for sub_table_name, sub_json_data in to_normalize:
                sub_result = self.walker(sub_json_data, sub_table_name)
                relationnal_db.update(sub_result)
        else :
             relationnal_db[table_name] = json_data
        return self.final_normalization(relationnal_db)