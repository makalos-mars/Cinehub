
SET client_encoding = 'UTF8';

CREATE TABLE aficionado(
    correo_aficionado VARCHAR(100) PRIMARY KEY, 
    nombre VARCHAR(100), 
    id_aficionado INT
);

CREATE TABLE critico(
    correo_critico VARCHAR(100) PRIMARY KEY, 
    nombre VARCHAR(100), 
    cedula_profesional VARCHAR(20)
);

CREATE TABLE reportero(
    correo_reportero VARCHAR(100) PRIMARY KEY, 
    nombre VARCHAR(100),
    nota TEXT,
    portafolio TEXT
);

CREATE TABLE opinion(
    id INT PRIMARY KEY, 
    calificacion INT, 
    comentario TEXT,
    correo_reportero VARCHAR(100),
    correo_aficionado VARCHAR(100),
    correo_critico VARCHAR(100),
    FOREIGN KEY (correo_reportero) REFERENCES reportero(correo_reportero),
    FOREIGN KEY (correo_aficionado) REFERENCES aficionado(correo_aficionado),
    FOREIGN KEY (correo_critico) REFERENCES critico(correo_critico)
);

CREATE TABLE director(
    correo VARCHAR(100) PRIMARY KEY,
    nombre VARCHAR(100),
    guion TEXT
);

-- Tabla de autenticación separada del perfil.
-- 'rol' indica en qué tabla buscar el perfil completo del usuario.
-- En producción, 'contrasena' debe almacenarse como hash (bcrypt/argon2).
CREATE TABLE credenciales (
    correo      VARCHAR(100) PRIMARY KEY,
    contrasena  VARCHAR(255) NOT NULL,
    rol         VARCHAR(20)  NOT NULL CHECK (rol IN ('aficionado', 'critico', 'reportero', 'director'))
);

CREATE TABLE produccion(
    id_produccion INT PRIMARY KEY, 
    tipo VARCHAR(50), 
    estado VARCHAR(50), 
    genero VARCHAR(50),
    correo_director VARCHAR(100),
    FOREIGN KEY (correo_director) REFERENCES director(correo)
);

CREATE TABLE pelicula(
    id_pelicula INT PRIMARY KEY, 
    titulo VARCHAR(100), 
    genero VARCHAR(100), 
    portada TEXT, 
    sinopsis TEXT, 
    formato VARCHAR(50), 
    duracion INTERVAL,
    id_opinion INT,
    correo_director VARCHAR(100),
    id_produccion INT,
    FOREIGN KEY (id_opinion) REFERENCES opinion(id),
    FOREIGN KEY (correo_director) REFERENCES director(correo),
    FOREIGN KEY (id_produccion) REFERENCES produccion(id_produccion)
);

CREATE TABLE reparto(
    id_reparto INT PRIMARY KEY, 
    actor VARCHAR(100), 
    extra VARCHAR(100), 
    doble VARCHAR(100),
    id_produccion INT,
    FOREIGN KEY (id_produccion) REFERENCES produccion(id_produccion)
);

CREATE TABLE cine(
    no_sucursal INT PRIMARY KEY, 
    nombre_cine VARCHAR(100), 
    ubicacion VARCHAR(200), 
    numero_sala INT
);

CREATE TABLE cartelera(
    id_pelicula INT,
    no_sucursal INT,
    horario_de_emision TIME, 
    PRIMARY KEY (id_pelicula, no_sucursal),
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula),
    FOREIGN KEY (no_sucursal) REFERENCES cine(no_sucursal)
);


INSERT INTO aficionado(correo_aficionado, nombre, id_aficionado) VALUES
('juanito@gmail.com', 'Juan Pérez', 101),
('laura_mtz@gmail.com', 'Laura Martínez', 102),
('carlos_rojas@gmail.com', 'Carlos Rojas', 103),
('maria_garcia@gmail.com', 'María García', 104),
('jorge_lopez@gmail.com', 'Jorge López', 105),
('ana_fernandez@gmail.com', 'Ana Fernández', 106),
('luis_sanchez@gmail.com', 'Luis Sánchez', 107),
('paty_gomez@gmail.com', 'Patricia Gómez', 108),
('roberto_ramirez@gmail.com', 'Roberto Ramírez', 109),
('veronica_flores@gmail.com', 'Verónica Flores', 110),
('fernando_morales@gmail.com', 'Fernando Morales', 111),
('andrea_castro@gmail.com', 'Andrea Castro', 112),
('ricardo_orozco@gmail.com', 'Ricardo Orozco', 113),
('paola_mendoza@gmail.com', 'Paola Mendoza', 114),
('alejandro_navarro@gmail.com', 'Alejandro Navarro', 115);

INSERT INTO critico (correo_critico, nombre, cedula_profesional) VALUES
('carlos_monsi@gmail.com', 'Carlos Monsiváis', 'CP777'),
('maria_ibarguengoitia@gmail.com', 'María Ibargüengoitia', 'CP888'),
('jorge_ayala@gmail.com', 'Jorge Ayala Blanco', 'CP999'),
('fernando_rossi@gmail.com', 'Fernando Rossi', 'CP111'),
('hadassa_hill@gmail.com', 'Hadassa Hill', 'CP222'),
('leonardo_garcia@gmail.com', 'Leonardo García Tsao', 'CP333'),
('lucia_carreras@gmail.com', 'Lucía Carreras', 'CP444'),
('arturo_aguilar@gmail.com', 'Arturo Aguilar', 'CP555'),
('elisa_lozano@gmail.com', 'Elisa Lozano', 'CP666'),
('rafael_azcona@gmail.com', 'Rafael Azcona', 'CP000'),
('beatriz_garcia@gmail.com', 'Beatriz García', 'CP7772'),
('oscar_sanchez@gmail.com', 'Óscar Sánchez', 'CP8882'),
('daniela_morales@gmail.com', 'Daniela Morales', 'CP9992'),
('enrique_franco@gmail.com', 'Enrique Franco', 'CP1112'),
('silvia_vargas@gmail.com', 'Silvia Vargas', 'CP2222');

INSERT INTO reportero(correo_reportero, nombre, nota, portafolio) VALUES
('jose_luis@gmail.com', 'José Luis Hernández', 'Cine mexicano', 'https://portafolio.joseluis.com'),
('maria_fernanda@tv.com', 'María Fernanda Ramírez', 'Entrevistas', 'https://portafolio.mfernanda.com'),
('carlos_alberto@gmail.com', 'Carlos Alberto Mendoza', 'Crítica', 'https://portafolio.carlosalberto.com'),
('ana_silvia@azteca.com', 'Ana Silvia López', 'Reportajes especiales', 'https://portafolio.anasilvia.com'),
('javier_martinez@gmail.com', 'Javier Martínez', 'Espectáculos', 'https://portafolio.javiermtz.com'),
('paulina_garcia@gmail.com', 'Paulina García', 'Cobertura de festivales', 'https://portafolio.paulinag.com'),
('ricardo_sanchez@eluniversal.com', 'Ricardo Sánchez', 'Columnas', 'https://portafolio.ricardos.com'),
('laura_limon@gmail.com', 'Laura Limón', 'Investigación', 'https://portafolio.lauralimon.com'),
('fernando_montes@televisa.com', 'Fernando Montes', 'Noticias nocturnas', 'https://portafolio.fernandomontes.com'),
('carmen_ruiz@gmail.com', 'Carmen Ruiz', 'Espectáculos', 'https://portafolio.carmenruiz.com'),
('pedro_salinas@gmail.com', 'Pedro Salinas', 'Cine independiente', 'https://portafolio.pedrosalinas.com'),
('victor_manzana@gmail.com', 'Víctor Manzana', 'Sátira política', 'https://portafolio.victormanzana.com'),
('daniel_velasco@gmail.com', 'Daniel Velasco', 'Análisis cinematográfico', 'https://portafolio.danielvelasco.com'),
('martha_ortega@gmail.com', 'Martha Ortega', 'Documentales', 'https://portafolio.marthaortega.com'),
('roberto_campos@gmail.com', 'Roberto Campos', 'Noticias culturales', 'https://portafolio.robertocampos.com');


INSERT INTO director(correo, nombre, guion) VALUES
('alfonso_arau@gmail.com', 'Alfonso Arau', 'Adaptación de la novela de Laura Esquivel'),
('roberto_gomez@gmail.com', 'Roberto Gómez Bolaños', 'Creador de personajes como el Chavo del 8'),
('xavier_robles@gmail.com', 'Xavier Robles', 'Guion original basado en hechos reales'),
('fernando_kalife@gmail.com', 'Fernando Kalife', 'Guion sobre el Mundial México 86'),
('guillermo_del_toro@gmail.com', 'Guillermo del Toro', 'Guion original de fantasía oscura'),
('alejandro_inarritu@gmail.com', 'Alejandro González Iñárritu', 'Historias cruzadas en la CDMX'),
('carlos_cuaron@gmail.com', 'Carlos Cuarón', 'Comedia dramática sobre fútbol'),
('amate_escalante@gmail.com', 'Amat Escalante', 'Drama social sobre el narcotráfico'),
('michelle_rodriguez@gmail.com', 'Michelle Rodríguez', 'Acción con temática policiaca'),
('luis_estrada@gmail.com', 'Luis Estrada', 'Sátira política sobre medios de comunicación'),
('emilio_portes@gmail.com', 'Emilio Portes', 'Comedia navideña con humor negro'),
('kenya_marquez@gmail.com', 'Kenya Márquez', 'Documental sobre clases sociales'),
('natalia_beristain@gmail.com', 'Natalia Beristáin', 'Drama sobre relaciones femeninas'),
('rigoberto_castaneda@gmail.com', 'Rigoberto Castañeda', 'Terror basado en leyendas urbanas'),
('jorge_michel@gmail.com', 'Jorge Michel Grau', 'Terror con crítica social');


INSERT INTO produccion(id_produccion, tipo, estado, genero, correo_director) VALUES
(101, 'Largometraje', 'Finalizada', 'Drama Romántico', 'alfonso_arau@gmail.com'),
(102, 'Serie', 'Finalizada', 'Comedia', 'roberto_gomez@gmail.com'),
(103, 'Documental', 'Finalizada', 'Crimen', 'xavier_robles@gmail.com'),
(104, 'Serie', 'Desarrollo', 'Deporte', 'fernando_kalife@gmail.com'),
(105, 'Largometraje', 'Finalizada', 'Fantasía Oscura', 'guillermo_del_toro@gmail.com'),
(106, 'Largometraje', 'Finalizada', 'Drama', 'alejandro_inarritu@gmail.com'),
(107, 'Largometraje', 'Finalizada', 'Comedia', 'carlos_cuaron@gmail.com'),
(108, 'Largometraje', 'Finalizada', 'Drama', 'amate_escalante@gmail.com'),
(109, 'Largometraje', 'Rodaje', 'Acción', 'michelle_rodriguez@gmail.com'),
(110, 'Largometraje', 'Finalizada', 'Comedia Satírica', 'luis_estrada@gmail.com'),
(111, 'Serie', 'Finalizada', 'Comedia', 'emilio_portes@gmail.com'),
(112, 'Largometraje', 'Rodaje', 'Social', 'kenya_marquez@gmail.com'),
(113, 'Largometraje', 'Finalizada', 'Drama', 'natalia_beristain@gmail.com'),
(114, 'Largometraje', 'Finalizada', 'Terror', 'rigoberto_castaneda@gmail.com'),
(115, 'Largometraje', 'Finalizada', 'Terror', 'jorge_michel@gmail.com');

INSERT INTO opinion(id, calificacion, comentario, correo_reportero, correo_aficionado, correo_critico) VALUES
(2001, 5, 'Un clásico del cine mexicano, lleno de magia y tradición', 'jose_luis@gmail.com', NULL, NULL),
(2002, 4, 'El humor de Chespirito nunca pasa de moda', NULL, 'juanito@gmail.com', NULL),
(2003, 5, 'Documental desgarrador e imprescindible', NULL, NULL, 'carlos_monsi@gmail.com'),
(2004, 3, 'Buena nostalgia ochentera, pero le falta ritmo', 'javier_martinez@gmail.com', NULL, NULL),
(2005, 5, 'Obra maestra del cine fantástico', NULL, 'maria_garcia@gmail.com', NULL),
(2006, 5, 'Cruda y real, Iñárritu en su mejor momento', NULL, NULL, 'jorge_ayala@gmail.com'),
(2007, 4, 'Comedia divertida con diálogos ingeniosos', 'paulina_garcia@gmail.com', NULL, NULL),
(2008, 4, 'Incómoda y necesaria', NULL, 'carlos_rojas@gmail.com', NULL),
(2009, 3, 'Entretenida pero predecible', 'fernando_montes@televisa.com', NULL, NULL),
(2010, 5, 'La mejor sátira política mexicana', NULL, NULL, 'leonardo_garcia@gmail.com'),
(2011, 4, 'Pastorela con mucho corazón', 'victor_manzana@gmail.com', NULL, NULL),
(2012, 4, 'Conmovedor retrato de la maternidad', NULL, 'laura_mtz@gmail.com', NULL),
(2013, 5, 'Actuaciones magistrales', NULL, NULL, 'lucia_carreras@gmail.com'),
(2014, 3, 'Terror efectivo pero con altibajos', 'ricardo_sanchez@eluniversal.com', NULL, NULL),
(2015, 4, 'Violenta y perturbadora, bien lograda', NULL, 'jorge_lopez@gmail.com', NULL);

INSERT INTO pelicula(id_pelicula, titulo, genero, portada, sinopsis, formato, duracion, id_opinion, correo_director, id_produccion) VALUES
(301, 'Como agua para chocolate', 'Drama Romántico', 'agua_chocolate.jpg', 'Tita y Pedro viven un amor prohibido durante la Revolución Mexicana, donde la magia y la cocina se entrelazan', 'Digital', '1:45:00', 2001, 'alfonso_arau@gmail.com', 101),
(302, 'Chespirito', 'Comedia', 'chespirito.jpg', 'Programa de sketches del Chavo del 8, el Chapulín Colorado y más personajes icónicos', 'Digital', '0:30:00', 2002, 'roberto_gomez@gmail.com', 102),
(303, 'Las tres muertes de Marisela Escobedo', 'Crimen', 'marisela.jpg', 'Documental sobre la lucha de una madre por justicia tras el feminicidio de su hija en Chihuahua', 'Digital', '1:52:00', 2003, 'xavier_robles@gmail.com', 103),
(304, 'México 86', 'Deporte', 'mexico86.jpg', 'Serie sobre el histórico Mundial de Futbol donde Maradona brilló y México se consolidó como sede', 'Digital', '1:30:00', 2004, 'fernando_kalife@gmail.com', 104),
(305, 'El laberinto del fauno', 'Fantasía Oscura', 'laberinto_fauno.jpg', 'Ofelia descubre un mundo mágico mientras su madre vive la posguerra española', 'Digital', '1:58:00', 2005, 'guillermo_del_toro@gmail.com', 105),
(306, 'Amores perros', 'Drama', 'amores_perros.jpg', 'Tres historias conectadas por un accidente automovilístico en la Ciudad de México', 'Digital', '2:34:00', 2006, 'alejandro_inarritu@gmail.com', 106),
(307, 'Rudo y Cursi', 'Comedia', 'rudo_cursi.jpg', 'Dos hermanos que triunfan en el fútbol pero enfrentan la fama, el dinero y la traición', 'Digital', '1:43:00', 2007, 'carlos_cuaron@gmail.com', 107),
(308, 'Heli', 'Drama', 'heli.jpg', 'Una familia mexicana se ve envuelta en el narcotráfico tras el romance de la hija mayor', 'Digital', '1:45:00', 2008, 'amate_escalante@gmail.com', 108),
(309, 'Misión rescate', 'Acción', 'mision_rescate.jpg', 'Policía mexicana debe salvar a rehenes en un edificio tomado por narcotraficantes', 'IMAX', '1:55:00', 2009, 'michelle_rodriguez@gmail.com', 109),
(310, 'La dictadura perfecta', 'Comedia Satírica', 'dictadura_perfecta.jpg', 'Sátira sobre la manipulación de los medios de comunicación en México', 'Digital', '1:47:00', 2010, 'luis_estrada@gmail.com', 110),
(311, 'Pastorela', 'Comedia', 'pastorela.jpg', 'El diablo intenta robar un niño en una pastorela navideña mexicana', 'Digital', '1:36:00', 2011, 'emilio_portes@gmail.com', 111),
(312, 'Las niñas bien', 'Documental', 'ninas_bien.jpg', 'Retrato de la alta sociedad mexicana y sus privilegios', 'Digital', '1:25:00', 2012, 'kenya_marquez@gmail.com', 112),
(313, 'No quiero dormir sola', 'Drama', 'no_quiero_dormir.jpg', 'Dos mujeres exploran su amistad y sexualidad en la Ciudad de México', 'Digital', '1:33:00', 2013, 'natalia_beristain@gmail.com', 113),
(314, 'Kilómetro 31', 'Terror', 'km31.jpg', 'Una mujer investiga la desaparición de su hermana gemela en una carretera embrujada', 'Digital', '1:43:00', 2014, 'rigoberto_castaneda@gmail.com', 114),
(315, 'Somos lo que hay', 'Terror', 'somos_lo_que_hay.jpg', 'Familia de caníbales sobrevive tras la muerte del padre en un México contemporáneo', 'Digital', '1:30:00', 2015, 'jorge_michel@gmail.com', 115);


INSERT INTO reparto(id_reparto, actor, extra, doble, id_produccion) VALUES
(5001, 'Marco Leonardi', 'Extra 1', 'Doble 1', 101),
(5002, 'Lumi Cavazos', 'Extra 2', 'Doble 2', 101),
(5003, 'Roberto Gómez Bolaños', 'Extra 3', 'Doble 3', 102),
(5004, 'Flor Edwarda Gurrola', 'Extra 4', 'Doble 4', 103),
(5005, 'Diego Luna', 'Extra 5', 'Doble 5', 104),
(5006, 'Ivana Baquero', 'Extra 6', 'Doble 6', 105),
(5007, 'Gael García Bernal', 'Extra 7', 'Doble 7', 106),
(5008, 'Adriana Barraza', 'Extra 8', 'Doble 8', 106),
(5009, 'Demián Bichir', 'Extra 9', 'Doble 9', 107),
(5010, 'Armando Espitia', 'Extra 10', 'Doble 10', 108),
(5011, 'Martha Higareda', 'Extra 11', 'Doble 11', 109),
(5012, 'Damián Alcázar', 'Extra 12', 'Doble 12', 110),
(5013, 'Joaquín Cosío', 'Extra 13', 'Doble 13', 110),
(5014, 'Ana de la Reguera', 'Extra 14', 'Doble 14', 111),
(5015, 'Iliana Fox', 'Extra 15', 'Doble 15', 112),
(5016, 'Ximena Sariñana', 'Extra 16', 'Doble 16', 113),
(5017, 'Mayra Sérbulo', 'Extra 17', 'Doble 17', 114),
(5018, 'Francisco Barreiro', 'Extra 18', 'Doble 18', 115);


INSERT INTO cine(no_sucursal, nombre_cine, ubicacion, numero_sala) VALUES
(1, 'Cinepolis Perisur', 'CDMX', 15),
(2, 'Cinemex Patriotismo', 'CDMX', 8),
(3, 'Cinepolis Andares', 'Guadalajara', 14),
(4, 'Cinepolis Angelopolis', 'Puebla', 12),
(5, 'Cinepolis Morelia', 'Michoacán', 8),
(6, 'Cinemark Reforma', 'CDMX', 10),
(7, 'Cinepolis Satelite', 'Estado de México', 18),
(8, 'Cinemex Antara', 'CDMX', 6),
(9, 'Cinepolis Monterrey', 'Monterrey', 12),
(10, 'Cinepolis Cancún', 'Quintana Roo', 9),
(11, 'Cinepolis Tijuana', 'Tijuana', 10),
(12, 'Cinemex Santa Fe', 'CDMX', 8),
(13, 'Cinepolis Querétaro', 'Querétaro', 12),
(14, 'Cinepolis Mérida', 'Yucatán', 7),
(15, 'Cinemex Universidad', 'CDMX', 5);

INSERT INTO cartelera(id_pelicula, no_sucursal, horario_de_emision) VALUES
(301, 1, '16:00:00'),
(301, 2, '18:30:00'),
(301, 3, '20:00:00'),
(302, 4, '10:00:00'),
(302, 5, '12:30:00'),
(303, 6, '17:00:00'),
(303, 7, '19:30:00'),
(304, 8, '15:00:00'),
(304, 9, '21:00:00'),
(305, 10, '16:30:00'),
(305, 11, '20:30:00'),
(306, 12, '18:00:00'),
(306, 13, '22:00:00'),
(307, 14, '14:00:00'),
(307, 15, '17:30:00'),
(308, 1, '19:00:00'),
(308, 2, '21:30:00'),
(309, 3, '16:00:00'),
(309, 4, '20:00:00'),
(310, 5, '18:00:00'),
(310, 6, '20:30:00'),
(311, 7, '15:30:00'),
(311, 8, '19:00:00'),
(312, 9, '17:00:00'),
(312, 10, '21:00:00'),
(313, 11, '16:00:00'),
(313, 12, '18:30:00'),
(314, 13, '20:00:00'),
(314, 14, '22:30:00'),
(315, 15, '19:00:00'),
(315, 1, '21:00:00');

INSERT INTO credenciales (correo, contrasena, rol) VALUES
('juanito@gmail.com',          'test1234', 'aficionado'),
('laura_mtz@gmail.com',        'test1234', 'aficionado'),
('carlos_rojas@gmail.com',     'test1234', 'aficionado'),
('maria_garcia@gmail.com',     'test1234', 'aficionado'),
('jorge_lopez@gmail.com',      'test1234', 'aficionado'),
('ana_fernandez@gmail.com',    'test1234', 'aficionado'),
('luis_sanchez@gmail.com',     'test1234', 'aficionado'),
('paty_gomez@gmail.com',       'test1234', 'aficionado'),
('roberto_ramirez@gmail.com',  'test1234', 'aficionado'),
('veronica_flores@gmail.com',  'test1234', 'aficionado'),
('fernando_morales@gmail.com', 'test1234', 'aficionado'),
('andrea_castro@gmail.com',    'test1234', 'aficionado'),
('ricardo_orozco@gmail.com',   'test1234', 'aficionado'),
('paola_mendoza@gmail.com',    'test1234', 'aficionado'),
('alejandro_navarro@gmail.com','test1234', 'aficionado'),
('carlos_monsi@gmail.com',        'test1234', 'critico'),
('maria_ibarguengoitia@gmail.com','test1234', 'critico'),
('jorge_ayala@gmail.com',         'test1234', 'critico'),
('fernando_rossi@gmail.com',      'test1234', 'critico'),
('hadassa_hill@gmail.com',        'test1234', 'critico'),
('leonardo_garcia@gmail.com',     'test1234', 'critico'),
('lucia_carreras@gmail.com',      'test1234', 'critico'),
('arturo_aguilar@gmail.com',      'test1234', 'critico'),
('elisa_lozano@gmail.com',        'test1234', 'critico'),
('rafael_azcona@gmail.com',       'test1234', 'critico'),
('beatriz_garcia@gmail.com',      'test1234', 'critico'),
('oscar_sanchez@gmail.com',       'test1234', 'critico'),
('daniela_morales@gmail.com',     'test1234', 'critico'),
('enrique_franco@gmail.com',      'test1234', 'critico'),
('silvia_vargas@gmail.com',       'test1234', 'critico'),
('jose_luis@gmail.com',              'test1234', 'reportero'),
('maria_fernanda@tv.com',            'test1234', 'reportero'),
('carlos_alberto@gmail.com',         'test1234', 'reportero'),
('ana_silvia@azteca.com',            'test1234', 'reportero'),
('javier_martinez@gmail.com',        'test1234', 'reportero'),
('paulina_garcia@gmail.com',         'test1234', 'reportero'),
('ricardo_sanchez@eluniversal.com',  'test1234', 'reportero'),
('laura_limon@gmail.com',            'test1234', 'reportero'),
('fernando_montes@televisa.com',     'test1234', 'reportero'),
('carmen_ruiz@gmail.com',            'test1234', 'reportero'),
('pedro_salinas@gmail.com',          'test1234', 'reportero'),
('victor_manzana@gmail.com',         'test1234', 'reportero'),
('daniel_velasco@gmail.com',         'test1234', 'reportero'),
('martha_ortega@gmail.com',          'test1234', 'reportero'),
('roberto_campos@gmail.com',         'test1234', 'reportero'),
('alfonso_arau@gmail.com',          'test1234', 'director'),
('roberto_gomez@gmail.com',         'test1234', 'director'),
('xavier_robles@gmail.com',         'test1234', 'director'),
('fernando_kalife@gmail.com',       'test1234', 'director'),
('guillermo_del_toro@gmail.com',    'test1234', 'director'),
('alejandro_inarritu@gmail.com',    'test1234', 'director'),
('carlos_cuaron@gmail.com',         'test1234', 'director'),
('amate_escalante@gmail.com',       'test1234', 'director'),
('michelle_rodriguez@gmail.com',    'test1234', 'director'),
('luis_estrada@gmail.com',          'test1234', 'director'),
('emilio_portes@gmail.com',         'test1234', 'director'),
('kenya_marquez@gmail.com',         'test1234', 'director'),
('natalia_beristain@gmail.com',     'test1234', 'director'),
('rigoberto_castaneda@gmail.com',   'test1234', 'director'),
('jorge_michel@gmail.com',          'test1234', 'director');