from util import token
import requests

def extract(url):
    headers = {'Authorization': f'Basic {token()}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
