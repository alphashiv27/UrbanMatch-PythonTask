from pydantic import BaseModel
from typing import List

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

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

