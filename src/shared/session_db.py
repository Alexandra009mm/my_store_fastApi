from sqlmodel import Session , create_engine
import os
from dotenv import load_dotenv
from typing import Annotated

from fastapi import Depends
 
load_dotenv()  # Carga las variables de entorno desde el archivo .env

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("Falta DATABASE_URL en el archivo .env")

engine = create_engine(database_url)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]