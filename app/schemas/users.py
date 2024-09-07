from typing import Self
from pydantic import BaseModel, EmailStr, model_validator, Field


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str = Field(alias='confirmPassword')

    @model_validator(mode='after')
    def validate_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")
        return self


class LoginUser(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    email: str
