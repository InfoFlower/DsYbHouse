def build_condition(header, data, on, type_of_struct, type_of_condition='supp'):
    nb = 0
    first = True
    condition = ""
    condition_params = []
    for i, h in enumerate(header):
        if h in on:
            if not first:
                condition += " OR " if type_of_condition == 'comp' else " AND "
            if type_of_struct == 'column':
                unique_values = data[i]
                first = False
            if type_of_struct == 'row':
                unique_values = list(set(row[i] for row in data))
                first = False
            if unique_values not in condition_params:
                if isinstance(unique_values,list):
                    condition_params.extend(unique_values)
                else:
                    condition_params.append(unique_values)
            placeholders = ', '.join([f"'{i}'" for i in condition_params])
            condition += f'"{h}" IN ({placeholders})'
            nb += 1
        if nb >= len(on):
            break
    return condition, condition_params


def try_reorganize_data(data):
    modified_data = []
    first = True
    for i in data :
        if first :
            mapped = len(i)
        if len(i)<mapped :
            i = i + [None]*(mapped-len(i))
            modified_data.append(i)
        elif len(i)>mapped :
            i = i[:mapped]
            modified_data.append(i)
        else :
            modified_data.append(i)
        first = False
    return modified_data