from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class CurrentUser(BaseModel):
    id_user: int
    email: str
    role: str
    id_anonyme: str

    model_config = {"from_attributes": True}
