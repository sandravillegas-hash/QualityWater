import streamlit as st
import pandas as pd
import plotly.express as px
from database import load_data

def render_dashboard_principal():
    st.title("💧 Dashboard de Calidad del Agua (IRCA Histórico)")
    st.markdown("Explorador de datos del Índice de Riesgo de la Calidad del Agua a nivel municipal y departamental.")

    # Cargar datos
    df = load_data()

    if df.empty:
        st.error("No se encontraron datos. Verifica la conexión a la base de datos o revisa si la tabla 'irca_historico' tiene registros.")
        return

    # --- PANEL LATERAL: FILTROS ---
    st.sidebar.header("🔍 Filtros Generales")

    # Filtro por Año
    años_disponibles = sorted(df['anio'].dropna().unique())
    selected_anios = st.sidebar.multiselect("Año(s)", options=años_disponibles, default=años_disponibles)

    # Filtro por Departamento
    deptos_disponibles = sorted(df['depto_nombre'].dropna().unique())
    selected_deptos = st.sidebar.multiselect("Departamento(s)", options=deptos_disponibles)

    # Filtrar datos por depto para el siguiente filtro
    df_filtered_muni = df[df['depto_nombre'].isin(selected_deptos)] if selected_deptos else df

    # Filtro por Municipio
    munis_disponibles = sorted(df_filtered_muni['muni_nombre'].dropna().unique())
    selected_munis = st.sidebar.multiselect("Municipio(s)", options=munis_disponibles)

    # Aplicar filtros
    df_filtered = df[df['anio'].isin(selected_anios)] if selected_anios else df
    if selected_deptos:
        df_filtered = df_filtered[df_filtered['depto_nombre'].isin(selected_deptos)]
    if selected_munis:
        df_filtered = df_filtered[df_filtered['muni_nombre'].isin(selected_munis)]

    st.sidebar.markdown(f"**Total registros filtrados:** {len(df_filtered)}")

    if df_filtered.empty:
        st.warning("No hay datos para la combinación de filtros seleccionada.")
        return

    # --- SECCIÓN: KPIs PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)

    promedio_general = df_filtered['irca_general'].mean()
    promedio_urbano = df_filtered['irca_urbano'].mean()
    promedio_rural = df_filtered['irca_rural'].mean()
    
    with col1:
        st.metric("Promedio IRCA General", f"{promedio_general:.2f}" if pd.notna(promedio_general) else "N/A")
    with col2:
        st.metric("Promedio IRCA Urbano", f"{promedio_urbano:.2f}" if pd.notna(promedio_urbano) else "N/A")
    with col3:
        st.metric("Promedio IRCA Rural", f"{promedio_rural:.2f}" if pd.notna(promedio_rural) else "N/A")
    with col4:
        st.metric("Mediciones Totales", len(df_filtered))

    st.markdown("---")

    # --- SECCIÓN: GRÁFICOS INTERACTIVOS ---
    
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Evolución Temporal del IRCA Promedio")
        df_trend = df_filtered.groupby('anio')[['irca_general', 'irca_urbano', 'irca_rural']].mean().reset_index()
        df_trend_melted = pd.melt(df_trend, id_vars=['anio'], value_vars=['irca_general', 'irca_urbano', 'irca_rural'], 
                                var_name='Tipo', value_name='IRCA')
        
        fig_trend = px.line(df_trend_melted, x='anio', y='IRCA', color='Tipo', markers=True,
                            labels={'anio': 'Año', 'IRCA': 'Valor Promedio', 'Tipo': 'Zona'},
                            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
        fig_trend.update_xaxes(type='category') 
        st.plotly_chart(fig_trend, use_container_width=True)

    with row1_col2:
        st.subheader("Distribución de Riesgo General")
        riesgo_counts = df_filtered['riesgo_general'].value_counts().reset_index()
        riesgo_counts.columns = ['Nivel de Riesgo', 'Cantidad']
        
        color_map = {
            'INVIABLE SANITARIAMENTE': 'red',
            'ALTO': 'orange',
            'MEDIO': 'yellow',
            'BAJO': 'lightgreen',
            'SIN RIESGO': 'green'
        }
        
        fig_pie = px.pie(riesgo_counts, values='Cantidad', names='Nivel de Riesgo', hole=0.4,
                            color='Nivel de Riesgo', color_discrete_map=color_map)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Top 10 Municipios con Mayor IRCA General")
        df_muni_avg = df_filtered.groupby(['muni_nombre', 'depto_nombre'])['irca_general'].mean().reset_index()
        df_muni_top10 = df_muni_avg.sort_values(by='irca_general', ascending=False).head(10)
        
        fig_bar = px.bar(df_muni_top10, x='irca_general', y='muni_nombre', color='depto_nombre',
                            orientation='h', labels={'irca_general': 'IRCA General Promedio', 'muni_nombre': 'Municipio', 'depto_nombre': 'Departamento'})
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with row2_col2:
        st.subheader("Comparativa IRCA Urbano vs Rural")
        df_scatter = df_filtered.dropna(subset=['irca_urbano', 'irca_rural'])
        color_map_scatter = {
            'INVIABLE SANITARIAMENTE': 'red', 'ALTO': 'orange', 'MEDIO': 'yellow', 
            'BAJO': 'lightgreen', 'SIN RIESGO': 'green'
        }
        fig_scatter = px.scatter(df_scatter, x='irca_urbano', y='irca_rural', color='riesgo_general', hover_data=['muni_nombre', 'anio'],
                                    labels={'irca_urbano': 'IRCA Urbano', 'irca_rural': 'IRCA Rural'},
                                    color_discrete_map=color_map_scatter)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("Ver Datos Tabulares"):
        st.dataframe(df_filtered)
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar datos filtrados como CSV",
            data=csv,
            file_name='datos_irca_filtrados.csv',
            mime='text/csv',
        )
