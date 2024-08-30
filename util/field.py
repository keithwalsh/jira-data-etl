def field_type(key, mode='standard'):
    if mode == 'standard':
        return not key.startswith('customfield_')
    elif mode == 'custom':
        return key.startswith('customfield_')
    else:
        raise ValueError("Invalid mode specified. Use 'standard' or 'custom'.")

def get_value(data, field_id):
    for item in data:
        if item['field_id'] == field_id:
            return item['value']
    return None
