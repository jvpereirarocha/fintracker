from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.domain.exceptions.auth import PasswordsDontMatchException


class UserCredentialsDTO(BaseModel):
    username: str
    password: str


class CreateUserDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str = Field(alias="confirmPassword")
    
    @model_validator(mode="after")
    def validate_password(self) -> Self:
        if self.password != self.confirm_password:
            raise PasswordsDontMatchException(
                message="The passwords don't match"
            )
        return self


class PublicTokenResponse(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(serialization_alias="tokenType")


class UserPublicResponse(BaseModel):
    username: str
    email: str