from pydantic import BaseModel, ConfigDict, field_validator


class UserBase(BaseModel):
    username: str
    sub: str
    name: str
    email: str
    email_verified: str | None
    salt: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    username: str
    sub: str
    name: str
    email: str
    email_verified: bool | None


class TempUserCreate(UserBase):
    username: str
    password: str
    name: str
    email: str


class UserEmailVerified(UserBase):
    username: str


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str

    @field_validator('old_password')
    @classmethod
    def old_password_is_not_blank(cls, value):
        if not value:
            raise ValueError("Old password field can't be blank!!!")
        return value

    @field_validator('new_password')
    @classmethod
    def new_password_is_not_blank(cls, value):
        if not value:
            raise ValueError("New password field can't be blank!!!")
        return value
