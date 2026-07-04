import secrets


def get_secret_key(existing: str | None = None) -> str:
    """Return configured Flask secret key or generate one automatically."""
    if existing and existing.strip():
        return existing.strip()
    return secrets.token_hex(32)
