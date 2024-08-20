from sqlmodel import SQLModel, Session, create_engine, select
import os
import logging

from calculo import calcular_votos_por_lista,calculo_escanos
from model import *


DB_URL="sqlite:///mi_base_de_datos.db"
DB_URL = os.getenv("DB_URL")
# Used for debugging
ECHO = os.getenv("ECHO", "False").lower() == "true"

logging.info("creating engine")
engine = create_engine(DB_URL, connect_args={'check_same_thread': False}, echo=ECHO)

#from common.database import initialize_db
def create_db_and_tables(engine, recreate=False):
    if recreate:
        logging.warning("dropping tables")
        SQLModel.metadata.drop_all(engine)
    logging.warning("creating tables")
    SQLModel.metadata.create_all(engine)

def initialize_db(engine,recreate=True):
    logging.warning("Initializing DB")
    create_db_and_tables(engine, recreate=recreate)
    if not recreate:
        return
    ## Add roles
    with Session(engine) as db:
        roles = [
            Role(id=1, nombre="Admin"),
            Role(id=2, nombre="Reader"),
            Role(id=3, nombre="Writer"),
            Role(id=4, nombre="Uploader"),
        ]
        db.add_all(roles)
        db.commit()
        # should refresh here ??
        
        default_users = [
            User(id=1, nombre="admin",
                        email="admin@localhost.com", hashed_password=hash_password("admin"), roles=[roles[0]]),
            User(id=2, nombre="reader",
                        email="reader@localhost.com", hashed_password=hash_password("reader"), roles=[roles[1]]),
            User(id=3, nombre="test",
                        email="test@localhost.com", hashed_password=hash_password("#test1234"), roles=roles[1:]),
        ]
        db.add_all(default_users)
        db.commit()

def get_db():
    # db = scoped_session(sessionmaker(bind=engine))
    # db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with Session(engine) as session:
        yield session


def test_one():
    DB_URL="sqlite:///test_one.db"
    # DB_URL = os.getenv("DB_URL")
    # Used for debugging
    ECHO = os.getenv("ECHO", "False").lower() == "true"
    engine = create_engine(DB_URL, connect_args={'check_same_thread': False}, echo=ECHO)

    initialize_db(engine)
    import random
    import itertools as itools

    def create_uploaders_users(session, n=3):
        statement = select(Role).where(Role.nombre == "Uploader")
        uploader_role = session.exec(statement).first()
        uploaders = [User(nombre=f"Uploader {idx}",
                                email=f"uploader{idx}@localhost",
                                hashed_password=hash_password(f"uploader{idx}"),
                                roles=[uploader_role])
                        for idx in range(1,n+1)]
        session.add_all(uploaders)
        session.commit()
        return uploaders

    def create_elections(session, n=3):
        elections = [Eleccion(id=idx, escanos=random.randint(5,50),
                                    nombre=f"Eleccion {idx}",
                                    descripcion=f"Descripcion {idx}",
                                    fecha=f"2022-01-{idx:02d}")
                        for idx in range(1,n+1)]


        session.add_all(elections)
        session.commit()
        return elections

    def create_lists(session, n=5):
        listas = [Lista(id=idx, nombre=f"Lista {idx}", descripcion=f"Lista {idx}") for idx in range(1,n+1)]
        session.add_all(listas)
        session.commit()
        return listas

    def assignar_listas_a_eleccion(session, elecciones, listas):

        for eleccion in elecciones:

            listas_eleccion = random.sample(listas, k=3)
            eleccion.listas.extend(listas_eleccion)
            session.add(eleccion)
            session.commit()

    def agregar_votos_random(session, elecciones,uploaders):

        for eleccion in elecciones:
            votos_listas = [VotoListaEleccion(
                                    lista_id=lista.id,
                                    eleccion_id=eleccion.id,
                                    created_by_id= random.choice(uploaders).id,
                                    votos=random.randint(500, 2000))
                                for lista in eleccion.listas]
            session.add_all(votos_listas)
            session.commit()
            # Add twice
            votos_listas = [VotoListaEleccion(
                                    lista_id=lista.id,
                                    eleccion_id=eleccion.id,
                                    created_by_id= random.choice(uploaders).id,
                                    votos=random.randint(500, 2000))
                                for lista in eleccion.listas]
            session.add_all(votos_listas)
            session.commit()

    with Session(engine) as session:
            uploaders = create_uploaders_users(session)
            elecciones = create_elections(session)
            listas = create_lists(session)
            assignar_listas_a_eleccion(session, elecciones, listas)
            agregar_votos_random(session, elecciones,uploaders)
            for eleccion in elecciones:
                votos = calcular_votos_por_lista(eleccion)
                votos = calculo_escanos(votos, eleccion.escanos)
                
                # Guardar en algun lado!


if __name__ == "__main__":
    initialize_db(engine, False)
    # test_one()