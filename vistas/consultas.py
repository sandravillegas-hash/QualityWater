import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_engine

def render_consultas_analiticas():
    st.title("📊 Consultas Analíticas (SQL)")
    st.markdown("Ejecución directa de consultas SQL sobre la base de datos `quality_water` para responder preguntas de negocio específicas.")

    st.markdown("---")
    st.subheader("Consulta N°1: Promedio de IRCA por Departamento")
    st.info("Objetivo: Obtener el nivel de riesgo promedio transformando el valor numérico a una categoría descriptiva, excluyendo los totales nacionales ('0').")

    # Mostrar el código SQL de la consulta
    sql_query = """
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
    WHERE muni_cod <> '0' 
    GROUP BY depto_nombre
    ORDER BY promedio_irca DESC;
    """
    with st.expander("Ver Código SQL Ejecutado"):
        st.code(sql_query, language="sql")

    try:
        # Ejecutar la consulta
        engine = get_engine()
        df_resultados = pd.read_sql(sql_query, con=engine)
        
        if df_resultados.empty:
            st.warning("La consulta no arrojó resultados.")
            return

        # Diseño en dos columnas: Tabla y Gráfico
        col1, col2 = st.columns([1, 1.5])

        with col1:
            st.markdown("**Resultados Tabulares**")
            st.dataframe(df_resultados, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**Visualización del Nivel de Riesgo Promedio**")
            
            # Mapeo de colores semánticos
            color_map = {
                'Inviable Sanitariamente': '#e41a1c',
                'Riesgo Alto': '#ff7f00',
                'Riesgo Medio': '#ffff33',
                'Riesgo Bajo': '#a6d854',
                'Sin Riesgo': '#4daf4a'
            }

            fig = px.bar(df_resultados, 
                         x='promedio_irca', 
                         y='depto_nombre', 
                         color='clasificacion_promedio',
                         orientation='h',
                         color_discrete_map=color_map,
                         labels={
                             'promedio_irca': 'IRCA General Promedio',
                             'depto_nombre': 'Departamento',
                             'clasificacion_promedio': 'Clasificación de Riesgo'
                         })
            # Ordenar para que el de mayor riesgo quede arriba
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error ejecutando la consulta SQL: {e}")

    st.markdown("---")
    st.subheader("Consulta N°2: Estacionalidad de la Calidad del Agua")
    st.info("Objetivo: Analizar la distribución de muestras por mes y nivel de riesgo en el año 2024.")

    sql_query_2_display = """
    SELECT 
        MONTHNAME(fecha_toma) AS mes, 
        nivel_riesgo, 
        COUNT(*) AS total_muestras
    FROM muestra
    WHERE YEAR(fecha_toma) = 2024 -- Refinamiento: Uso de función YEAR estándar de MySQL
    GROUP BY mes, nivel_riesgo
    ORDER BY FIELD(mes, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December');
    """
    
    with st.expander("Ver Código SQL Ejecutado"):
        st.code(sql_query_2_display, language="sql")

    try:
        # Adaptación para SQLite (Doble motor), la UI dice que corre código MySQL, 
        # pero bajo el capó resolvemos compatibilidad si el usuario está en modo stand-alone
        if engine.name == 'sqlite':
            sql_query_2_exec = """
            SELECT 
                CASE cast(strftime('%m', fecha_toma) as integer)
                    WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
                    WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June'
                    WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September'
                    WHEN 10 THEN 'October' WHEN 11 THEN 'November' WHEN 12 THEN 'December'
                END AS mes, 
                cast(strftime('%m', fecha_toma) as integer) AS mes_num,
                nivel_riesgo, 
                COUNT(*) AS total_muestras
            FROM muestra
            WHERE cast(strftime('%Y', fecha_toma) as integer) = 2024
            GROUP BY mes, mes_num, nivel_riesgo
            ORDER BY mes_num;
            """
        else:
            sql_query_2_exec = sql_query_2_display
            
        df_resultados_2 = pd.read_sql(sql_query_2_exec, con=engine)
        
        if df_resultados_2.empty:
            st.warning("La consulta no arrojó resultados para el año 2024.")
        else:
            # Diseño en dos columnas
            col1_2, col2_2 = st.columns([1, 1.5])

            with col1_2:
                st.markdown("**Resultados Tabulares**")
                # Limpiamos columna auxiliar de sqlite si existe antes de mostrar
                if 'mes_num' in df_resultados_2.columns:
                    df_resultados_2_show = df_resultados_2.drop(columns=['mes_num'])
                else:
                    df_resultados_2_show = df_resultados_2
                st.dataframe(df_resultados_2_show, use_container_width=True, hide_index=True)

            with col2_2:
                st.markdown("**Visualización de Estacionalidad de Riesgo**")
                
                fig2 = px.bar(df_resultados_2, 
                             x='mes', 
                             y='total_muestras', 
                             color='nivel_riesgo',
                             barmode='group',
                             labels={
                                 'mes': 'Mes',
                                 'total_muestras': 'Total Muestras',
                                 'nivel_riesgo': 'Nivel de Riesgo'
                             })
                
                # Respetar el orden natural cronológico de los meses en el eje X
                meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                fig2.update_xaxes(categoryorder='array', categoryarray=meses_orden)
                
                st.plotly_chart(fig2, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error ejecutando la consulta SQL N°2: {e}")

    st.markdown("---")
    st.subheader("Consulta N°3: Prestadores con Mayor Nivel de Alerta (Top 5)")
    st.info("Objetivo: Identificar los prestadores que requieren mayor vigilancia técnica basado en su promedio histórico de IRCA.")

    sql_query_3 = """
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
    """
    
    with st.expander("Ver Código SQL Ejecutado"):
        st.code(sql_query_3, language="sql")

    try:
        df_resultados_3 = pd.read_sql(sql_query_3, con=engine)
        
        if df_resultados_3.empty:
            st.warning("La consulta no arrojó resultados.")
        else:
            col1_3, col2_3 = st.columns([1, 1.5])

            with col1_3:
                st.markdown("**Resultados Tabulares**")
                st.dataframe(df_resultados_3, use_container_width=True, hide_index=True)

            with col2_3:
                st.markdown("**Visualización de Prestadores Críticos**")
                
                fig3 = px.bar(df_resultados_3, 
                             x='promedio_irca_prestador', 
                             y='nombre_prestador', 
                             color='promedio_irca_prestador',
                             orientation='h',
                             color_continuous_scale='Reds',
                             text='promedio_irca_prestador',
                             labels={
                                 'promedio_irca_prestador': 'IRCA Promedio',
                                 'nombre_prestador': 'Prestador',
                                 'total_muestras_tomadas': 'Muestras Evaluadas'
                             },
                             hover_data=['total_muestras_tomadas'])
                
                # Ordenar para que la barra más larga quede arriba
                fig3.update_layout(yaxis={'categoryorder':'total ascending'})
                fig3.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig3, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error ejecutando la consulta SQL N°3: {e}")
