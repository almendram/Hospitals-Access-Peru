# app.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import streamlit.components.v1 as components

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Acceso a Hospitales en Perú", layout="wide")

# Paths
BASE_DIR = Path().resolve()
DATA_DIR = BASE_DIR / "data"
SHAPE_DIR = DATA_DIR / "shape_file"
OUT_DIR = BASE_DIR / "outputs"

# Archivos
POP_FILE = SHAPE_DIR / "CCPP_IGN100K.shp"
DISTRICTS_FILE = SHAPE_DIR / "DISTRITOS.shp"
HOSP_CSV = DATA_DIR / "hospitales.csv"

# CARGA DE DATOS
@st.cache_data
def cargar_datos():
    hospitales = pd.read_csv(HOSP_CSV, dtype=str)
    distritos = gpd.read_file(DISTRICTS_FILE)
    return hospitales, distritos

hospitales, distritos = cargar_datos()

# TABS PRINCIPALES
tab1, tab2, tab3 = st.tabs([
    "🗂️ Descripción de los datos",
    "📊 Mapas estáticos y análisis departamental",
    "🗺️ Mapas dinámicos"
])


# TAB 1: DESCRIPCIÓN DE LOS DATOS
with tab1:
    st.title("🗂️ Descripción de los datos")

    st.markdown("""
    **Unidad de análisis:** Hospitales públicos operativos en el Perú.  
    **Fuentes de datos:** MINSA – IPRESS (subconjunto operativo), Centros Poblados (IGN).  
    **Reglas de filtrado:**  
    - Solo hospitales operativos  
    - Latitud y longitud válidas  
    """)

    st.subheader("Vista previa de los datos de hospitales")
    st.dataframe(hospitales.head())


# TAB 2: MAPAS ESTÁTICOS + ANÁLISIS
with tab2:
    st.title("📊 Mapas estáticos y análisis departamental")

    if "DEPARTAMEN" in hospitales.columns:
        resumen = hospitales.groupby("DEPARTAMEN").size().reset_index(name="N_Hospitales")

        st.subheader("Tabla resumen por departamento")
        st.dataframe(resumen)

        st.subheader("Gráfico de barras")
        fig, ax = plt.subplots(figsize=(10, 5))
        resumen.sort_values("N_Hospitales", ascending=False).plot.bar(
            x="DEPARTAMEN", y="N_Hospitales", ax=ax, legend=False, color="skyblue"
        )
        plt.xticks(rotation=90)
        st.pyplot(fig)

    st.subheader("Mapa estático (GeoPandas)")
    fig, ax = plt.subplots(figsize=(6, 6))
    distritos.plot(ax=ax, edgecolor="black", facecolor="none")
    if "ESTE" in hospitales.columns and "NORTE" in hospitales.columns:
        plt.scatter(pd.to_numeric(hospitales["ESTE"], errors="coerce"),
                    pd.to_numeric(hospitales["NORTE"], errors="coerce"),
                    s=5, c="red")
    st.pyplot(fig)


# TAB 3: MAPAS DINÁMICOS (FOLIUM)
with tab3:
    st.title("🗺️ Mapas dinámicos")

    st.subheader("Coropleta Nacional con hospitales")
    mapa_nacional = OUT_DIR / "mapa_hospitales_distritos.html"
    if mapa_nacional.exists():
        with open(mapa_nacional, "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=600)
    else:
        st.warning("⚠️ No se encontró el archivo 'mapa_hospitales_distritos.html'. Genera primero el mapa con tu script.")

    st.subheader("Mapas de proximidad (Lima y Loreto)")
    mapa_proximidad = OUT_DIR / "proximity_combinado.html"
    if mapa_proximidad.exists():
        with open(mapa_proximidad, "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=600)
    else:
        st.warning("⚠️ No se encontró el archivo 'proximity_combinado.html'. Genera primero el mapa con tu script.")
