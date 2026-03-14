import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def get_engine():
    """Crea y devuelve la conexión SQLAlchemy basándose en la configuración del .env"""
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    try:
        if db_type == "mysql":
            db_host = os.getenv("DB_HOST", "127.0.0.1")
            db_user = os.getenv("DB_USER", "root")
            db_password = os.getenv("DB_PASSWORD", "")
            db_name = os.getenv("DB_NAME", "quality_water")
            db_port = os.getenv("DB_PORT", "3306")
            
            # Cadena de conexión usando mysql-connector-python
            connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            st.sidebar.success("🔗 Conectado a **MySQL**")
            
        elif db_type == "sqlite":
            sqlite_file = "quality_water.db"
            if not os.path.exists(sqlite_file):
                st.error(f"El archivo SQLite '{sqlite_file}' no existe. Por favor, ejecuta la migración primero.")
                return None
            
            # Cadena de conexión usando sqlite
            connection_string = f"sqlite:///{sqlite_file}"
            st.sidebar.success("🔗 Conectado a **SQLite** (Local)")
        else:
            st.error(f"Tipo de base de datos no soportado: {db_type}")
            return None

        engine = create_engine(connection_string)
        return engine
        
    except Exception as e:
        st.error(f"Error al configurar la conexión a la base de datos: {e}")
        return None

@st.cache_data(ttl=600)
def load_data():
    """Carga los datos de irca_historico independientemente del motor y los almacena en caché."""
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()
        
    query = "SELECT * FROM irca_historico;"
    
    try:
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        st.error(f"Error al consultar la tabla irca_historico: {e}")
        return pd.DataFrame()
