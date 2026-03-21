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

    # Estandarizar nivel de riesgo para igualar los diccionarios de color (Evita fallos de mayúsculas o 'Riesgo alto' vs 'ALTO')
    def _clean_risk(val):
        if pd.isna(val): return val
        v = str(val).upper()
        if 'INVIABLE' in v: return 'INVIABLE SANITARIAMENTE'
        if 'ALTO' in v: return 'ALTO'
        if 'MEDIO' in v: return 'MEDIO'
        if 'BAJO' in v: return 'BAJO'
        if 'SIN' in v: return 'SIN RIESGO'
        return v
    
    df_filtered = df_filtered.copy()
    df_filtered['riesgo_general'] = df_filtered['riesgo_general'].apply(_clean_risk)

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
            'INVIABLE SANITARIAMENTE': '#d73027',  # Rojo intenso
            'ALTO': '#fc8d59',                     # Naranja
            'MEDIO': '#fee08b',                    # Amarillo pálido
            'BAJO': '#d9ef8b',                     # Verde claro
            'SIN RIESGO': '#1a9850'                # Verde fuerte
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
            'INVIABLE SANITARIAMENTE': '#d73027', 
            'ALTO': '#fc8d59', 
            'MEDIO': '#fee08b', 
            'BAJO': '#d9ef8b', 
            'SIN RIESGO': '#1a9850'
        }
        fig_scatter = px.scatter(df_scatter, x='irca_urbano', y='irca_rural', color='riesgo_general', hover_data=['muni_nombre', 'anio'],
                                    labels={'irca_urbano': 'IRCA Urbano', 'irca_rural': 'IRCA Rural'},
                                    color_discrete_map=color_map_scatter)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.subheader("Mapa Departamental de IRCA General (Medición 2024)")
    st.info("Vista geográfica del IRCA departamental tomando el registro consolidado oficial (donde el Municipio es 'TODOS').")

    # Filtrar solo registros departamentales ('TODOS' o código '0')
    df_mapa = df_filtered[(df_filtered['muni_nombre'].str.upper() == 'TODOS') | (df_filtered['muni_cod'] == '0')]
    
    if df_mapa.empty:
        st.warning("No hay datos departamentales agregados ('TODOS') para esta selección de filtros.")
    else:
        # Promediar si hay múltiples años seleccionados a la vez
        df_mapa_avg = df_mapa.groupby('depto_nombre')['irca_general'].mean().reset_index()

        # Coordenadas estáticas predefinidas (Aproximadas) y población estimada de proyecciones recientes del DANE para el mapeo geo-proporcional
        colombia_coords = {
            'Amazonas': {'lat': -1.442, 'lon': -71.572, 'pob': 82000, 'nombre_limpio': 'Amazonas'},
            'Antioquia': {'lat': 6.550, 'lon': -75.344, 'pob': 6882000, 'nombre_limpio': 'Antioquia'},
            'Arauca': {'lat': 6.643, 'lon': -70.970, 'pob': 304000, 'nombre_limpio': 'Arauca'},
            'Archipielago de San Andrs, Providencia y Santa Catalina': {'lat': 12.573, 'lon': -81.700, 'pob': 65000, 'nombre_limpio': 'San Andrés y Providencia'},
            'Atlntico': {'lat': 10.655, 'lon': -74.965, 'pob': 2772000, 'nombre_limpio': 'Atlántico'},
            'Bogot, D.C.': {'lat': 4.609, 'lon': -74.081, 'pob': 7901000, 'nombre_limpio': 'Bogotá, D.C.'},
            'Bolvar': {'lat': 8.861, 'lon': -74.332, 'pob': 2236000, 'nombre_limpio': 'Bolívar'},
            'Boyac': {'lat': 5.518, 'lon': -72.930, 'pob': 1255000, 'nombre_limpio': 'Boyacá'},
            'Crdoba': {'lat': 8.324, 'lon': -75.688, 'pob': 1845000, 'nombre_limpio': 'Córdoba'},
            'Caldas': {'lat': 5.297, 'lon': -75.405, 'pob': 1032000, 'nombre_limpio': 'Caldas'},
            'Caquet': {'lat': 1.050, 'lon': -73.695, 'pob': 419000, 'nombre_limpio': 'Caquetá'},
            'Casanare': {'lat': 5.385, 'lon': -71.693, 'pob': 442000, 'nombre_limpio': 'Casanare'},
            'Cauca': {'lat': 2.404, 'lon': -76.626, 'pob': 1515000, 'nombre_limpio': 'Cauca'},
            'Cesar': {'lat': 9.293, 'lon': -73.456, 'pob': 1341000, 'nombre_limpio': 'Cesar'},
            'Choc': {'lat': 5.578, 'lon': -76.819, 'pob': 549000, 'nombre_limpio': 'Chocó'},
            'Cundinamarca': {'lat': 5.0, 'lon': -74.0, 'pob': 3442000, 'nombre_limpio': 'Cundinamarca'},
            'Guaina': {'lat': 2.684, 'lon': -68.995, 'pob': 52000, 'nombre_limpio': 'Guainía'},
            'Guaviare': {'lat': 2.054, 'lon': -72.015, 'pob': 89000, 'nombre_limpio': 'Guaviare'},
            'Huila': {'lat': 2.531, 'lon': -75.467, 'pob': 1140000, 'nombre_limpio': 'Huila'},
            'La Guajira': {'lat': 11.455, 'lon': -72.580, 'pob': 1015000, 'nombre_limpio': 'La Guajira'},
            'Magdalena': {'lat': 10.375, 'lon': -74.240, 'pob': 1463000, 'nombre_limpio': 'Magdalena'},
            'Meta': {'lat': 3.328, 'lon': -73.048, 'pob': 1080000, 'nombre_limpio': 'Meta'},
            'Nario': {'lat': 1.488, 'lon': -77.830, 'pob': 1629000, 'nombre_limpio': 'Nariño'},
            'Norte de Santander': {'lat': 8.239, 'lon': -73.013, 'pob': 1650000, 'nombre_limpio': 'Norte de Santander'},
            'Putumayo': {'lat': 0.612, 'lon': -76.225, 'pob': 369000, 'nombre_limpio': 'Putumayo'},
            'Quindo': {'lat': 4.498, 'lon': -75.666, 'pob': 562000, 'nombre_limpio': 'Quindío'},
            'Risaralda': {'lat': 5.093, 'lon': -75.879, 'pob': 978000, 'nombre_limpio': 'Risaralda'},
            'Santander': {'lat': 6.940, 'lon': -73.238, 'pob': 2323000, 'nombre_limpio': 'Santander'},
            'Sucre': {'lat': 8.924, 'lon': -75.110, 'pob': 968000, 'nombre_limpio': 'Sucre'},
            'Tolima': {'lat': 3.992, 'lon': -75.163, 'pob': 1346000, 'nombre_limpio': 'Tolima'},
            'Valle del Cauca': {'lat': 3.843, 'lon': -76.536, 'pob': 4583000, 'nombre_limpio': 'Valle del Cauca'},
            'Vichada': {'lat': 4.542, 'lon': -69.255, 'pob': 115000, 'nombre_limpio': 'Vichada'},
            'Vaups': {'lat': 0.814, 'lon': -70.473, 'pob': 47000, 'nombre_limpio': 'Vaupés'}
        }
        
        # Mapear coordenadas, población exacta y nombre limpio al DataFrame
        df_mapa_avg['lat'] = df_mapa_avg['depto_nombre'].map(lambda x: colombia_coords.get(x, {}).get('lat', 4.57))
        df_mapa_avg['lon'] = df_mapa_avg['depto_nombre'].map(lambda x: colombia_coords.get(x, {}).get('lon', -74.29))
        df_mapa_avg['Poblacion Estimada'] = df_mapa_avg['depto_nombre'].map(lambda x: colombia_coords.get(x, {}).get('pob', 500000))
        df_mapa_avg['Departamento'] = df_mapa_avg['depto_nombre'].map(lambda x: colombia_coords.get(x, {}).get('nombre_limpio', x))
        
        # Escalar tamaños (Raíz cuadrada) para que los extremos (Antioquia vs Vaupés) sean visibles sin saturar el mapa
        df_mapa_avg['Escala Burbuja'] = df_mapa_avg['Poblacion Estimada'] ** 0.5
        
        # Graficar mapa de dispersión geolocalizado usando el nombre corregido
        fig_map = px.scatter_mapbox(df_mapa_avg, lat="lat", lon="lon", hover_name="Departamento", 
                                    hover_data={"lat": False, "lon": False, "Escala Burbuja": False, "depto_nombre": False, "irca_general": ":.2f", "Poblacion Estimada": ":,"},
                                    color="irca_general", size="Escala Burbuja",
                                    color_continuous_scale=["green", "yellow", "orange", "red"], size_max=30,
                                    zoom=4.2, center={"lat": 4.5709, "lon": -74.2973},
                                    mapbox_style="carto-positron",
                                    labels={'irca_general': 'IRCA Dept.', 'Poblacion Estimada': 'Población'})
        
        fig_map.update_layout(margin={"r":0,"t":10,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    with st.expander("Ver Datos Tabulares"):
        st.dataframe(df_filtered)
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar datos filtrados como CSV",
            data=csv,
            file_name='datos_irca_filtrados.csv',
            mime='text/csv',
        )
