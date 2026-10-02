from pydantic import BaseModel, EmailStr, Field, model_validator

class RegisterRequest(BaseModel):
    email : EmailStr

    password : str = Field(
        min_length=8,
        max_length = 128,
    )

class RegisterResponse(BaseModel):
    message : str
    email : EmailStr


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def require_account_identifier(self) -> "LoginRequest":
        if not self.email and not self.username:
            raise ValueError("Email or username is required.")
        return self

    @property
    def account_email(self) -> str:
        return str(self.email or self.username or "").strip().lower()


class UserResponse(BaseModel):
    id: int
    email: EmailStr


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
        