-- ============================================================
--  CineHub — Tablas de Serie y Documental
--  Ejecuta esto en PostgreSQL si las tablas no existen aún
-- ============================================================

-- SERIE
CREATE TABLE IF NOT EXISTS serie (
    id_serie       SERIAL PRIMARY KEY,
    titulo         VARCHAR(200) NOT NULL,
    genero         VARCHAR(80),
    anio           INTEGER,
    temporadas     INTEGER,
    sinopsis       TEXT,
    id_produccion  INTEGER REFERENCES produccion(id_produccion) ON DELETE SET NULL
);

-- DOCUMENTAL
CREATE TABLE IF NOT EXISTS documental (
    id_documental  SERIAL PRIMARY KEY,
    titulo         VARCHAR(200) NOT NULL,
    tema           VARCHAR(80),
    anio           INTEGER,
    duracion_min   INTEGER,
    sinopsis       TEXT,
    id_produccion  INTEGER REFERENCES produccion(id_produccion) ON DELETE SET NULL
);

-- COLUMNAS EXTRA EN PELICULA (por si no existen)
ALTER TABLE pelicula ADD COLUMN IF NOT EXISTS anio         INTEGER;
ALTER TABLE pelicula ADD COLUMN IF NOT EXISTS duracion_min INTEGER;
ALTER TABLE pelicula ADD COLUMN IF NOT EXISTS sinopsis     TEXT;

-- Datos de ejemplo para probar el catálogo
INSERT INTO serie (titulo, genero, anio, temporadas, sinopsis) VALUES
  ('El señor de los cielos', 'Drama', 2013, 8, 'Narcotraficante que simula su muerte.'),
  ('Club de Cuervos', 'Comedia', 2015, 4, 'Drama familiar con un club de fútbol.')
ON CONFLICT DO NOTHING;

INSERT INTO documental (titulo, tema, anio, duracion_min, sinopsis) VALUES
  ('Alfonso Cuarón: El director', 'Arte', 2020, 90, 'Vida y obra del director mexicano.'),
  ('México Profundo', 'Cultura', 2018, 75, 'Exploración de las culturas indígenas de México.')
ON CONFLICT DO NOTHING;
