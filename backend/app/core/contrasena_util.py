from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()  # Argon2id

_DUMMY_HASH = password_hash.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    return password_hash.verify(password, hashed or _DUMMY_HASH) and hashed is not None
