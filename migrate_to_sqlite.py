import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def migrate_mysql_to_sqlite():
    """Conecta a MySQL, extrae la tabla y la guarda en una base local SQLite."""
    # 1. Conexión a MySQL original
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "quality_water")
    db_port = os.getenv("DB_PORT", "3306")

    print(f"[*] Conectando a MySQL ({db_host}:{db_port} - {db_name})...")
    mysql_conn_str = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        mysql_engine = create_engine(mysql_conn_str)
        
        # Leer datos de MySQL
        print("[*] Extrayendo datos de la tabla 'irca_historico' en MySQL...")
        df = pd.read_sql("SELECT * FROM irca_historico;", con=mysql_engine)
        
        if df.empty:
            print("[-] No hay datos en la tabla MySQL para migrar. Cancelando.")
            return

        print(f"[+] Se extrajeron {len(df)} registros correctamente.")

        # 2. Conexión a la nueva SQLite
        sqlite_file = "quality_water.db"
        sqlite_conn_str = f"sqlite:///{sqlite_file}"
        print(f"[*] Creando y conectando a base de datos SQLite local: {sqlite_file}...")
        sqlite_engine = create_engine(sqlite_conn_str)
        
        # Volcar datos a SQLite (Reemplaza la tabla si ya existe)
        print("[*] Volcando datos a SQLite...")
        df.to_sql('irca_historico', con=sqlite_engine, if_exists='replace', index=False)
        
        print("[+] ¡Migración completada exitosamente!")
        
    except Exception as e:
        print(f"[X] Hubo un error durante la migración: {e}")

if __name__ == "__main__":
    migrate_mysql_to_sqlite()
