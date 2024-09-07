from pydantic import BaseModel


class PublicToken(BaseModel):
    access_token: str
    token_type: str


class JWTPayload(BaseModel):
    sub: str
    exp: int
