import streamlit as st
import importlib.util

# Configuración inicial de la página (DEBE estar primero)
st.set_page_config(
    page_title="Quality Water Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados globales
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #1f77b4; }
    .metric-label { font-size: 14px; font-weight: 600; color: #555; }
</style>
""", unsafe_allow_html=True)

# Importar las páginas modulares
from vistas.dashboard import render_dashboard_principal
from vistas.consultas import render_consultas_analiticas
from vistas.sql_interactivo import render_sql_interactivo

# --- ENRUTAMIENTO MULTIPÁGINA (Sidebar) ---
st.sidebar.title("Desarrollo Estudiantes Talento Tech")
st.sidebar.markdown("---")

ruta_opcion = st.sidebar.radio(
    "Selecciona una vista:",
    ("Dashboard Principal (IRCA)", "Consultas Analíticas (SQL)", "Laboratorio SQL Interactivo")
)

st.sidebar.markdown("---")
st.sidebar.info("Proyecto Exploratorio de Calidad del Agua. Con soporte dual para MySQL y SQLite local.")

# Renderizar la vista según la opción seleccionada
if ruta_opcion == "Dashboard Principal (IRCA)":
    render_dashboard_principal()
elif ruta_opcion == "Consultas Analíticas (SQL)":
    render_consultas_analiticas()
elif ruta_opcion == "Laboratorio SQL Interactivo":
    render_sql_interactivo()
