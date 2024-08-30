def get_value_by_field_id(data, field_id):
    for item in data:
        if item['field_id'] == field_id:
            return item['value']
    return None
