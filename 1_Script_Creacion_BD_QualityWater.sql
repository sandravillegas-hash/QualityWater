CREATE SCHEMA Quality_Water;
use quality_water;

CREATE TABLE irca_historico (
    id_registro INT NOT NULL AUTO_INCREMENT,
    depto_cod INT,
    depto_nombre VARCHAR(100),
    muni_cod VARCHAR(20),
    muni_nombre VARCHAR(100),
    anio INT,
    irca_general FLOAT NULL,
    riesgo_general VARCHAR(100),
    irca_urbano FLOAT NULL,
    riesgo_urbano VARCHAR(100),
    irca_rural FLOAT NULL,
    riesgo_rural VARCHAR(100),
    PRIMARY KEY (id_registro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE geografia (
    codigo_dane VARCHAR(10) NOT NULL COMMENT 'Código DANE de la ubicación',
    departamento VARCHAR(255) COMMENT 'Nombre del departamento',
    municipio VARCHAR(255) COMMENT 'Nombre del municipio',
    PRIMARY KEY (codigo_dane)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: parametro
-- Tabla maestra para los parámetros medidos.
CREATE TABLE tipo_muestra (
    id_tipo_muestra INT NOT NULL COMMENT 'ID único del tipo de muestra',
    descripcion TEXT COMMENT 'Descripción del tipo de muestra',
    PRIMARY KEY (id_tipo_muestra)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;


CREATE TABLE parametro (
    id_parametro INT NOT NULL COMMENT 'ID único del parámetro',
    nombre VARCHAR(255) COMMENT 'Nombre del parámetro',
    unidad_medida VARCHAR(50) COMMENT 'Unidad de medida del parámetro',
    limite_maximo_perm VARCHAR(100) COMMENT 'Límite máximo permitido',
    puntaje_calculo_irca DECIMAL(10, 4) COMMENT 'Puntaje asignado para el cálculo del IRCA',
    categoria VARCHAR(100) NULL COMMENT 'Categoría del parámetro' ,
   PRIMARY KEY (id_parametro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;

-- ALTER TABLE parametro 
-- ADD COLUMN categoria VARCHAR(100) NULL COMMENT 'Categoría del parámetro' AFTER puntaje_calculo_irca;


-- Tabla: prestador
-- Tabla maestra de los prestadores del servicio.
CREATE TABLE prestador (
    id_prestador INT NOT NULL COMMENT 'ID único del prestador',
    codigo_rups VARCHAR(50) COMMENT 'Código RUPS del prestador',
    nombre_prestador VARCHAR(255) COMMENT 'Nombre del prestador',
    PRIMARY KEY (id_prestador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: punto_muestreo
-- Depende de 'geografia'.
CREATE TABLE punto_muestreo (
    id_punto INT NOT NULL COMMENT 'ID único del punto de muestreo',
    codigo_dane VARCHAR(10) COMMENT 'Código DANE de la ubicación (llave foránea)',
    ubicacion_red VARCHAR(255) COMMENT 'Descripción de la ubicación en la red',
    direccion TEXT COMMENT 'Dirección física del punto',
    zona TEXT COMMENT 'Zona de ubicación',
    latitud_grados INT COMMENT 'Grados de latitud',
    latitud_minutos INT COMMENT 'Minutos de latitud',
    latitud_segundos DECIMAL(10, 6) COMMENT 'Segundos de latitud',
    longitud_grados INT COMMENT 'Grados de longitud',
    longitud_minutos INT COMMENT 'Minutos de longitud',
    longitud_segundos DECIMAL(10, 6) COMMENT 'Segundos de longitud',
    PRIMARY KEY (id_punto),
    CONSTRAINT fk_punto_geografia
        FOREIGN KEY (codigo_dane)
        REFERENCES geografia (codigo_dane)
        ON DELETE SET NULL -- Si se borra la geografía, el punto queda sin ubicación
        ON UPDATE CASCADE  -- Si cambia el código DANE, se actualiza aquí
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: muestra
-- Depende de 'prestador', 'punto_muestreo' y 'tipo_muestra'.
CREATE TABLE muestra (
    id_muestra INT NOT NULL COMMENT 'ID único de la muestra',
    id_prestador INT COMMENT 'ID del prestador (llave foránea)',
    id_punto INT COMMENT 'ID del punto de muestreo (llave foránea)',
    id_tipo_muestra INT COMMENT 'ID del tipo de muestra (llave foránea)',
    fecha_toma DATE COMMENT 'Fecha de toma de la muestra',
    agua_tratada VARCHAR(2) COMMENT 'Indica si es agua tratada (Sí, no)',
    producto_priorizacion VARCHAR(255) COMMENT 'Producto asociado a la priorización',
    criterio_priorizacion VARCHAR(255) COMMENT 'Criterio de priorización utilizado',
    porcentaje_irca DECIMAL(10, 4) COMMENT 'Porcentaje de IRCA calculado',
    nivel_riesgo VARCHAR(100) COMMENT 'Nivel de riesgo determinado',
    PRIMARY KEY (id_muestra),
    CONSTRAINT fk_muestra_prestador
        FOREIGN KEY (id_prestador)
        REFERENCES prestador (id_prestador)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_muestra_punto
        FOREIGN KEY (id_punto)
        REFERENCES punto_muestreo (id_punto)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_muestra_tipo
        FOREIGN KEY (id_tipo_muestra)
        REFERENCES tipo_muestra (id_tipo_muestra)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: resultado_detalle
-- Depende de 'muestra' y 'parametro'.
CREATE TABLE resultado_detalle (
    id_resultado INT NOT NULL COMMENT 'ID único del resultado',
    id_muestra INT NOT NULL COMMENT 'ID de la muestra (llave foránea)',
    id_parametro INT NOT NULL COMMENT 'ID del parámetro (llave foránea)',
    resultado_valor VARCHAR(255) COMMENT 'Valor del resultado obtenido',
    incertidumbre VARCHAR(100) COMMENT 'Incertidumbre asociada al resultado',
    cumplimiento VARCHAR(100) COMMENT 'Indica cumplimiento del parámetro',
    PRIMARY KEY (id_resultado),
    CONSTRAINT fk_resultado_muestra
        FOREIGN KEY (id_muestra)
        REFERENCES muestra (id_muestra)
        ON DELETE CASCADE -- Si se borra la muestra, se borran sus resultados detallados
        ON UPDATE CASCADE,
    CONSTRAINT fk_resultado_parametro
        FOREIGN KEY (id_parametro)
        REFERENCES parametro (id_parametro)
        ON DELETE RESTRICT -- No se puede borrar el parámetro si tiene resultados asociados
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
