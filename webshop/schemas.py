from pydantic import BaseModel, EmailStr


class User(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: EmailStr
    password: str


class UserInDB(User):
    hashed_password: str


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str