from util import get_auth_header
import requests

def make_api_request(url: str) -> dict:
    try:
        response = requests.get(url, headers={'Authorization': get_auth_header()})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None