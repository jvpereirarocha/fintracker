from pydantic import BaseModel, Field


class PublicToken(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field(..., alias="tokenType")


class JWTPayload(BaseModel):
    sub: str
    exp: int
