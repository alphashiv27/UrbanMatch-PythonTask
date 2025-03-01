import enum
from pydantic import BaseModel
from typing import List

class InvalidEmailEnum(enum.Enum):
    INVALID_EMAIL = "Invalid email"
    DUPLICATE_EMAIL = "Duplicate email"
    NO_ERROR = "No error"

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: List[str]

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class InterestFilter(BaseModel):
    gender: set[str]
    city: set[str]
    age_range_start: int
    age_range_end: int

class ValidateEmailResponse(BaseModel):
    is_valid: bool
    
    class Config:
        extra = "allow"

class InvalidEmailResponse(ValidateEmailResponse):
    is_valid: bool = False
    error: InvalidEmailEnum = InvalidEmailEnum.INVALID_EMAIL

class DuplicateEmailResponse(InvalidEmailResponse):
    is_valid: bool = False
    error: InvalidEmailEnum = InvalidEmailEnum.DUPLICATE_EMAIL
    user_id: int

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

