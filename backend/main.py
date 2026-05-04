from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

class ConsultaSQL(BaseModel):
    query: str

app = FastAPI(title="CineHub API")

# IMPORTANTE: Esto permite que tu HTML (Live Server) se comunique con FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": "cinemx_prototipo", 
    "user": "postgres",           
    "password": "byemike24", # Pon tu contraseña real
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# REPORTE 1: Películas y Directores
@app.get("/api/reportes/1")
def reporte_peliculas_directores():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # Hacemos un JOIN entre pelicula y director
    cursor.execute("""
        SELECT p.titulo, p.genero, p.formato, d.nombre AS director 
        FROM pelicula p
        JOIN director d ON p.correo_director = d.correo;
    """)
    resultados = cursor.fetchall()
    cursor.close(); conn.close()
    return resultados

# REPORTE 2: Opiniones de Críticos
@app.get("/api/reportes/2")
def reporte_opiniones_criticos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT p.titulo, c.nombre AS critico, o.calificacion, o.comentario 
        FROM pelicula p
        JOIN opinion o ON p.id_opinion = o.id
        JOIN critico c ON o.correo_critico = c.correo_critico;
    """)
    resultados = cursor.fetchall()
    cursor.close(); conn.close()
    return resultados

# REPORTE 3: Cartelera por Sucursal
@app.get("/api/reportes/3")
def reporte_cartelera():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT c.nombre_cine, c.ubicacion, p.titulo, ca.horario_de_emision 
        FROM cartelera ca
        JOIN cine c ON ca.no_sucursal = c.no_sucursal
        JOIN pelicula p ON ca.id_pelicula = p.id_pelicula;
    """)
    resultados = cursor.fetchall()
    cursor.close(); conn.close()
    return resultados

# REPORTE 4: Reparto de Producciones
@app.get("/api/reportes/4")
def reporte_reparto():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT pr.tipo, p.titulo, r.actor, r.extra, r.doble 
        FROM produccion pr
        JOIN pelicula p ON pr.id_produccion = p.id_produccion
        JOIN reparto r ON pr.id_produccion = r.id_produccion;
    """)
    resultados = cursor.fetchall()
    cursor.close(); conn.close()
    return resultados

# REPORTE 5: Consulta Libre en Vivo
@app.post("/api/consulta-libre")
def ejecutar_consulta_libre(consulta: ConsultaSQL):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Ejecutamos exactamente lo que escribas en la página web
        cursor.execute(consulta.query)
        resultados = cursor.fetchall()
        cursor.close(); conn.close()
        return resultados
    except Exception as e:
        cursor.close(); conn.close()
        # Si la consulta tiene un error de sintaxis, se lo mandamos a la página
        return [{"error_sql": f"Error en tu consulta: {str(e)}"}]