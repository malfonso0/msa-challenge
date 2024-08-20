from fastapi import FastAPI
import os
import logging
from database import initialize_db, engine,DB_URL

db_path = DB_URL.replace("sqlite:///", "")
if not os.path.exists(db_path):
    initialize_db(engine, recreate=True)

from routes import (
    eleccion_router,
    user_router,
    lista_router,
    security_router)

app = FastAPI()
app.include_router(eleccion_router)
app.include_router(user_router)
app.include_router(lista_router)
app.include_router(security_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
