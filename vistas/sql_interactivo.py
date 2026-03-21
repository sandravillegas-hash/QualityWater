import streamlit as st
import pandas as pd
from database import get_engine

def render_sql_interactivo():
    st.title("🛠️ Laboratorio SQL Interactivo")
    st.markdown("Esta sección te permite escribir y ejecutar tus propias consultas SQL directamente sobre la base de datos `quality_water` de manera libre.")
    
    col_info, col_query = st.columns([1.2, 2])
    
    with col_info:
        st.markdown("### 📚 Diccionario de Datos")
        st.info("El esquema relacional cuenta con **8 tablas** conectadas:")
        
        st.markdown("""
        1. **`irca_historico`**: Tabla consolidada con los reportes de IRCA por ciudad/departamento.
        2. **`muestra`**: Fechas y ubicación macro de recolección física del agua.
        3. **`resultado_detalle`**: El microscopio de los datos. Contiene los resultados precisos por cada parámetro medido en las muestras.
        4. **`parametro`**: Catálogo descriptivo (ej. Mercurio, Cloro, E.Coli).
        5. **`prestador`**: Organismos/Empresas encargadas de los sistemas de acueducto.
        6. **`punto_muestreo`**: Ubicaciones específicas (lat/lon) y características constructivas.
        7. **`geografia`**: Catálogo oficial DANE de departamentos y municipios.
        8. **`tipo_muestra`**: Metodología y red de donde se extrajo el agua.
        """)
        
        with st.expander("💡 Ejemplos de Consultas"):
            st.code("""-- 1. Ver primeros reportes IRCA
SELECT * FROM irca_historico LIMIT 5;

-- 2. Prestadores con más muestras
SELECT p.nombre_prestador, COUNT(m.id_muestra) as total
FROM prestador p
JOIN muestra m ON p.id_prestador = m.id_prestador
GROUP BY p.nombre_prestador
ORDER BY total DESC LIMIT 10;

-- 3. Conteo de parámetros medidos
SELECT nombre, unidad_medida 
FROM parametro LIMIT 5;
            """, language="sql")
            
    with col_query:
        st.markdown("### 💻 Consola de Ejecución")
        query_input = st.text_area("✍️ Escribe tu consulta SQL aquí:", height=200, value="SELECT * FROM irca_historico LIMIT 15;")
        
        if st.button("▶️ Ejecutar Consulta", type="primary", use_container_width=True):
            engine = get_engine()
            try:
                # Pandas se encarga de lanzar el query, recuperar el dataset y cerrar la conexión
                with st.spinner("Consultando la base de datos..."):
                    df_result = pd.read_sql(query_input, con=engine)
                
                st.success(f"Consulta ejecutada con éxito. Se recuperaron **{len(df_result)}** filas.")
                
                st.markdown("**Resultados:**")
                st.dataframe(df_result, use_container_width=True)
                
            except Exception as e:
                st.error("❌ Ocurrió un error de sintaxis o de conexión al ejecutar tu consulta:")
                st.code(str(e), language="bash")
