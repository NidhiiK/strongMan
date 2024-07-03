import secrets
import string

def generate_psk(length=52):
    alphabet = string.ascii_letters + string.digits
    psk = ''.join(secrets.choice(alphabet) for _ in range(length))
    return psk
