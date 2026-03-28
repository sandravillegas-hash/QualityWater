# QualityWater
Análisis histórico del indicador IRCA
Una aplicación web interactiva construida con **Streamlit** para visualizar y analizar el dataset de Uber extraído de una base de datos SQL.
 
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)


# 💧 Dashboard de Calidad del Agua (IRCA Histórico)


Este proyecto es una aplicación web interactiva construida con **Python** y **Streamlit**. Está diseñada para explorar de forma visual e interactiva el histórico del **Índice de Riesgo de la Calidad del Agua (IRCA)** a nivel departamental y municipal en Colombia.

## 🚀 Características Principales

- **Filtros Interactivos**: Permite filtrar los registros por año, departamento y municipio.
- **KPIs Dinámicos**: Muestra automáticamente los promedios del IRCA General, Urbano y Rural, así como el conteo de mediciones filtradas.
- **Gráficos en Plotly**:
  - Evolución temporal de los promedios IRCA por zona.
  - Distribución tipo "pie" del nivel de riesgo general.
  - Top 10 municipios con peor nivel IRCA (barras horizontales).
  - Análisis de dispersión (scatter plot) comparando directamente IRCA Urbano vs Rural coloreado por nivel de riesgo general.
- **Soporte de Doble Base de Datos (Dual DB)**: Puede configurarse fácilmente para leer datos operativos de un motor MySQL o desde un archivo local auto-contenido de SQLite (`quality_water.db`).
- **Descarga de Datos**: Exporta la información visible en la grilla directamente a archivo `.csv`.

---

## 💻 Requisitos Previos

Necesitas tener instalado **Python 3.9, 3.10, 3.11, 3.12 o 3.13**. (Probado localmente en Python 3.13 con soporte nativo).

Las dependencias principales del proyecto se encuentran en `requirements.txt`:
- `streamlit`
- `pandas`
- `plotly`
- `sqlalchemy`
- `mysql-connector-python`
- `python-dotenv`

---

## ⚙️ Instalación y Configuración

1. **Clona o descarga este repositorio** en tu máquina local.
2. Abre una terminal en la carpeta principal del proyecto.
3. **Instala las dependencias** requeridas ejecutando:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configura las Credenciales**:
   El proyecto utiliza un archivo `.env` en la raíz de la carpeta para gestionar las conexiones. Edita este archivo en un block de notas o tu editor de código, definiendo tu usuario y contraseña (en caso de usar MySQL), y el motor de preferencia.

   Estructura obligatoria del `.env`:
   ```env
   DB_TYPE=sqlite
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=tu_contraseña
   DB_NAME=quality_water
   DB_PORT=3306
   ```

---

## 🗄️ Administración de Bases de Datos (MySQL vs SQLite)

Este proyecto puede funcionar en dos modalidades, que controlas mediante la primera línea de tu archivo `.env` (`DB_TYPE`):

### Opción A: Base de datos auto-contenida (RECOMENDADA)
Si cambias en el `.env` la configuración a `DB_TYPE=sqlite`, el proyecto no requerirá ningún servidor local externo (como XAMPP) operando. Simplemente leerá en tiempo real el archivo `quality_water.db` que ya consolida los datos de `irca_historico`.

### Opción B: Motor de base de datos MySQL 
Si cambias a `DB_TYPE=mysql`, el proyecto se conectará usando las credenciales del host local que brindes en las demás variables de entorno de este archivo (`DB_HOST`, `DB_PASSWORD`, etc.) para acceder a la base de datos `quality_water` de tu máquina.

> **Scripts Útiles Incluidos**:
> - `test_db.py`: Úsalo temporalmente (`python test_db.py`) para confirmar desde la terminal si MySQL está conectando sin requerir levantar toda la web app.
> - `migrate_to_sqlite.py`: Script para uso del administrador de datos. Se encarga únicamente de conectarse al MySQL en uso (`DB_TYPE=mysql`) mediante las credenciales, extraer todos los registros y construir un volcado o base local al archivo de `quality_water.db`.

---

## ▶️ Ejecución del Dashboard

Una vez todo esté configurado, ejecuta el dashboard abriendo tu consola y usando el siguiente comando:

```bash
streamlit run app.py
```

La aplicación procesará la lectura de la base de datos, levantará un servidor local automáticamente y se abrirá en tu navegador web por defecto en la dirección:
👉 **[http://localhost:8501](http://localhost:8501)**
