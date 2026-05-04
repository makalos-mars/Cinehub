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
    "dbname": "cinemx_prototipo", #aqui ponen el nombre su base de datos, el que crearon en postgres 
    "user": "postgres",           
    "password": "byemike24", # su contraseña locos
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Recibe la consulta Sql, la ejecuta y devuelve la tabla
@app.post("/api/consulta-libre")
def ejecutar_consulta_libre(consulta: ConsultaSQL):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(consulta.query)
        if cursor.description:
            resultados = cursor.fetchall()
            if not resultados:
                return [{"Mensaje": "La consulta se ejecutó, pero no se encontraron registros."}]
        else:
            conn.commit()
            resultados = [{"Mensaje": "Consulta ejecutada con éxito (Sin datos para mostrar)"}]
            
        cursor.close()
        conn.close()
        return resultados
        
    except Exception as e:
        return [{"error_sql": str(e)}]
