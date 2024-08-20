from fastapi import APIRouter, Depends, HTTPException
from model import Lista, ListaCreate
from typing import List, Annotated

from routes.security import (
    db_dependency,
    writer_user_dependency,
    get_current_user,
)

lista_router = APIRouter(tags=["listas"], dependencies= [Depends(get_current_user)] )

@lista_router.post("/listas/", response_model=Lista, dependencies= [writer_user_dependency] )
def create_lista(lista: ListaCreate, session: db_dependency):
    db_lista = Lista.model_validate(lista)
    session.add(db_lista)
    session.commit()
    session.refresh(db_lista)
    return db_lista

@lista_router.get("/listas/", response_model=List[Lista])
def read_listas(session: db_dependency):
    return session.query(Lista).all()

@lista_router.get("/listas/{lista_id}", response_model=Lista)
def read_lista(lista_id: int, session: db_dependency):
    return session.get(Lista, lista_id)

@lista_router.delete("/listas/{lista_id}", dependencies= [writer_user_dependency])
def delete_lista(lista_id: int, session: db_dependency):
    db_lista = session.get(Lista, lista_id)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="Lista not found")
    try:
        session.delete(db_lista)
        session.commit()
        return {"message": "Lista deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))