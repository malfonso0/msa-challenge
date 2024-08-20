from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Relationship, Field
from .user import User, UserPublic
from .lista import ListaEleccion, Lista

class VotoEleccionCreate(SQLModel):
    mesa: int = Field(primary_key=True) #unique=True #->para la eleccion

    votos: int
    lista_id: int = Field(foreign_key="lista.id", primary_key=True)
    # Ejemplo.. si solo se cargaran totales por mesa.. no por dni..

class VotoListaEleccion(VotoEleccionCreate, table=True):

    # En este ejemplo.. la clave sera mesa, eleccion y lista. ya que solo se permitira 1 de ese triplo
    # en algun otro modelo.. se podria tener aca un id autoincremental
    # id: int = Field(default=None, primary_key=True)

    #TODO: Agregar otros campos como ciudad, cp escuela.. cosas del estilo,
    #  nro maquina.. etc
    # permitiria tener mejor control/seguridad

    eleccion_id: int = Field(primary_key=True, foreign_key="eleccion.id", ondelete="CASCADE")
    created_by_id: int = Field(default=None, foreign_key="users.id")

    lista : Optional["Lista"] = Relationship()#back_populates="votos"
    eleccion: Optional["Eleccion"] = Relationship(back_populates="votos")
    creation_user: User = Relationship()


class EleccionBase(SQLModel):
    nombre: str
    descripcion: str
    fecha: str # TODO: date year/month/day format
    escanos: int

class Eleccion(EleccionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    listas: List["Lista"] = Relationship( link_model=ListaEleccion,  back_populates="elecciones")#, cascade_delete=True
    votos : List["VotoListaEleccion"] = Relationship(back_populates="eleccion",  cascade_delete=True)

    calculos: List["Calculo"] = Relationship(back_populates="eleccion",  cascade_delete=True)
class EleccionCreate(EleccionBase):
    pass


class EscanosPorLista(SQLModel):
    lista_id : int = Field(foreign_key="lista.id", primary_key=True)
    votos : int
    escanos : int

class EscanosPorListaDB(EscanosPorLista,table=True):
    calculo_id : int = Field(foreign_key="calculo.id", primary_key=True)
    # calculo : Optional["Calculo"] = Relationship(back_populates="escanos")

class CalculoBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    eleccion_id: Optional[int] = Field(default=None, foreign_key="eleccion.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: int = Field(default=None, foreign_key="users.id")

class Calculo(CalculoBase, table=True):
    eleccion: Eleccion= Relationship(back_populates="calculos")
    reparticion_escanos : List[EscanosPorListaDB] = Relationship(  cascade_delete=True)#back_populates="calculo",
    creation_user: User = Relationship()

class CalculoWithEscanos(CalculoBase):
    eleccion: Eleccion
    creation_user: UserPublic
    reparticion_escanos : list[EscanosPorLista] = []
