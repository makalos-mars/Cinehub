from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

class ConsultaSQL(BaseModel):
    query: str

app = FastAPI(title="CineHub API")

#conexion entre el backend y el frontend, para que puedan comunicarse sin problemas de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": "", #aqui ponen el nombre su base de datos, el que crearon en postgres 
    "user": "postgres",           
    "password": "", # su contraseña locos
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
