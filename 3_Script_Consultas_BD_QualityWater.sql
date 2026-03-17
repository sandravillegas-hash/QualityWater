USE quality_water;

-- CONSULTA N°1. EXTRACCIÓN Y TRANSFORMACIÓN: Promedio de IRCA por Departamento
-- Objetivo: Obtener el nivel de riesgo promedio transformando el valor numérico a una categoría descriptiva.
SELECT 
    depto_nombre, 
    ROUND(AVG(irca_general), 2) AS promedio_irca,
    CASE 
        WHEN AVG(irca_general) > 80 THEN 'Inviable Sanitariamente'
        WHEN AVG(irca_general) > 35 THEN 'Riesgo Alto'
        WHEN AVG(irca_general) > 14 THEN 'Riesgo Medio'
        WHEN AVG(irca_general) > 5 THEN 'Riesgo Bajo'
        ELSE 'Sin Riesgo'
    END AS clasificacion_promedio
FROM irca_historico
WHERE muni_cod <> '0' -- Refinamiento: Excluir totales departamentales
GROUP BY depto_nombre
ORDER BY promedio_irca DESC;

-- CONSULTA N°2. JOIN Y REFINAMIENTO: Puntos de muestreo por Municipio y Departamento
-- Objetivo: Unir tablas para localizar geográficamente los puntos de control activos.
SELECT 
    g.departamento, 
    g.municipio, 
    p.ubicacion_red, 
    p.direccion,
    CONCAT(p.latitud_grados, '°', p.latitud_minutos, "'") AS coordenadas_lat
FROM punto_muestreo p
JOIN geografia g ON p.codigo_dane = g.codigo_dane
WHERE p.zona = 'Urbano' -- Refinamiento: Solo zonas urbanas
ORDER BY g.departamento, g.municipio;

-- CONSULTA N°3. Identificar muestras con IRCA superior al promedio nacional
-- Objetivo: Fase de Control para identificar desviaciones críticas.
SELECT 
    id_muestra, 
    fecha_toma, 
    porcentaje_irca, 
    nivel_riesgo
FROM muestra
WHERE porcentaje_irca > (SELECT AVG(porcentaje_irca) FROM muestra)
ORDER BY porcentaje_irca DESC;

-- 4. TRANSFORMACIÓN Y GROUP BY: Conteo de muestras por Nivel de Riesgo y Mes
-- Objetivo: Analizar la estacionalidad de la calidad del agua.

SELECT 
    MONTHNAME(fecha_toma) AS mes, 
    nivel_riesgo, 
    COUNT(*) AS total_muestras
FROM muestra
WHERE YEAR(fecha_toma) = 2024 -- Refinamiento: Uso de función YEAR estándar de MySQL
GROUP BY mes, nivel_riesgo
ORDER BY FIELD(mes, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August');

-- 5. MULTI-JOIN: Detalle completo de muestras, prestadores y ubicación
-- Objetivo: Consolidar información para reportes de control oficial.
SELECT 
    m.id_muestra, 
    pr.nombre_prestador, 
    g.municipio, 
    tm.descripcion AS detalle_tipo_muestra,
    m.porcentaje_irca
FROM muestra m
JOIN prestador pr ON m.id_prestador = pr.id_prestador
JOIN punto_muestreo p ON m.id_punto = p.id_punto
JOIN geografia g ON p.codigo_dane = g.codigo_dane
JOIN tipo_muestra tm ON m.id_tipo_muestra = tm.id_tipo_muestra
WHERE m.agua_tratada = 'Sí';


-- 6. CONTROL: Verificación de integridad de Geografía vs Histórico
-- Objetivo: Encontrar códigos DANE en el histórico que no existen en la tabla maestra de geografía.

SELECT 
    DISTINCT muni_cod, 
    muni_nombre 
FROM irca_historico
WHERE muni_cod COLLATE utf8mb4_unicode_ci NOT IN (
    SELECT codigo_dane 
    FROM geografia
) 
AND muni_cod <> '0';


-- 7. TRANSFORMACIÓN AVANZADA: Cálculo de desviación de puntos críticos
-- Objetivo: Comparar el IRCA de una muestra contra el límite máximo de "Sin Riesgo" (5%).
SELECT 
    id_muestra,
    porcentaje_irca,
    (porcentaje_irca - 5.0) AS desviacion_limite_seguro,
    IF(porcentaje_irca > 5.0, 'REQUIERE INTERVENCIÓN', 'CUMPLE') AS estado_alerta
FROM muestra
WHERE nivel_riesgo <> 'Sin Riesgo';


-- 8. EXTRACCIÓN Y REFINAMIENTO: Top 5 Prestadores con mayor riesgo promedio
-- Objetivo: Identificar los prestadores que requieren mayor vigilancia técnica.
SELECT 
    p.nombre_prestador, 
    COUNT(m.id_muestra) AS total_muestras_tomadas,
    ROUND(AVG(m.porcentaje_irca), 2) AS promedio_irca_prestador
FROM muestra m
JOIN prestador p ON m.id_prestador = p.id_prestador
GROUP BY p.nombre_prestador
HAVING COUNT(m.id_muestra) > 1 -- Refinamiento: Solo prestadores con más de una muestra
ORDER BY promedio_irca_prestador DESC
LIMIT 5;