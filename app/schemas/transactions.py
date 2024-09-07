from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    description: str
    value: str = Field(alias="amount", default="")
    date: str = Field(alias="registration_date", default="")