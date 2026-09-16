import base64


def get_auth_header(email: str | None, token: str | None) -> str | None:
    """Basic auth for Jira Cloud (email:token) or a bare token; None means request anonymously."""
    if not token:
        return None
    if email:
        return f"Basic {base64.b64encode(f'{email}:{token}'.encode('utf-8')).decode('utf-8')}"
    return f'Basic {token}'
