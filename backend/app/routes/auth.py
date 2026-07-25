from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email
from app.crud.activity_log import log_activity
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, Token
from app.utils.deps import get_current_user
from app.utils.security import verify_password, create_access_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    user = create_user(db, user_in)
    log_activity(db, "user_registered", user_id=user.id, details={"email": user.email})
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated")

    token = create_access_token({"sub": user.id, "role": user.role.value})
    log_activity(db, "user_logged_in", user_id=user.id)
    return Token(access_token=token, user=user)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
