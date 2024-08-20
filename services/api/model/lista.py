from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Relationship, Field

from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from .eleccion import Eleccion

class ListaEleccionCreate(SQLModel):
    lista_id: int = Field(foreign_key="lista.id", primary_key=True)

class ListaEleccion(ListaEleccionCreate, table=True):
    eleccion_id: int = Field(foreign_key="eleccion.id", primary_key=True)#, ondelete="CASCADE"

    # TODO: Tal vez aca tambien almacenar el nombre de la lista
    # permitiendo que la lista original se elimine.. pero quede la info aca

    # votos : List["VotoListaEleccion"] = Relationship(back_populates="lista",link_model=Lista)

#********************************************************************************
#################################################################################
#********************************************************************************
class ListaBase(SQLModel):
    nombre: str
    descripcion: str

class Lista(ListaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    elecciones: List["Eleccion"] = Relationship(link_model=ListaEleccion, back_populates="listas")

    def __gt__(a, b): return a.nombre>b.nombre
    def __lt__(a, b): return a.nombre<b.nombre
    def __eq__(a, b): return a.nombre==b.nombre

class ListaCreate(ListaBase):
    pass
