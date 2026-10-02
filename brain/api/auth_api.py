from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from brain.auth.dependencies import get_current_user
from brain.auth.security import create_access_token, hash_password, verify_password
from brain.database.session import get_db
from brain.models.user import User
from brain.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    # -----------------------------------------
    # 1. Check whether email already exists
    # -----------------------------------------

    email = str(request.email).lower()
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # -----------------------------------------
    # 2. Hash password
    # -----------------------------------------

    password_hash = hash_password(
        request.password
    )

    # -----------------------------------------
    # 3. Create user
    # -----------------------------------------

    user = User(
        email=email,
        password_hash=password_hash
    )

    # -----------------------------------------
    # 4. Save to database
    # -----------------------------------------

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to create account.") from exc

    # -----------------------------------------
    # 5. Response
    # -----------------------------------------

    return RegisterResponse(
        message="Account created successfully.",
        email=user.email,
    )


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.email == request.account_email).first()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return LoginResponse(
        access_token=create_access_token(user.id),
        user=UserResponse(id=user.id, email=user.email),
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email)