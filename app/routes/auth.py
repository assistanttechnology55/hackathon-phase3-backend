from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import User
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime
import jwt
import os

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-min-32-characters")
ALGORITHM = "HS256"

# ============ Schemas ============
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    token: str
    user: dict

# ============ Auth Endpoints ============

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_session)):
    """User signup"""
    # Check if user exists
    existing_user = db.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = pwd_context.hash(request.password)
    user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate JWT token
    token = create_access_token(str(user.id))
    
    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_session)):
    """User login"""
    # Find user
    user = db.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT token
    token = create_access_token(str(user.id))
    
    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    )

def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
