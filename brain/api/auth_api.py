from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from brain.auth.security import hash_password
from brain.database.session import get_db
from brain.models.user import User
from brain.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
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

    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

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
        email=request.email,
        password_hash=password_hash
    )

    # -----------------------------------------
    # 4. Save to database
    # -----------------------------------------

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create account.",
        )

    # -----------------------------------------
    # 5. Response
    # -----------------------------------------

    return RegisterResponse(
        message="Account created successfully.",
        email=user.email,
    )