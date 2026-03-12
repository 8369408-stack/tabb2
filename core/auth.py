import time
import json
import hmac
import hashlib
import base64

from fastapi import Request, HTTPException

from core.config import ConfigManager, hash_password

TOKEN_EXPIRY = 86400  # 24 小时


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def create_jwt(config: ConfigManager) -> str:
    secret = config.get("admin", "jwt_secret")
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(
        json.dumps({"role": "admin", "exp": int(time.time()) + TOKEN_EXPIRY}).encode()
    )
    signature = _b64url_encode(
        hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def verify_jwt(token: str, config: ConfigManager) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("invalid token format")
        header_b64, payload_b64, sig_b64 = parts
        secret = config.get("admin", "jwt_secret")
        expected_sig = _b64url_encode(
            hmac.new(
                secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
            ).digest()
        )
        if not hmac.compare_digest(sig_b64, expected_sig):
            raise ValueError("invalid signature")
        payload = json.loads(_b64url_decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            raise ValueError("token expired")
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


def verify_password(password: str, config: ConfigManager) -> bool:
    stored_hash = config.get("admin", "password_hash")
    salt = config.get("admin", "salt")
    computed, _ = hash_password(password, salt)
    return hmac.compare_digest(computed, stored_hash)


def require_admin(config: ConfigManager):
    """返回一个 FastAPI 依赖函数"""

    async def dependency(request: Request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing token")
        token = auth[7:]
        return verify_jwt(token, config)

    return dependency
