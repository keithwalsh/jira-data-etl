from dotenv import load_dotenv
import os, sys
import base64 as b64

def base64(input_string):
    return b64.b64encode(input_string.encode('utf-8')).decode('utf-8')

def token():

    load_dotenv()
    jira_email, jira_api_token = os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')
    
    if not jira_api_token:
        print("Environment variables 'JIRA_EMAIL' or 'JIRA_API_TOKEN' are not set.")
        sys.exit(1)
        
    return base64(f"{jira_email}:{jira_api_token}") if jira_email else jira_api_token