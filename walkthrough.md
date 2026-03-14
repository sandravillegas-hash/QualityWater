# Análisis de `irca_historico` con Streamlit

Se ha construido un dashboard interactivo en Python usando la librería **Streamlit** para conectarse a la base de datos MySQL local (`quality_water`) y explorar la tabla `irca_historico`.

## 🛠 Arquitectura

El proyecto consta de los siguientes archivos:

- [requirements.txt](file:///c:/Users/sandvise/Desktop/talento%20tech/ANALISIS%20DE%20DATOS/PROYECTO/Quality_Water/requirements.txt): Contiene las dependencias necesarias (`streamlit`, `pandas`, `plotly`, `sqlalchemy`, y `mysql-connector-python`).
- [.env](file:///c:/Users/sandvise/Desktop/talento%20tech/ANALISIS%20DE%20DATOS/PROYECTO/Quality_Water/.env): Archivo para configurar de manera segura las credenciales de la base de datos (host, usuario, contraseña, db).
- [database.py](file:///c:/Users/sandvise/Desktop/talento%20tech/ANALISIS%20DE%20DATOS/PROYECTO/Quality_Water/database.py): Módulo que maneja la conexión a MySQL usando `SQLAlchemy` y que recupera todos los datos hacia un DataFrame de Pandas (utilizando caché en memoria para no saturar la base de datos).
- [app.py](file:///c:/Users/sandvise/Desktop/talento%20tech/ANALISIS%20DE%20DATOS/PROYECTO/Quality_Water/app.py): La aplicación principal del dashboard que renderiza:
  - Filtros interactivos de año, departamento y municipio.
  - KPIs con promedios del IRCA general, rural y urbano.
  - Gráficos interactivos construidos con Plotly.

## 📊 Vistas y Gráficos Implementados

1. **Evolución Temporal del IRCA Promedio:** Muestra un gráfico de líneas comparando el IRCA general, urbano y rural a lo largo de los años.
2. **Distribución de Riesgo General:** Un gráfico de anillos (pie chart) que ilustra el porcentaje de registros para los distintos niveles de riesgo (Bajo, Medio, Alto, Inviable, Sin Riesgo).
3. **Top 10 Municipios con Mayor IRCA:** Un gráfico de barras horizontales mostrando los casos más graves en el filtrado actual.
4. **Comparativa Urbano vs Rural:** Un gráfico de dispersión (scatter) coloreado según el nivel de riesgo general.

## 🚀 Cómo ejecutarlo

1. Configura tu contraseña de MySQL editando el archivo [.env](file:///c:/Users/sandvise/Desktop/talento%20tech/ANALISIS%20DE%20DATOS/PROYECTO/Quality_Water/.env):
   ```env
   DB_PASSWORD=tu_contraseña
   ```
2. Instala las dependencias abriendo la terminal en esta carpeta:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación de Streamlit:
   ```bash
   streamlit run app.py
   ```
   > El dashboard se abrirá de forma automática en tu navegador (usualmente en `http://localhost:8501`).
