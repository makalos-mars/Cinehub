from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional
import traceback

app = FastAPI(title="CineHub API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Configuración de base de datos ────────────────────────────────────
DB_CONFIG = {
    "dbname": "cinemx_prototipo",
    "user": "postgres",
    "password": "byemike24",
    "host": "localhost",
    "port": "5432"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

# Relación rol → tabla y columna PK de correo
TABLA_CONFIG = {
    "aficionado": {"tabla": "aficionado", "pk": "correo_aficionado"},
    "critico":    {"tabla": "critico",    "pk": "correo_critico"},
    "reportero":  {"tabla": "reportero",  "pk": "correo_reportero"},
    "director":   {"tabla": "director",   "pk": "correo"},
}

# ── Modelos ───────────────────────────────────────────────────────────

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
    anio: Optional[int] = None
    duracion_min: Optional[int] = None
    sinopsis: Optional[str] = None
    id_produccion: Optional[int] = None

class SerieData(BaseModel):
    titulo: str
    genero: str
    anio: Optional[int] = None
    temporadas: Optional[int] = None
    sinopsis: Optional[str] = None
    id_produccion: Optional[int] = None

class DocumentalData(BaseModel):
    titulo: str
    tema: str
    anio: Optional[int] = None
    duracion_min: Optional[int] = None
    sinopsis: Optional[str] = None
    id_produccion: Optional[int] = None

class ConsultaSQL(BaseModel):
    query: str

# ── Helpers ───────────────────────────────────────────────────────────

def run_query(sql: str, params=None, fetch=True):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        if fetch:
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        else:
            conn.commit()
            return {"affected": cur.rowcount}
    finally:
        cur.close()
        conn.close()

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

# ═══════════════════════════════════════════════════════════════════════
#  ENDPOINTS DE REPORTES
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/reportes/{reporte_id}")
def obtener_reporte(reporte_id: str):
    query = REPORTES.get(reporte_id)
    if not query:
        return [{"error": "Reporte no encontrado"}]
    try:
        rows = run_query(query)
        return rows if rows else [{"Mensaje": "No se encontraron registros."}]
    except Exception as e:
        return [{"error_sql": str(e)}]

@app.post("/api/consulta-libre")
def ejecutar_consulta_libre(consulta: ConsultaSQL):
    try:
        rows = run_query(consulta.query)
        return rows if rows else [{"Mensaje": "Consulta ejecutada. Sin registros."}]
    except Exception as e:
        return [{"error_sql": str(e)}]

# ═══════════════════════════════════════════════════════════════════════
#  AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/auth/verificar-correo/{correo}")
def verificar_correo(correo: str):
    try:
        rows = run_query(
            "SELECT correo FROM credenciales WHERE correo = %s",
            (correo.lower(),)
        )
        return {"existe": len(rows) > 0}
    except Exception as e:
        return {"existe": False, "error": str(e)}

@app.post("/api/auth/login")
def login(data: LoginData):
    try:
        rows = run_query(
            "SELECT correo, rol FROM credenciales WHERE correo = %s AND contrasena = %s",
            (data.correo.lower(), data.contrasena)
        )
        if not rows:
            return {"ok": False, "mensaje": "Correo o contraseña incorrectos."}
        cred = rows[0]
        rol = cred["rol"]
        cfg = TABLA_CONFIG.get(rol)
        if not cfg:
            return {"ok": False, "mensaje": f"Rol desconocido: {rol}"}
        perfil_rows = run_query(
            f"SELECT nombre FROM {cfg['tabla']} WHERE {cfg['pk']} = %s",
            (data.correo.lower(),)
        )
        nombre = perfil_rows[0]["nombre"] if perfil_rows else data.correo
        return {"ok": True, "correo": data.correo.lower(), "rol": rol, "nombre": nombre}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}

@app.post("/api/auth/registro")
def registro(data: RegistroData):
    if data.rol not in TABLA_CONFIG:
        return {"ok": False, "mensaje": "Rol no válido."}
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT correo FROM credenciales WHERE correo = %s", (data.correo.lower(),))
        if cur.fetchone():
            return {"ok": False, "mensaje": "Este correo ya está registrado."}
        cfg = TABLA_CONFIG[data.rol]
        nombre_completo = f"{data.nombre} {data.apellido}"
        cur.execute(
            f"INSERT INTO {cfg['tabla']} ({cfg['pk']}, nombre) VALUES (%s, %s)",
            (data.correo.lower(), nombre_completo)
        )
        cur.execute(
            "INSERT INTO credenciales (correo, contrasena, rol) VALUES (%s, %s, %s)",
            (data.correo.lower(), data.contrasena, data.rol)
        )
        conn.commit()
        return {"ok": True, "correo": data.correo.lower(), "rol": data.rol, "nombre": nombre_completo}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensaje": str(e)}
    finally:
        cur.close()
        conn.close()

@app.get("/api/auth/usuario/{correo}")
def obtener_usuario(correo: str):
    try:
        rows = run_query("SELECT correo, rol FROM credenciales WHERE correo = %s", (correo.lower(),))
        if not rows:
            return {"ok": False, "mensaje": "Usuario no encontrado."}
        rol = rows[0]["rol"]
        cfg = TABLA_CONFIG[rol]
        perfil = run_query(
            f"SELECT * FROM {cfg['tabla']} WHERE {cfg['pk']} = %s",
            (correo.lower(),)
        )
        if not perfil:
            return {"ok": False, "mensaje": "Perfil no encontrado."}
        return {"ok": True, "rol": rol, "perfil": perfil[0]}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}

@app.delete("/api/auth/usuario/{correo}")
def eliminar_usuario(correo: str):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT rol FROM credenciales WHERE correo = %s", (correo.lower(),))
        cred = cur.fetchone()
        if not cred:
            return {"ok": False, "mensaje": "Usuario no encontrado."}
        rol = cred["rol"]
        cfg = TABLA_CONFIG[rol]
        cur.execute("DELETE FROM credenciales WHERE correo = %s", (correo.lower(),))
        cur.execute(f"DELETE FROM {cfg['tabla']} WHERE {cfg['pk']} = %s", (correo.lower(),))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensaje": "No se puede eliminar: tiene datos asociados en el sistema."}
    finally:
        cur.close()
        conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  ABC — PELÍCULAS
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/peliculas")
def listar_peliculas():
    try:
        rows = run_query("""
            SELECT p.id_pelicula, p.titulo, p.genero, p.anio,
                   p.duracion_min, p.sinopsis,
                   COALESCE(d.nombre, '—') AS director
            FROM pelicula p
            LEFT JOIN produccion pr ON p.id_produccion = pr.id_produccion
            LEFT JOIN director d    ON pr.correo_director = d.correo
            ORDER BY p.titulo
        """)
        return rows
    except Exception as e:
        # Si las columnas no existen aún, devuelve lo básico
        try:
            rows = run_query("SELECT * FROM pelicula ORDER BY titulo")
            return rows
        except Exception as e2:
            return [{"error": str(e2)}]

@app.get("/api/peliculas/{id_pelicula}")
def obtener_pelicula(id_pelicula: int):
    try:
        rows = run_query("SELECT * FROM pelicula WHERE id_pelicula = %s", (id_pelicula,))
        if not rows:
            return {"error": "No encontrada"}
        return rows[0]
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/peliculas")
def crear_pelicula(data: PeliculaData):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO pelicula (titulo, genero, anio, duracion_min, sinopsis, id_produccion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (data.titulo, data.genero, data.anio, data.duracion_min, data.sinopsis, data.id_produccion))
        nuevo = dict(cur.fetchone())
        conn.commit()
        return {"ok": True, "pelicula": nuevo}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        cur.close(); conn.close()

@app.put("/api/peliculas/{id_pelicula}")
def actualizar_pelicula(id_pelicula: int, data: PeliculaData):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            UPDATE pelicula
            SET titulo=%s, genero=%s, anio=%s, duracion_min=%s, sinopsis=%s, id_produccion=%s
            WHERE id_pelicula=%s
            RETURNING *
        """, (data.titulo, data.genero, data.anio, data.duracion_min, data.sinopsis, data.id_produccion, id_pelicula))
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            return {"ok": False, "error": "Película no encontrada"}
        return {"ok": True, "pelicula": dict(updated)}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        cur.close(); conn.close()

@app.delete("/api/peliculas/{id_pelicula}")
def eliminar_pelicula(id_pelicula: int):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pelicula WHERE id_pelicula = %s", (id_pelicula,))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": "No se puede eliminar: tiene datos relacionados."}
    finally:
        cur.close(); conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  ABC — SERIES
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/series")
def listar_series():
    try:
        rows = run_query("SELECT * FROM serie ORDER BY titulo")
        return rows
    except Exception as e:
        return [{"error": str(e)}]

@app.get("/api/series/{id_serie}")
def obtener_serie(id_serie: int):
    try:
        rows = run_query("SELECT * FROM serie WHERE id_serie = %s", (id_serie,))
        return rows[0] if rows else {"error": "No encontrada"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/series")
def crear_serie(data: SerieData):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO serie (titulo, genero, anio, temporadas, sinopsis, id_produccion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (data.titulo, data.genero, data.anio, data.temporadas, data.sinopsis, data.id_produccion))
        nuevo = dict(cur.fetchone())
        conn.commit()
        return {"ok": True, "serie": nuevo}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        cur.close(); conn.close()

@app.put("/api/series/{id_serie}")
def actualizar_serie(id_serie: int, data: SerieData):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            UPDATE serie
            SET titulo=%s, genero=%s, anio=%s, temporadas=%s, sinopsis=%s, id_produccion=%s
            WHERE id_serie=%s
            RETURNING *
        """, (data.titulo, data.genero, data.anio, data.temporadas, data.sinopsis, data.id_produccion, id_serie))
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            return {"ok": False, "error": "Serie no encontrada"}
        return {"ok": True, "serie": dict(updated)}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        cur.close(); conn.close()

@app.delete("/api/series/{id_serie}")
def eliminar_serie(id_serie: int):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM serie WHERE id_serie = %s", (id_serie,))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": "No se puede eliminar: tiene datos relacionados."}
    finally:
        cur.close(); conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  ABC — DOCUMENTALES
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/documentales")
def listar_documentales():
    try:
        rows = run_query("SELECT * FROM documental ORDER BY titulo")
        return rows
    except Exception as e:
        return [{"error": str(e)}]

@app.get("/api/documentales/{id_documental}")
def obtener_documental(id_documental: int):
    try:
        rows = run_query("SELECT * FROM documental WHERE id_documental = %s", (id_documental,))
        return rows[0] if rows else {"error": "No encontrado"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/documentales")
def crear_documental(data: DocumentalData):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO documental (titulo, tema, anio, duracion_min, sinopsis, id_produccion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (data.titulo, data.tema, data.anio, data.duracion_min, data.sinopsis, data.id_produccion))
        nuevo = dict(cur.fetchone())
        conn.commit()
        return {"ok": True, "documental": nuevo}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        cur.close(); conn.close()

@app.put("/api/documentales/{id_documental}")
def actualizar_documental(id_documental: int, data: DocumentalData):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            UPDATE documental
            SET titulo=%s, tema=%s, anio=%s, duracion_min=%s, sinopsis=%s, id_produccion=%s
            WHERE id_documental=%s
            RETURNING *
        """, (data.titulo, data.tema, data.anio, data.duracion_min, data.sinopsis, data.id_produccion, id_documental))
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            return {"ok": False, "error": "Documental no encontrado"}
        return {"ok": True, "documental": dict(updated)}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        cur.close(); conn.close()

@app.delete("/api/documentales/{id_documental}")
def eliminar_documental(id_documental: int):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM documental WHERE id_documental = %s", (id_documental,))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": "No se puede eliminar: tiene datos relacionados."}
    finally:
        cur.close(); conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return {"status": "ok", "db": "conectada"}
    except Exception as e:
        return {"status": "error", "db": str(e)}
