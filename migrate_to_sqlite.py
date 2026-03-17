import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def migrate_mysql_to_sqlite():
    """Conecta a MySQL, extrae múltiples tablas y las guarda en una base local SQLite."""
    # 1. Conexión a MySQL original
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "quality_water")
    db_port = os.getenv("DB_PORT", "3306")

    print(f"[*] Conectando a MySQL ({db_host}:{db_port} - {db_name})...")
    mysql_conn_str = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Lista de todas las tablas en orden (tablas maestras primero)
    tablas_a_migrar = [
        "geografia",
        "tipo_muestra",
        "parametro",
        "prestador",
        "punto_muestreo",
        "muestra",
        "resultado_detalle",
        "irca_historico"
    ]

    try:
        mysql_engine = create_engine(mysql_conn_str)
        
        # 2. Conexión a la nueva SQLite
        sqlite_file = "quality_water.db"
        sqlite_conn_str = f"sqlite:///{sqlite_file}"
        print(f"[*] Creando y conectando a base de datos SQLite local: {sqlite_file}...")
        sqlite_engine = create_engine(sqlite_conn_str)

        print("-" * 50)
        # Iterar sobre las tablas y migrar cada una
        for tabla in tablas_a_migrar:
            print(f"[*] Extrayendo datos de la tabla '{tabla}' en MySQL...")
            try:
                # Leer datos de MySQL
                df = pd.read_sql(f"SELECT * FROM {tabla};", con=mysql_engine)
                
                if df.empty:
                    print(f"[-] No hay datos en '{tabla}' para migrar, pero se creará vacía.")
                else:
                    print(f"[+] Se leyeron {len(df)} registros de '{tabla}'.")

                # Volcar datos a SQLite (Reemplaza la tabla si ya existe)
                print(f"[*] Volcando '{tabla}' a SQLite...")
                df.to_sql(tabla, con=sqlite_engine, if_exists='replace', index=False)
                print(f"[OK] Tabla '{tabla}' migrada con éxito.\n")
                
            except Exception as e:
                 print(f"[X] Error migrando la tabla '{tabla}': {e}\n")

        print("-" * 50)
        print("[+] ¡Migración de base de datos expandida completada exitosamente!")
        
    except Exception as e:
        print(f"[X] Hubo un error de conexión inicial: {e}")

if __name__ == "__main__":
    migrate_mysql_to_sqlite()
