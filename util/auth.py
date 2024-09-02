import os, sys
import base64

def get_auth_header() -> str:
    email, token = os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')
    if not token:
        print("Environment variable 'JIRA_API_TOKEN' is not set.")
        sys.exit(1)
    return f"Basic {base64.b64encode(f"{email}:{token}".encode('utf-8')).decode('utf-8')}" if email else f"Basic {token}"