"""
安全相关：密码 bcrypt 哈希存储、JWT 生成
"""
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt

# JWT 配置
SECRET_KEY = "bayes-campus-opinion-secret-key-2026"  # 生产环境请用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时

BCRYPT_ROUNDS = 12


def get_password_hash(password: str) -> str:
    """密码存储：bcrypt 哈希"""
    pwd_bytes = password.encode("utf-8")[:72]  # bcrypt 限制 72 字节
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, stored_password: str) -> bool:
    """密码校验：支持 bcrypt 哈希；若为旧明文则向后兼容"""
    if not stored_password:
        return False
    if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            stored_password.encode("utf-8"),
        )
    return plain_password == stored_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """生成 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """解析 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(token: str | None) -> int | None:
    """从 Authorization Bearer token 中解析用户 ID"""
    if not token or not token.startswith("Bearer "):
        return None
    payload = decode_token(token.replace("Bearer ", ""))
    if not payload or "sub" not in payload:
        return None
    try:
        return int(payload["sub"])
    except (ValueError, TypeError):
        return None
