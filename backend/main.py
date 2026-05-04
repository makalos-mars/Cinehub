from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="CineHub API")

# ⚠️ ¡IMPORTANTE! Cambia estos datos por los de tu PostgreSQL local
DB_CONFIG = {
    "dbname": "cinemx_prototipo", # Pon el nombre que le diste a tu BD en pgAdmin/psql
    "user": "postgres",                     # Usualmente es postgres
    "password": "",       # La contraseña que usas para entrar a psql
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    # Esta función crea el "puente" hacia tu base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Ruta de prueba para ver si el servidor está vivo
@app.get("/")
def read_root():
    return {"mensaje": "¡El servidor de CineHub está corriendo perfectamente!"}

# Ruta para pedirle las películas a PostgreSQL
@app.get("/api/peliculas")
def obtener_peliculas():
    try:
        # 1. Abrimos la conexión
        conn = get_db_connection()
        # Usamos RealDictCursor para que los datos salgan en formato JSON automáticamente
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 2. Ejecutamos la consulta a tu tabla
        cursor.execute("SELECT id_pelicula, titulo, genero, formato FROM pelicula;")
        peliculas = cursor.fetchall()
        
        # 3. Cerramos la puerta
        cursor.close()
        conn.close()
        
        # 4. Devolvemos los datos
        return peliculas
        
    except Exception as e:
        return {"error": f"Hubo un problema con la base de datos: {str(e)}"}