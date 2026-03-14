import os
import pandas as pd
from dotenv import load_dotenv
import mysql.connector

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def test_connection():
    """Prueba la conexión a la base de datos usando mysql-connector-python y obtiene el top 5 de irca_historico"""
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "quality_water")
    db_port = os.getenv("DB_PORT", "3306")

    print(f"[*] Intentando conectar a la base de datos MySQL en {db_host}:{db_port} como usuario '{db_user}'...")
    
    try:
        # Establece la conexión directa
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )

        if connection.is_connected():
            print("[+] ¡Conexión exitosa a la base de datos!")
            
            # Consultar los primeros 5 registros
            query = "SELECT * FROM irca_historico LIMIT 5;"
            print("\n[*] Ejecutando consulta: SELECT * FROM irca_historico LIMIT 5;")
            
            # Usar pandas para mostrar los datos de forma bonita
            df = pd.read_sql(query, con=connection)
            
            if df.empty:
                print("[-] La tabla está vacía o no tiene registros aún.")
            else:
                print("\n=== TOP 5 REGISTROS DE 'irca_historico' ===")
                print(df.to_string())
                print("===========================================\n")
                
    except mysql.connector.Error as err:
        print(f"[X] Error de MySQL: {err}")
    except Exception as e:
        print(f"[X] Ocurrió un error inesperado: {e}")
    finally:
        # Cierra la conexión si está abierta
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("[*] Conexión cerrada.")

if __name__ == "__main__":
    test_connection()
