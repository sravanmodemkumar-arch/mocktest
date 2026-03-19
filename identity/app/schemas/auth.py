from pydantic import BaseModel, Field


class SendOTPRequest(BaseModel):
    mobile: str = Field(..., pattern=r"^[6-9]\d{9}$", description="10-digit Indian mobile number")


class VerifyOTPRequest(BaseModel):
    mobile: str = Field(..., pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
