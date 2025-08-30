# Utility for generating secure API keys
import secrets
import string

def generate_api_key(length=40):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
