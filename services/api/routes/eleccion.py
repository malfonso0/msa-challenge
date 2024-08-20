from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import List,Annotated

from model import (
    Eleccion,EleccionCreate,
    Lista,
    ListaEleccionCreate,
    ListaEleccion,
    VotoEleccionCreate,VotoListaEleccion,
    EscanosPorLista, EscanosPorListaDB, Calculo,CalculoWithEscanos
)
from routes.security import (
    get_db,
    writer_user_dependency,
    uploader_user_dependency,
    get_current_user,
    db_dependency
)
from calculo import calcular_votos_por_lista,calculo_escanos

# db_dependency= Annotated[Session, Depends(get_db)]

eleccion_router = APIRouter(tags=["elecciones"], dependencies= [Depends(get_current_user)] )

# Ruta para crear una nueva elección
@eleccion_router.post("/elecciones/", response_model=Eleccion, dependencies= [writer_user_dependency] )
def crear_eleccion(eleccion: EleccionCreate, session: db_dependency):
    db_eleccion = Eleccion.model_validate(eleccion)
    session.add(db_eleccion)
    session.commit()
    session.refresh(db_eleccion)
    return db_eleccion

# Ruta para obtener todas las elecciones
@eleccion_router.get("/elecciones/", response_model=List[Eleccion])
def obtener_elecciones(session: Annotated[Session, Depends(get_db)]):
    elecciones =  session.exec(select(Eleccion)).all()
    return elecciones

# Ruta para obtener una elección por ID
@eleccion_router.get("/elecciones/{eleccion_id}", response_model=Eleccion)
def obtener_eleccion(eleccion_id: int, session: Annotated[Session, Depends(get_db)]):
    eleccion = session.get(Eleccion, eleccion_id)
    if not eleccion:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    return eleccion

# Ruta para eliminar una elección
@eleccion_router.delete("/elecciones/{eleccion_id}",dependencies= [writer_user_dependency] )
def eliminar_eleccion(eleccion_id: int, session: Annotated[Session, Depends(get_db)] ):
    eleccion = session.query(Eleccion).get(eleccion_id)
    if not eleccion:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    session.delete(eleccion)
    session.commit()
    return {"mensaje": "Elección eliminada con éxito"}

# *******************************************************************************
######################### ELECCION LISTAS ######################################
# *******************************************************************************
@eleccion_router.post("/elecciones/{eleccion_id}/listas",tags=["elecciones-lista"],
                        response_model=ListaEleccion, dependencies= [writer_user_dependency] )
def crear_listaeleccion(eleccion_id:int, lista:ListaEleccionCreate, session: Annotated[Session, Depends(get_db)]):
    
    eleccion = session.get(Eleccion, eleccion_id)
    if eleccion is None:
        raise HTTPException(status_code=404, detail="Eleccion no encontrada")
    db_lista = session.get(Lista, lista.lista_id)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    
    if db_lista in eleccion.listas:
        raise HTTPException(status_code=400, detail="Lista ya existe en la elección")

    db_listae = ListaEleccion(
        eleccion_id=eleccion_id,
        lista_id=lista.lista_id
    )
    try:
        session.add(db_listae)
        session.commit()
        session.refresh(db_listae)
        return db_listae
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@eleccion_router.get("/elecciones/{eleccion_id}/listas",tags=["elecciones-lista"], response_model=List[Lista])
def get_listas_eleccion(eleccion_id:int , session: Annotated[Session, Depends(get_db)]):

    eleccion = session.get(Eleccion, eleccion_id)
    if eleccion is None:
        raise HTTPException(status_code=404, detail="Elección no encontrada")

    return eleccion.listas


### ACa tendria que decidir si utilizar lista_id o listaeleccion.id
# me da mas natural el lista_id .. pero bueno
@eleccion_router.delete("/elecciones/{eleccion_id}/listas/{lista_id}",tags=["elecciones-lista"]
                            ,dependencies= [writer_user_dependency] )
def delete_listaeleccion(eleccion_id:int, lista_id:int, session: Annotated[Session, Depends(get_db)]):

    db_listae = session.get(ListaEleccion, (lista_id, eleccion_id))
    if db_listae is None:
        raise HTTPException(status_code=404, detail="Lista de eleccion no encontrada")
    try:
        session.delete(db_listae)
        session.commit()
        return {"message": "Lista eliminada de la elección"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# *******************************************************************************
######################### ELECCION Votos ######################################
# *******************************************************************************
@eleccion_router.post("/elecciones/{eleccion_id}/votos",tags=["elecciones-votos"], 
                    response_model=VotoListaEleccion, dependencies= [uploader_user_dependency] )
def crear_voto(eleccion_id:int,
                voto:VotoEleccionCreate,
                session: Annotated[Session, Depends(get_db)],
                current_user = Depends(get_current_user),
                ):

    eleccion = session.get(Eleccion, eleccion_id)
    if eleccion is None:
        raise HTTPException(status_code=404, detail="Eleccion no encontrada")
    db_lista = session.get(Lista, voto.lista_id)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    if db_lista not in eleccion.listas:
        raise HTTPException(status_code=400, detail="La lista no pertenece a la elección")

    db_voto = session.get(VotoListaEleccion, (voto.mesa, voto.lista_id, eleccion_id))
    if db_voto is not None:
        raise HTTPException(status_code=400, detail="Voto ya existente")

    db_voto = VotoListaEleccion(
        votos = voto.votos,
        mesa=voto.mesa,
        eleccion_id=eleccion_id,
        lista_id=voto.lista_id,
        created_by_id=current_user.id
    )
    try:
        session.add(db_voto)
        session.commit()
        session.refresh(db_voto)
        return db_voto
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@eleccion_router.get("/elecciones/{eleccion_id}/votos",tags=["elecciones-votos"], 
                        response_model=List[VotoListaEleccion])
def get_votos_eleccion(eleccion_id:int , session: Annotated[Session, Depends(get_db)]):

    eleccion = session.get(Eleccion, eleccion_id)
    if eleccion is None:
        raise HTTPException(status_code=404, detail="Elección no encontrada")

    return eleccion.votos

@eleccion_router.get("/elecciones/{eleccion_id}/votos/{lista_id}/{mesa}",tags=["elecciones-votos"], 
                        response_model=VotoListaEleccion)
def get_votos_eleccion(eleccion_id:int, lista_id:int, mesa:int,
                        session: Annotated[Session, Depends(get_db)]):

    vle = session.get(VotoListaEleccion, (mesa, lista_id, eleccion_id))
    if vle is None:
        raise HTTPException(status_code=404, detail="Voto no encontrado")

    return vle


@eleccion_router.get("/elecciones/{eleccion_id}/calcular_escanos",tags=["elecciones-calculos"], 
                        response_model=CalculoWithEscanos
                        )
def calcular_escanos(eleccion_id:int,
                            session: Annotated[Session, Depends(get_db)],
                            current_user = Depends(get_current_user),
):

    eleccion = session.get(Eleccion, eleccion_id)
    if eleccion is None:
        raise HTTPException(status_code=404, detail="Elección no encontrada")

    votos = calcular_votos_por_lista(eleccion)
    votos = calculo_escanos(votos, eleccion.escanos)
    [voto.pop("lista") for voto in votos]
    ## Guardar aca antes de devolver, y agregar un uuid or algo para poder obtenerlo
    
    calculo = Calculo(
        eleccion_id=eleccion_id,
        created_by_id=current_user.id)
    
    for voto in votos:
        calculo.escanos.append(EscanosPorLista(**voto))
    try:
        session.add(calculo)
        session.commit()
        session.refresh(calculo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return calculo

@eleccion_router.get("/elecciones/{eleccion_id}/calculos",
                    response_model=List[CalculoWithEscanos],
                    tags=["elecciones-calculos"])
def get_calculos(eleccion_id:int,session: Annotated[Session, Depends(get_db)]):

    eleccion = session.get(Eleccion, eleccion_id)
    if eleccion is None:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    #TODO: hacerlo.. aqui

    return eleccion.calculos

@eleccion_router.get("/elecciones/{eleccion_id}/calculos/{calculo_id}",
                        tags=["elecciones-calculos"],response_model=CalculoWithEscanos
)
def get_calculo(eleccion_id:int,calculo_id:int,session: Annotated[Session, Depends(get_db)]):
    calculo = session.get(Calculo, calculo_id)
    if calculo is None:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    #TODO: hacerlo.. aqui

    return calculo