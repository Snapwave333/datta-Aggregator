"""Authentication and authorization for API."""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config import settings
from src.models import get_db, User, Subscription, SubscriptionTier
from src.api.schemas import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_api_key() -> str:
    """Generate a random API key."""
    return f"daas_{secrets.token_urlsafe(32)}"


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    company_name: Optional[str] = None,
    is_admin: bool = False,
) -> User:
    """Create a new user with default subscription."""
    # Hash password
    hashed_password = get_password_hash(password)

    # Create user
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        company_name=company_name,
        is_admin=is_admin,
        api_key=generate_api_key(),
    )
    db.add(user)
    db.flush()

    # Create default subscription
    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.FREE,
        api_calls_per_day=100,
        max_results_per_query=50,
    )
    db.add(subscription)

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try API key first
    if api_key:
        user = db.query(User).filter(User.api_key == api_key).first()
        if user and user.is_active:
            return user

    # Try JWT token
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )
        return user

    raise credentials_exception


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current user and verify they are an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def check_rate_limit(user: User, db: Session) -> bool:
    """Check if user has exceeded their daily API rate limit."""
    if not user.subscription:
        return False

    sub = user.subscription

    # Reset counter if it's a new day
    if sub.last_api_call_at:
        if sub.last_api_call_at.date() < datetime.utcnow().date():
            sub.api_calls_today = 0

    # Check limit
    if sub.api_calls_today >= sub.api_calls_per_day:
        return False

    # Increment counter
    sub.api_calls_today += 1
    sub.last_api_call_at = datetime.utcnow()
    sub.total_api_calls += 1
    db.commit()

    return True
