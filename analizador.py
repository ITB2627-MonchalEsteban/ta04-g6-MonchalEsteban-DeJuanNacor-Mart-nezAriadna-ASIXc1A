import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configuración de página de la app
st.set_page_config(page_title="Analizador de Incidencias XML", layout="wide")
st.title("📊 Analizador y Filtro de Incidencias XML")

# 1. Cargar archivo XML
uploaded_file = st.sidebar.file_uploader("Carga tu archivo XML", type=["xml"])

def parse_xml(file):
    """Parsea el archivo XML y convierte sus nodos en una lista de diccionarios."""
    tree = ET.parse(file)
    root = tree.getroot()
    
    records = []
    # Busca dinámicamente los elementos hijos (incidencias)
    for child in root:
        data = {}
        for elem in child:
            data[elem.tag] = elem.text
        records.append(data)
    
    return pd.DataFrame(records)

if uploaded_file is not None:
    df = parse_xml(uploaded_file)
    
    # Inicializar estado para evaluación manual
    if 'evaluaciones' not in st.session_state or len(st.session_state.evaluaciones) != len(df):
        st.session_state.evaluaciones = ['Sin clasificar'] * len(df)
        
    df['Evaluación'] = st.session_state.evaluaciones

    st.subheader("📋 Datos cargados del XML")
    st.dataframe(df, use_container_width=True)

    # -------------------------------------------------------------
    # 2. FILTRADO AUTOMÁTICO
    # -------------------------------------------------------------
    st.sidebar.header("🤖 Filtro Automático")
    columna_filtro = st.sidebar.selectbox("Selecciona la columna para filtrar", options=df.columns)
    palabra_clave = st.sidebar.text_input("Palabra clave / Valor (ej. 'Resuelto', 'Baja', 'OK')")
    
    if st.sidebar.button("Aplicar Filtro Automático"):
        if palabra_clave:
            mask = df[columna_filtro].astype(str).str.contains(palabra_clave, case=False, na=False)
            df.loc[mask, 'Evaluación'] = 'Buena'
            df.loc[~mask, 'Evaluación'] = 'Mala'
            st.session_state.evaluaciones = df['Evaluación'].tolist()
            st.sidebar.success(f"Filtro aplicado sobre '{columna_filtro}' con valor '{palabra_clave}'")

    # -------------------------------------------------------------
    # 3. FILTRADO MANUAL
    # -------------------------------------------------------------
    st.subheader("✏️ Edición / Filtrado Manual de Incidencias")
    idx = st.number_input("Selecciona el número de índice de la incidencia", min_value=0, max_value=len(df)-1, step=1)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Detalle de la incidencia seleccionada:**")
        st.json(df.iloc[idx].drop('Evaluación').to_dict())
        
    with col2:
        if st.button("Marcar como Buena 👍"):
            st.session_state.evaluaciones[idx] = 'Buena'
            st.rerun()
            
    with col3:
        if st.button("Marcar como Mala 👎"):
            st.session_state.evaluaciones[idx] = 'Mala'
            st.rerun()

    # Actualizamos DataFrame con las decisiones del estado
    df['Evaluación'] = st.session_state.evaluaciones

    # -------------------------------------------------------------
    # 4. ESTADÍSTICAS Y DIAGRAMA DE BARRAS
    # -------------------------------------------------------------
    st.markdown("---")
    st.subheader("📈 Estadísticas y Métricas")

    conteo = df['Evaluación'].value_counts()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidencias", len(df))
    c2.metric("Buenas 👍", conteo.get('Buena', 0))
    c3.metric("Malas 👎", conteo.get('Mala', 0))

    # Gráfico de barras
    fig, ax = plt.subplots(figsize=(7, 4))
    categorias = ['Buena', 'Mala', 'Sin clasificar']
    valores = [conteo.get(cat, 0) for cat in categorias]
    colores = ['#4CAF50', '#F44336', '#9E9E9E']

    ax.bar(categorias, valores, color=colores, width=0.5)
    ax.set_ylabel("Cantidad de Incidencias")
    ax.set_title("Distribución de Incidencias (Buenas vs Malas)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)

else:
    st.info("👆 Carga un archivo XML desde el panel lateral para empezar.")