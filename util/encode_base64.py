import base64

def encode_base64(input_string):
    return base64.b64encode(input_string.encode('utf-8')).decode('utf-8')