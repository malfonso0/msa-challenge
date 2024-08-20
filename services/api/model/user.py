from typing import List, Optional
from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlmodel import SQLModel, Relationship, Field
from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def hash_verify(password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(password, hashed_password)

class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)


class UserBase(SQLModel):
    nombre: str
    email:  EmailStr = Field(sa_column=Column("email", String, unique=True, index=True)) 

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    roles: list["Role"] = Relationship(back_populates="usuarios", link_model=UserRole)
    hashed_password: str = Field()


class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id:int
    roles: list["Role"] = Relationship(back_populates="usuarios", link_model=UserRole)

class UserUpdate(SQLModel):
    # Dont allow to update email for now
    nombre: str | None = None
    password: str | None = None


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

    usuarios: List["User"] = Relationship(back_populates="roles", link_model=UserRole)

