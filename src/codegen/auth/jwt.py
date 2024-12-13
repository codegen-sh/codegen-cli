import jwt


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False})
