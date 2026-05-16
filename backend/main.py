from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI(title="CineHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": "cinemx_proyectofinal",
    "user": "postgres",
    "password": "byemike24",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Relación rol → tabla y columna PK de correo
TABLA_CONFIG = {
    "aficionado": {"tabla": "aficionado", "pk": "correo_aficionado"},
    "critico":    {"tabla": "critico",    "pk": "correo_critico"},
    "reportero":  {"tabla": "reportero",  "pk": "correo_reportero"},
    "director":   {"tabla": "director",   "pk": "correo"},
}

# ── Modelos ──────────────────────────────────────────────────────────

class ConsultaSQL(BaseModel):
    query: str

class LoginData(BaseModel):
    correo: str
    contrasena: str

class RegistroData(BaseModel):
    nombre: str
    apellido: str
    correo: str
    contrasena: str
    rol: str

# ── Reportes predefinidos ─────────────────────────────────────────────

REPORTES = {
    "1": """
        SELECT genero, COUNT(*) AS total_peliculas
        FROM pelicula
        GROUP BY genero
        ORDER BY total_peliculas DESC
    """,
    "2": """
        SELECT p.titulo, p.genero, d.nombre AS director,
               c.nombre_cine, c.ubicacion,
               TO_CHAR(ca.horario_de_emision, 'DD/MM/YYYY HH24:MI') AS horario
        FROM pelicula p
        JOIN cartelera ca   ON p.id_pelicula    = ca.id_pelicula
        JOIN cine c         ON ca.no_sucursal    = c.no_sucursal
        JOIN produccion pr  ON p.id_produccion   = pr.id_produccion
        JOIN director d     ON pr.correo_director = d.correo
        ORDER BY ca.horario_de_emision
    """,
    "3": """
        SELECT c.nombre_cine, c.ubicacion,
               COUNT(DISTINCT ca.id_pelicula) AS peliculas_distintas,
               COUNT(ca.id_pelicula)          AS total_funciones
        FROM cine c
        LEFT JOIN cartelera ca ON c.no_sucursal = ca.no_sucursal
        GROUP BY c.no_sucursal, c.nombre_cine, c.ubicacion
        ORDER BY total_funciones DESC
    """
}

def _ejecutar(query: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados if resultados else [{"Mensaje": "No se encontraron registros."}]

# ── Endpoints de reportes ─────────────────────────────────────────────

@app.get("/api/reportes/{reporte_id}")
def obtener_reporte(reporte_id: str):
    query = REPORTES.get(reporte_id)
    if not query:
        return [{"error": "Reporte no encontrado"}]
    try:
        return _ejecutar(query)
    except Exception as e:
        return [{"error_sql": str(e)}]

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

# ── Endpoints de autenticación ────────────────────────────────────────

@app.get("/api/auth/verificar-correo/{correo}")
def verificar_correo(correo: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT correo FROM credenciales WHERE correo = %s", (correo.lower(),))
        existe = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return {"existe": existe}
    except Exception as e:
        return {"existe": False, "error": str(e)}

@app.post("/api/auth/login")
def login(data: LoginData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT correo, rol FROM credenciales WHERE correo = %s AND contrasena = %s",
            (data.correo.lower(), data.contrasena)
        )
        cred = cursor.fetchone()
        if not cred:
            cursor.close()
            conn.close()
            return {"ok": False, "mensaje": "Correo o contraseña incorrectos."}

        rol = cred["rol"]
        cfg = TABLA_CONFIG[rol]
        cursor.execute(
            f"SELECT nombre FROM {cfg['tabla']} WHERE {cfg['pk']} = %s",
            (data.correo.lower(),)
        )
        perfil = cursor.fetchone()
        cursor.close()
        conn.close()

        nombre = perfil["nombre"] if perfil else data.correo
        return {"ok": True, "correo": data.correo.lower(), "rol": rol, "nombre": nombre}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}

@app.post("/api/auth/registro")
def registro(data: RegistroData):
    if data.rol not in TABLA_CONFIG:
        return {"ok": False, "mensaje": "Rol no válido."}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT correo FROM credenciales WHERE correo = %s", (data.correo.lower(),))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"ok": False, "mensaje": "Este correo ya está registrado."}

        cfg = TABLA_CONFIG[data.rol]
        nombre_completo = f"{data.nombre} {data.apellido}"

        cursor.execute(
            f"INSERT INTO {cfg['tabla']} ({cfg['pk']}, nombre) VALUES (%s, %s)",
            (data.correo.lower(), nombre_completo)
        )
        cursor.execute(
            "INSERT INTO credenciales (correo, contrasena, rol) VALUES (%s, %s, %s)",
            (data.correo.lower(), data.contrasena, data.rol)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"ok": True, "correo": data.correo.lower(), "rol": data.rol, "nombre": nombre_completo}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}
