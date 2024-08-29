import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract(endpoint):

    jira_domain = os.getenv('JIRA_DOMAIN')
    token = os.getenv('JIRA_API_TOKEN')
    
    if not jira_domain or not token:
        logging.error("Environment variables 'JIRA_DOMAIN' or 'JIRA_API_TOKEN' are not set.")
        return None
    
    jira_url = f"https://{jira_domain}.atlassian.net/{endpoint}"
    headers = {
        'Authorization': f'Basic {token}'
    }

    try:
        response = requests.get(jira_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Error occurred during request: {req_err}")
    except ValueError as json_err:
        logging.error(f"JSON decode error: {json_err}")
    except Exception as err:
        logging.error(f"An unexpected error occurred: {err}")
    
    return None