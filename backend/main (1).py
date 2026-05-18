from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="CineHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": "cinemx",
    "user": "postgres",
    "password": "diego1415",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

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

class PeliculaData(BaseModel):
    titulo: str
    genero: str
    tipo: str          # 'pelicula' | 'documental' | 'serie'
    anio: Optional[int] = None
    duracion: Optional[int] = None   # minutos
    sinopsis: Optional[str] = None
    imagen_url: Optional[str] = None
    id_produccion: Optional[int] = None

class PeliculaUpdate(BaseModel):
    titulo: Optional[str] = None
    genero: Optional[str] = None
    tipo: Optional[str] = None
    anio: Optional[int] = None
    duracion: Optional[int] = None
    sinopsis: Optional[str] = None
    imagen_url: Optional[str] = None
    id_produccion: Optional[int] = None

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

# ══════════════════════════════════════════════════════════════════════
# ── CRUD DE CATÁLOGO (Películas / Documentales / Series) ──────────────
# ══════════════════════════════════════════════════════════════════════

# ── Listar por tipo (o todos) ─────────────────────────────────────────

@app.get("/api/catalogo")
def listar_catalogo(tipo: str = None, q: str = None):
    """
    Lista todo el catálogo.
    ?tipo=pelicula|documental|serie  filtra por tipo
    ?q=texto                         búsqueda por título
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        conditions = []
        params = []

        if tipo:
            conditions.append("p.tipo = %s")
            params.append(tipo)
        if q:
            conditions.append("p.titulo ILIKE %s")
            params.append(f"%{q}%")

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        cursor.execute(f"""
            SELECT
                p.id_pelicula,
                p.titulo,
                p.genero,
                p.tipo,
                p.anio,
                p.duracion,
                p.sinopsis,
                p.imagen_url,
                p.id_produccion,
                d.nombre AS director
            FROM pelicula p
            LEFT JOIN produccion pr ON p.id_produccion = pr.id_produccion
            LEFT JOIN director d    ON pr.correo_director = d.correo
            {where}
            ORDER BY p.titulo
        """, params)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows if rows else []
    except Exception as e:
        return {"error": str(e)}


# ── Obtener uno ───────────────────────────────────────────────────────

@app.get("/api/catalogo/{id_pelicula}")
def obtener_pelicula(id_pelicula: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT p.*, d.nombre AS director
            FROM pelicula p
            LEFT JOIN produccion pr ON p.id_produccion = pr.id_produccion
            LEFT JOIN director d    ON pr.correo_director = d.correo
            WHERE p.id_pelicula = %s
        """, (id_pelicula,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return {"error": "No encontrado"}
        return row
    except Exception as e:
        return {"error": str(e)}


# ── Alta ──────────────────────────────────────────────────────────────

@app.post("/api/catalogo")
def crear_pelicula(data: PeliculaData):
    """
    Inserta una nueva entrada en la tabla pelicula.
    El campo 'tipo' debe ser: 'pelicula', 'documental' o 'serie'.
    """
    if data.tipo not in ("pelicula", "documental", "serie"):
        return {"ok": False, "mensaje": "Tipo inválido. Usa: pelicula, documental o serie."}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO pelicula
                (titulo, genero, tipo, anio, duracion, sinopsis, imagen_url, id_produccion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_pelicula
        """, (
            data.titulo, data.genero, data.tipo,
            data.anio, data.duracion, data.sinopsis,
            data.imagen_url, data.id_produccion
        ))
        new_id = cursor.fetchone()["id_pelicula"]
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "id_pelicula": new_id, "mensaje": f"'{data.titulo}' agregado correctamente."}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}


# ── Modificación ──────────────────────────────────────────────────────

@app.put("/api/catalogo/{id_pelicula}")
def actualizar_pelicula(id_pelicula: int, data: PeliculaUpdate):
    try:
        fields = {k: v for k, v in data.dict().items() if v is not None}
        if not fields:
            return {"ok": False, "mensaje": "No hay campos para actualizar."}

        set_clause = ", ".join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [id_pelicula]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE pelicula SET {set_clause} WHERE id_pelicula = %s",
            values
        )
        updated = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if updated == 0:
            return {"ok": False, "mensaje": "No se encontró el registro."}
        return {"ok": True, "mensaje": "Actualizado correctamente."}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}


# ── Baja ──────────────────────────────────────────────────────────────

@app.delete("/api/catalogo/{id_pelicula}")
def eliminar_pelicula(id_pelicula: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Guardar título antes de borrar
        cursor.execute("SELECT titulo FROM pelicula WHERE id_pelicula = %s", (id_pelicula,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return {"ok": False, "mensaje": "Registro no encontrado."}

        titulo = row["titulo"]

        # Eliminar dependencias primero (cartelera)
        cursor.execute("DELETE FROM cartelera WHERE id_pelicula = %s", (id_pelicula,))
        cursor.execute("DELETE FROM pelicula  WHERE id_pelicula = %s", (id_pelicula,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": f"'{titulo}' eliminado correctamente."}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}


# ── Listar directores (para formularios) ─────────────────────────────

@app.get("/api/directores")
def listar_directores():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT correo, nombre FROM director ORDER BY nombre")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        return {"error": str(e)}


# ── Listar producciones (para formularios) ────────────────────────────

@app.get("/api/producciones")
def listar_producciones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT pr.id_produccion, pr.correo_director, d.nombre AS director
            FROM produccion pr
            JOIN director d ON pr.correo_director = d.correo
            ORDER BY d.nombre
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        return {"error": str(e)}
