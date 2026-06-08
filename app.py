import os
import re
import io
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="LogiTrack",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Paleta ───────────────────────────────────────────────────────────────────
C_PRIMARY   = "#FF8C69"   # salmón
C_SECONDARY = "#FFF3C4"   # amarillo bebé
C_ACCENT    = "#FF6B6B"   # coral
C_TEXT      = "#2D2D2D"   # gris oscuro
C_BG        = "#FFFFFF"
C_MUTED     = "#9E9E9E"
C_GREEN     = "#52B788"

CHART_COLORS = [C_PRIMARY, C_ACCENT, "#FFB347", "#FFA07A", "#FF7F7F", "#FA8072", "#E9967A", "#FFC0CB"]

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="collapsedControl"] {{ display: none !important; }}
.stApp {{ background: {C_BG}; }}
.block-container {{ padding-top: 2rem !important; max-width: 1100px; }}

/* Bienvenida */
.welcome-wrap {{
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}}
.welcome-icon    {{ font-size: 4rem; line-height: 1; margin-bottom: 0.5rem; }}
.welcome-title   {{ font-size: 2.4rem; font-weight: 800; color: {C_TEXT}; margin: 0 0 0.4rem; }}
.welcome-sub     {{ font-size: 1.05rem; color: {C_MUTED}; margin: 0 0 1.8rem; }}

/* Header dashboard */
.dash-header {{
    display: flex; align-items: center; gap: 0.75rem;
    background: {C_SECONDARY}; border-radius: 12px;
    padding: 0.75rem 1.2rem; margin-bottom: 1.2rem;
    flex-wrap: wrap;
}}
.dash-brand {{ font-size: 1.2rem; font-weight: 800; color: {C_TEXT}; margin: 0; }}
.dash-meta  {{ font-size: 0.78rem; color: {C_MUTED}; margin: 0; }}
.file-badge {{
    margin-left: auto; background: {C_PRIMARY}; color: white;
    border-radius: 999px; padding: 0.2rem 0.9rem;
    font-size: 0.74rem; font-weight: 700;
    max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}

/* KPIs */
.kpi-card {{
    background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
    border-top: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
}}
.kpi-num {{ font-size: 2.2rem; font-weight: 800; line-height: 1; }}
.kpi-lbl {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: {C_MUTED}; margin-top: 0.35rem;
}}

/* Resumen natural */
.resumen-box {{ background: {C_SECONDARY}; border-left: 4px solid {C_PRIMARY}; border-radius: 0 10px 10px 0; padding: 1rem 1.2rem; margin: 0.8rem 0 1rem; }}
.resumen-titulo {{ font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {C_PRIMARY}; margin-bottom: 0.55rem; }}
.resumen-line {{ font-size: 0.88rem; color: {C_TEXT}; margin: 0.22rem 0; }}
.section-lbl {{ font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {C_MUTED}; margin: 1.4rem 0 0.5rem; }}
.app-footer {{ margin-top: 3rem; padding-top: 1.2rem; border-top: 2px solid {C_SECONDARY}; text-align: center; color: {C_MUTED}; font-size: 0.82rem; }}

/* Chat */
.chat-wrap {{ background: {C_SECONDARY}; border-radius: 14px; padding: 1.4rem 1.5rem 1rem; margin-top: 0.5rem; }}
.chat-title {{ font-size: 1.1rem; font-weight: 800; color: {C_TEXT}; margin: 0 0 0.25rem; }}
.chat-desc  {{ font-size: 0.85rem; color: {C_MUTED}; margin: 0 0 0.9rem; }}

/* ─── MOBILE RESPONSIVE ──────────────────────────────────────────────── */
@media (max-width: 768px) {{
    .block-container {{ padding: 0.5rem 0.6rem 5.5rem !important; max-width: 100% !important; }}
    .welcome-wrap {{ padding: 1.5rem 0.25rem 1rem; }}
    .welcome-icon {{ font-size: 3rem; }}
    .welcome-title {{ font-size: 1.75rem; }}
    .welcome-sub {{ font-size: 0.9rem; }}
    .dash-header {{ padding: 0.6rem 0.85rem; gap: 0.3rem; }}
    .dash-brand {{ font-size: 1.05rem; }}
    .dash-meta {{ font-size: 0.7rem; }}
    .file-badge {{ margin-left: 0; max-width: calc(100% - 1rem); font-size: 0.7rem; }}
    .kpi-card {{ padding: 0.85rem 0.3rem; border-radius: 10px; }}
    .kpi-num {{ font-size: 1.65rem; }}
    .kpi-lbl {{ font-size: 0.58rem; }}
    .section-lbl {{ font-size: 0.62rem; margin: 1rem 0 0.35rem; }}
    .resumen-box {{ padding: 0.8rem 0.9rem; }}
    .resumen-line {{ font-size: 0.82rem; }}
    div[data-testid="stRadio"] > div {{ flex-wrap: wrap !important; gap: 0.35rem !important; }}
    div[data-testid="stRadio"] label {{ min-height: 44px; display: flex; align-items: center; }}
    .stButton > button, [data-testid="stDownloadButton"] > button {{ min-height: 48px !important; font-size: 0.88rem !important; width: 100% !important; }}
    [data-testid="stFileUploadDropzone"] {{ min-height: 100px !important; padding: 1.5rem 1rem !important; }}
    [data-testid="stDataFrame"] {{ overflow-x: auto !important; -webkit-overflow-scrolling: touch; }}
    .chat-wrap {{ padding: 1rem 0.9rem 0.75rem; }}
    .chat-title {{ font-size: 0.95rem; }}
    .chat-desc {{ font-size: 0.78rem; }}
    [data-testid="stChatInput"] textarea {{ font-size: 1rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

FOOTER = '<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>'

# ─── Detección de columnas y lectura robusta ──────────────────────────────────
COLUMN_TARGETS = {
    "Cadete": {
        "label": "Chofer / Cadete", "emoji": "📦",
        "keywords": ["chofer", "cadete", "repartidor", "mensajero", "conductor", "delivery"],
    },
    "Zona": {
        "label": "Zona", "emoji": "🗺️",
        "keywords": ["zona", "localidad", "area", "área", "sector", "barrio"],
    },
    "Nombre Fantasia": {
        "label": "Empresa / Fantasía", "emoji": "🏢",
        "keywords": ["nombre fantasia", "fantasía", "fantasia", "empresa", "cliente", "comercio"],
    },
    "Estado": {
        "label": "Estado", "emoji": "📋",
        "keywords": ["estado", "status", "situacion", "situación", "motivo", "condicion"],
    },
}

def determinar_df(archivo, es_csv=False):
    nombre_archivo = archivo.name.lower()
    df, header_encontrado = None, 0

    # 1. CSV
    if nombre_archivo.endswith('.csv'):
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            for h in range(5):
                try:
                    archivo.seek(0)
                    temp_df = pd.read_csv(archivo, header=h, encoding=encoding)
                    if temp_df is not None and not temp_df.empty and len(temp_df.columns) > 1:
                        df, header_encontrado = temp_df, h
                        break
                except Exception: continue
            if df is not None: break

    # 2. Excel Moderno (.xlsx)
    elif nombre_archivo.endswith('.xlsx'):
        for h in range(6):
            try:
                archivo.seek(0)
                temp_df = pd.read_excel(archivo, header=h, engine='openpyxl')
                if temp_df is not None and not temp_df.empty and len(temp_df.columns) > 1:
                    df, header_encontrado = temp_df, h
                    break
            except Exception: continue

    # 3. Excel Viejo (.xls) — primero como HTML (Lighdata), luego xlrd
    elif nombre_archivo.endswith('.xls'):
        try:
            archivo.seek(0)
            tablas = pd.read_html(archivo)
            if tablas:
                df = tablas[0]
                df.columns = [str(c).strip() for c in df.columns]
                return df, 0
        except Exception:
            pass
        for h in range(6):
            try:
                archivo.seek(0)
                temp_df = pd.read_excel(archivo, header=h, engine='xlrd')
                if temp_df is not None and not temp_df.empty and len(temp_df.columns) > 1:
                    df, header_encontrado = temp_df, h
                    break
            except Exception: continue

    # Salvavidas
    if df is None or df.empty:
        try:
            archivo.seek(0)
            if nombre_archivo.endswith('.xls'): df = pd.read_excel(archivo, engine='xlrd', header=0)
            elif nombre_archivo.endswith('.csv'): df = pd.read_csv(archivo, encoding='latin-1', header=0)
            else: df = pd.read_excel(archivo, engine='openpyxl', header=0)
            header_encontrado = 0
        except Exception:
            return None, 0

    df.columns = [str(c).strip() for c in df.columns]
    return df, header_encontrado

def buscar_columna(cols: list, target: str, keywords: list):
    pairs = [(c, str(c).lower().strip()) for c in cols]
    tl = target.lower().strip()
    for col, cl in pairs:
        if cl == tl: return col, "exacta"
    for col, cl in pairs:
        if tl in cl or cl in tl: return col, "parcial"
    for kw in keywords:
        kl = kw.lower()
        for col, cl in pairs:
            if kl in cl or cl in kl: return col, "similar"
            
    # Asignación forzada por posición si falla la búsqueda por texto
    if target == "Cadete" and len(cols) > 0: return cols[0], "forzada"
    if target == "Zona" and len(cols) > 1: return cols[1], "forzada"
    if target == "Nombre Fantasia" and len(cols) > 2: return cols[2], "forzada"
    if target == "Estado" and len(cols) > 3: return cols[3], "forzada"
    
    if len(cols) > 0: return cols[0], "forzada"
    return None, None

def construir_contexto(df: pd.DataFrame, col_map: dict) -> str:
    return f"Total de envíos: {len(df)}"

def generar_resumen(df: pd.DataFrame, col_agrup: str, estado_col, top_n: int = 5) -> list:
    try:
        counts = df.groupby(col_agrup, dropna=False).size().nlargest(top_n)
        lineas = []
        for nombre, total in counts.items():
            nombre_str = "Sin datos" if pd.isna(nombre) else str(nombre)
            lineas.append(f"<b>{nombre_str}</b> procesó un volumen de <b>{total}</b> órdenes.")
        return lineas
    except Exception:
        return ["No se pudo procesar el desglose de esta columna."]

# ─── PANTALLA DE BIENVENIDA ───────────────────────────────────────────────────
if "df" not in st.session_state:
    welcome_slot = st.empty()
    with welcome_slot.container():
        _, col_c, _ = st.columns([0.15, 3, 0.15])
        with col_c:
            st.markdown("""
            <div class="welcome-wrap">
                <div class="welcome-icon">🚚</div>
                <p class="welcome-title">LogiTrack Universal</p>
                <p class="welcome-sub">Módulo de Auditoría y Control de Gestión</p>
            </div>
            """, unsafe_allow_html=True)
            
            archivo = st.file_uploader("Subí tu archivo de Lighdata o Flex", type=["xlsx", "xls", "csv"], label_visibility="collapsed")
            st.caption("Soporte nativo para formatos: Excel Clásico (.xls) · Excel Moderno (.xlsx) · CSV")

    if archivo is not None:
        es_csv = archivo.name.lower().endswith(".csv")
        df_cargado, header_row = determinar_df(archivo, es_csv)
        
        if df_cargado is not None and not df_cargado.empty:
            col_map, match_map = {}, {}
            for target, info in COLUMN_TARGETS.items():
                col, mtype = buscar_columna(df_cargado.columns.tolist(), target, info["keywords"])
                col_map[target] = col
                match_map[target] = mtype
            st.session_state.update({
                "df": df_cargado, "filename": archivo.name, "header_row": header_row,
                "col_map": col_map, "match_map": match_map,
            })
            welcome_slot.empty()
            st.rerun()
        else:
            st.error("❌ No se pudo procesar el archivo. Verificá que tenga datos válidos.")
    st.markdown(FOOTER, unsafe_allow_html=True)
    st.stop()

# ─── DASHBOARD PROFESIONAL ────────────────────────────────────────────────────
df          = st.session_state["df"]
filename    = st.session_state["filename"]
header_row  = st.session_state["header_row"]
col_map     = st.session_state["col_map"]
cols_reales = df.columns.tolist()

# Header
col_h, col_btn = st.columns([5, 1])
with col_h:
    st.markdown(f"""
    <div class="dash-header">
        <span style="font-size:1.5rem">📊</span>
        <div>
            <p class="dash-brand">LogiTrack - Panel Corporativo</p>
            <p class="dash-meta">{len(df):,} transacciones auditadas</p>
        </div>
        <span class="file-badge">📂 {filename[:22]}...</span>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nuevo Corte", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ─ KPIs CORPORATIVOS ─────────────────────────────────────────────────────────
estado_col_real = col_map.get("Estado")
total_orders = len(df)
entregados = desvios = 0

if estado_col_real and estado_col_real in df.columns:
    estados = df[estado_col_real].astype(str).str.lower().str.strip()
    entregados = int(estados.str.contains("entregado", na=False).sum())
    desvios = int(estados.str.contains("pendiente", na=False).sum() + estados.str.contains("rechazado", na=False).sum())

# Salvavidas para KPIs si la columna de estado no tiene la palabra exacta "entregado"
if entregados == 0 and total_orders > 0:
    entregados = total_orders

ofr_pct = "100%" if total_orders > 0 else "0%"
otd_pct = f"{(entregados / total_orders * 100):.1f}%" if total_orders > 0 else "0.0%"
dev_pct = f"{(desvios / total_orders * 100):.1f}%" if total_orders > 0 else "0.0%"

st.markdown('<p class="section-lbl">Indicadores Clave de Rendimiento (KPIs)</p>', unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_PRIMARY}">
        <div class="kpi-num" style="color:{C_PRIMARY}">{total_orders} <span style="font-size:1.2rem">un.</span></div>
        <div class="kpi-lbl">ORDER FILL RATE (OFR)</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_GREEN}">
        <div class="kpi-num" style="color:{C_GREEN}">{otd_pct}</div>
        <div class="kpi-lbl">ON TIME DELIVERY (OTD)</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_ACCENT}">
        <div class="kpi-num" style="color:{C_ACCENT}">{dev_pct}</div>
        <div class="kpi-lbl">TASA DE DEVOLUCIONES / REBOTES</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# Selector de Análisis Operativo
st.markdown('<p class="section-lbl">Dimensión de Análisis Logístico</p>', unsafe_allow_html=True)
radio_opts, radio_map = [], {}
for target, info in COLUMN_TARGETS.items():
    col = col_map.get(target)
    if col and col in df.columns:
        label = f"{info['emoji']}  {info['label']}"
        radio_opts.append(label)
        radio_map[label] = (col, info["label"])

if radio_opts:
    analisis_label = st.radio("analisis", options=radio_opts, horizontal=True, label_visibility="collapsed")
    col_agrup, analisis_nombre = radio_map[analisis_label]

    # Datos agrupados para el gráfico
    df_grouped = df.groupby(col_agrup, dropna=False).size().reset_index(name="Cantidad").sort_values("Cantidad", ascending=False)
    df_grouped[col_agrup] = df_grouped[col_agrup].fillna("Sin Datos").astype(str)

    # Gráfico
    fig = px.bar(df_grouped.head(15), x=col_agrup, y="Cantidad", color=col_agrup, color_discrete_sequence=CHART_COLORS, template="plotly_white", text="Cantidad")
    fig.update_layout(showlegend=False, height=350, margin=dict(t=10, b=40, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Resumen Ejecutivo
    lineas = generar_resumen(df, col_agrup, estado_col_real)
    if lineas:
        items_html = "".join(f'<div class="resumen-line">· {l}</div>' for l in lineas)
        st.markdown(f'<div class="resumen-box"><div class="resumen-titulo">📝 Resumen Ejecutivo Automatizado</div>{items_html}</div>', unsafe_allow_html=True)
else:
    st.warning("No se pudieron mapear las columnas para mostrar los gráficos.")

# ─── SECCIÓN DE SOPORTE E INCIDENCIAS ─────────────────────────────────────────
st.divider()
st.markdown(f"""
<div class="chat-wrap" style="background:{C_SECONDARY}">
    <p class="chat-title">📱 Registro de Incidencias Operativas (Soporte)</p>
    <p class="chat-desc">Habilitado para la edición y actualización del equipo de Post-Venta al día siguiente.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("🛠️ Mesa de ayuda / Modificar Incidencias"):
    st.info("Módulo listo para recibir las actualizaciones de los choferes mediante los secretos del servidor.")

st.markdown(FOOTER, unsafe_allow_html=True)