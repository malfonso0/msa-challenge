from typing import List,Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import select, Session
from model import Role, User, UserCreate, UserPublic, hash_password
from routes.security import (
    db_dependency,
    admin_user_dependency,
    get_db
)
user_router = APIRouter(tags=["users"], dependencies= [admin_user_dependency] )#

@user_router.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate, session: db_dependency):
    hashed_password = hash_password(user.password)
    extra_data = {"hashed_password": hashed_password}
    db_user = User.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@user_router.get("/users/", response_model=List[UserPublic])
def read_users(session: db_dependency,
                offset: int = 0,
                limit: int = Query(default=100, le=100),
                ):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@user_router.get("/users/{user_id}", response_model=UserPublic)
def read_user(user_id: int, session: db_dependency):
    user =  session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.delete("/users/{user_id}")
def delete_user(user_id: int,session: db_dependency):
    db_user = session.query(User).filter(User.id == user_id).first()
    session.delete(db_user)
    session.commit()
    return {"message": "User deleted successfully"}

@user_router.get("/users/{user_id}/roles/", response_model=List[Role])
def get_user_roles(user_id: int, session: db_dependency):
    user = session.query(User).filter(User.id == user_id).first()
    return user.roles

@user_router.post("/users/{user_id}/roles/")
def add_role_to_user(user_id: int, role_id: str, session: db_dependency):
    user = session.query(User).filter(User.id == user_id).first()
    role = session.query(Role).filter(Role.id == role_id).first()
    if role not in user.roles:
        user.roles.append(role)
        session.commit()
        return {"status": "ok"}

    raise HTTPException(status_code=400, detail="Usuario ya tiene el rol especificado")

@user_router.delete("/users/{user_id}/roles/{role_id}")
def remove_role_from_user(user_id: int, role_id: int, session: db_dependency):
    user = session.query(User).filter(User.id == user_id).first()
    role = session.query(Role).filter(Role.id == role_id).first()
    if role in user.roles:
        user.roles.remove(role)
        session.commit()
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="El usuario no tiene el rol especificado")

