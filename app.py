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
.welcome-steps {{
    display: inline-flex; flex-direction: column; gap: 0.8rem;
    background: {C_SECONDARY}; border-radius: 16px; padding: 1.4rem 1.8rem;
    text-align: left; width: 100%; margin-bottom: 1.8rem; box-sizing: border-box;
}}
.welcome-step  {{ display: flex; align-items: flex-start; gap: 0.75rem;
                  color: {C_TEXT}; font-size: 0.95rem; line-height: 1.4; }}
.step-num {{
    background: {C_PRIMARY}; color: white; border-radius: 999px;
    min-width: 1.65rem; height: 1.65rem;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.78rem; flex-shrink: 0; margin-top: 0.05rem;
}}

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

/* Top 5 — scroll container */
.top5-scroll {{
    display: flex; gap: 0.75rem; overflow-x: auto; padding-bottom: 0.5rem;
    -webkit-overflow-scrolling: touch; scrollbar-width: none; align-items: stretch;
}}
.top5-scroll::-webkit-scrollbar {{ display: none; }}
.top5-card {{
    flex: 1 1 0; min-width: 0; background: {C_SECONDARY}; border-radius: 12px; padding: 1rem 0.75rem;
    text-align: center; border-bottom: 3px solid {C_PRIMARY};
}}
.top5-medal {{ font-size: 1.5rem; line-height: 1; }}
.top5-name  {{ font-size: 0.78rem; font-weight: 700; color: {C_TEXT}; margin: 0.3rem 0 0.2rem; word-break: break-word; line-height: 1.2; }}
.top5-count {{ font-size: 1.6rem; font-weight: 800; color: {C_ACCENT}; line-height: 1; }}
.top5-lbl   {{ font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em; color: {C_MUTED}; font-weight: 600; }}

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
.chat-ex-label {{ font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {C_MUTED}; display: block; margin-bottom: 0.4rem; }}
.chat-ex {{ display: inline-block; background: white; border: 1.5px solid {C_PRIMARY}; color: {C_PRIMARY}; border-radius: 999px; padding: 0.22rem 0.75rem; margin: 0.15rem 0.2rem 0.15rem 0; font-size: 0.78rem; font-weight: 600; }}
.no-key-box {{ background: white; border: 1.5px solid {C_PRIMARY}; border-radius: 10px; padding: 0.9rem 1.2rem; font-size: 0.88rem; color: {C_TEXT}; margin-top: 0.75rem; line-height: 1.7; }}
.upload-hint {{ display: flex; align-items: flex-start; gap: 0.65rem; background: #EEF6FF; border: 1.5px solid #90CAF9; border-radius: 10px; padding: 0.75rem 0.95rem; font-size: 0.84rem; color: {C_TEXT}; margin-bottom: 0.85rem; line-height: 1.55; }}
.upload-hint-icon {{ font-size: 1.2rem; flex-shrink: 0; margin-top: 0.05rem; }}
.sheets-hint {{ background: #F0FFF4; border: 1.5px solid #A5D6A7; border-radius: 10px; padding: 0.75rem 0.95rem; font-size: 0.83rem; color: {C_TEXT}; margin-bottom: 0.85rem; line-height: 1.6; }}

/* ─── MOBILE RESPONSIVE ──────────────────────────────────────────────── */
@media (max-width: 768px) {{
    .block-container {{ padding: 0.5rem 0.6rem 5.5rem !important; max-width: 100% !important; }}
    .welcome-wrap {{ padding: 1.5rem 0.25rem 1rem; }}
    .welcome-icon {{ font-size: 3rem; }}
    .welcome-title {{ font-size: 1.75rem; }}
    .welcome-sub {{ font-size: 0.9rem; }}
    .welcome-steps {{ padding: 1rem 1rem; border-radius: 12px; }}
    .welcome-step {{ font-size: 0.88rem; }}
    .dash-header {{ padding: 0.6rem 0.85rem; gap: 0.3rem; }}
    .dash-brand {{ font-size: 1.05rem; }}
    .dash-meta {{ font-size: 0.7rem; }}
    .file-badge {{ margin-left: 0; max-width: calc(100% - 1rem); font-size: 0.7rem; }}
    .kpi-card {{ padding: 0.85rem 0.3rem; border-radius: 10px; }}
    .kpi-num {{ font-size: 1.65rem; }}
    .kpi-lbl {{ font-size: 0.58rem; }}
    .top5-scroll {{ scroll-snap-type: x mandatory; }}
    .top5-card {{ flex: 0 0 auto; min-width: 115px; scroll-snap-align: start; padding: 0.75rem 0.5rem; }}
    .top5-name {{ font-size: 0.72rem; }}
    .top5-count {{ font-size: 1.35rem; }}
    .top5-medal {{ font-size: 1.3rem; }}
    .section-lbl {{ font-size: 0.62rem; margin: 1rem 0 0.35rem; }}
    .resumen-box {{ padding: 0.8rem 0.9rem; }}
    .resumen-line {{ font-size: 0.82rem; }}
    div[data-testid="stRadio"] > div {{ flex-wrap: wrap !important; gap: 0.35rem !important; }}
    div[data-testid="stRadio"] label {{ min-height: 44px; display: flex; align-items: center; }}
    .stButton > button, [data-testid="stDownloadButton"] > button {{ min-height: 48px !important; font-size: 0.88rem !important; width: 100% !important; }}
    [data-testid="stFileUploadDropzone"] {{ min-height: 100px !important; padding: 1.5rem 1rem !important; }}
    [data-testid="stDataFrame"] {{ overflow-x: auto !important; -webkit-overflow-scrolling: touch; }}
    .js-plotly-plot .plotly {{ max-height: 320px; }}
    .chat-wrap {{ padding: 1rem 0.9rem 0.75rem; }}
    .chat-title {{ font-size: 0.95rem; }}
    .chat-desc {{ font-size: 0.78rem; }}
    .chat-ex {{ font-size: 0.73rem; padding: 0.25rem 0.6rem; }}
    [data-testid="stChatInput"] textarea {{ font-size: 1rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

FOOTER = '<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>'

# ─── Detección de columnas y lectura robusta ──────────────────────────────────
COLUMN_TARGETS = {
    "Cadete": {
        "label": "Chofer / Cadete", "emoji": "📦",
        "keywords": ["cadete", "chofer", "repartidor", "mensajero", "conductor", "delivery", "despachante"],
    },
    "Zona": {
        "label": "Zona", "emoji": "🗺️",
        "keywords": ["zona", "area", "área", "sector", "region", "región", "barrio"],
    },
    "Nombre Fantasia": {
        "label": "Empresa", "emoji": "🏢",
        "keywords": ["nombre fantasia", "fantasía", "fantasia", "empresa", "cliente", "comercio", "negocio", "razon social", "razón social"],
    },
    "Estado": {
        "label": "Estado", "emoji": "📋",
        "keywords": ["estado", "status", "situacion", "situación", "estatus", "condicion", "condición"],
    },
}

def detectar_df(archivo, es_csv=False):
    nombre_archivo = archivo.name.lower()
    
    # CASO 1: Es un Excel Viejo (.xls)
    if nombre_archivo.endswith('.xls'):
        for h in range(8):  # Buscamos hasta en las primeras 8 filas el título
            try:
                archivo.seek(0)
                df = pd.read_excel(archivo, header=h, engine='xlrd')
                if df is not None and not df.empty and len(df.columns) > 2:
                    return df, h
            except Exception:
                continue

    # CASO 2: Es un CSV
    elif nombre_archivo.endswith('.csv'):
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            for h in range(6):
                try:
                    archivo.seek(0)
                    df = pd.read_csv(archivo, header=h, encoding=encoding)
                    if df is not None and not df.empty and len(df.columns) > 2:
                        return df, h
                except Exception:
                    continue

    # CASO 3: Es un Excel Moderno (.xlsx)
    else:
        for h in range(8):
            try:
                archivo.seek(0)
                df = pd.read_excel(archivo, header=h, engine='openpyxl')
                if df is not None and not df.empty and len(df.columns) > 2:
                    return df, h
            except Exception:
                continue

    # 🚨 EL SALVAVIDAS SUPREMO: Si lo de arriba falló, lee el archivo crudo como venga
    try:
        archivo.seek(0)
        if nombre_archivo.endswith('.xls'):
            df = pd.read_excel(archivo, engine='xlrd', header=0)
        elif nombre_archivo.endswith('.csv'):
            df = pd.read_csv(archivo, encoding='latin-1', header=0)
        else:
            df = pd.read_excel(archivo, engine='openpyxl', header=0)
            
        # Forzamos que las columnas sean texto para evitar errores
        df.columns = [str(c).strip() for c in df.columns]
        return df, 0
    except Exception:
        return None, 0

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
            if kl in cl or kl in kl: return col, "similar"
    return None, None

def construir_contexto(df: pd.DataFrame, col_map: dict) -> str:
    partes = [f"Total de envíos: {len(df)}"]
    estado_col = col_map.get("Estado")
    if estado_col:
        dist = df[estado_col].value_counts()
        partes.append("\nDistribución por estado:")
        for estado, cnt in dist.items(): partes.append(f"  - {estado}: {cnt}")
    return "\n".join(partes)

def generar_resumen(df: pd.DataFrame, col_agrup: str, estado_col, top_n: int = 5) -> list:
    counts = df.groupby(col_agrup, dropna=False).size().nlargest(top_n)
    lineas = []
    for nombre, total in counts.items():
        nombre_str = "Sin datos" if pd.isna(nombre) else str(nombre)
        if estado_col:
            subset = df[df[col_agrup].isna()] if pd.isna(nombre) else df[df[col_agrup] == nombre]
            est = subset[estado_col].astype(str).str.lower()
            pend = int(est.str.contains("pendiente", na=False).sum() + est.str.contains("rechazado", na=False).sum())
            entr = int(est.str.contains("entregado", na=False).sum())
            lineas.append(f"<b>{nombre_str}</b> tiene <b>{total}</b> órdenes · {entr} exitosas · {pend} desvíos")
        else:
            lineas.append(f"<b>{nombre_str}</b> tiene <b>{total}</b> órdenes")
    return lineas

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
        df_cargado, header_row = detectar_df(archivo, es_csv)
        
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

# ─ KPIs CORPORATIVOS (MÉTRICAS REALES) ─────────────────────────────────────────
estado_col_real = col_map.get("Estado")
total_orders = len(df)
entregados = desvios = 0

if estado_col_real:
    estados = df[estado_col_real].astype(str).str.lower().str.strip()
    entregados = int(estados.str.contains("entregado", na=False).sum())
    desvios = int(estados.str.contains("pendiente", na=False).sum() + estados.str.contains("rechazado", na=False).sum())

# Cálculos Profesionales
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
    col = col_map[target]
    label = f"{info['emoji']}  {info['label']}"
    radio_opts.append(label)
    radio_map[label] = (col, info["label"])

analisis_label = st.radio("analisis", options=radio_opts, horizontal=True, label_visibility="collapsed")
col_agrup, analisis_nombre = radio_map[analisis_label]

if col_agrup is None:
    st.warning(f"No se detectó automáticamente la columna para {analisis_nombre} en este reporte de Lighdata.")
    st.stop()

# Datos agrupados para el gráfico
df_grouped = df.groupby(col_agrup, dropna=False).size().reset_index(name="Cantidad").sort_values("Cantidad", ascending=False)
df_grouped[col_agrup] = df_grouped[col_agrup].fillna("Sin Datos").astype(str)

# Gráfico Corporativo
fig = px.bar(df_grouped.head(15), x=col_agrup, y="Cantidad", color=col_agrup, color_discrete_sequence=CHART_COLORS, template="plotly_white", text="Cantidad")
fig.update_layout(showlegend=False, height=350, margin=dict(t=10, b=40, l=10, r=10))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Resumen Ejecutivo Automático
lineas = generar_resumen(df, col_agrup, estado_col_real)
if lineas:
    items_html = "".join(f'<div class="resumen-line">· {l}</div>' for l in lineas)
    st.markdown(f'<div class="resumen-box"><div class="resumen-titulo">📝 Resumen Ejecutivo Automatizado</div>{items_html}</div>', unsafe_allow_html=True)

# ─── SECCIÓN DE SOPORTE E INCIDENCIAS (SUPABASE O PENDIENTES) ──────────────────
st.divider()
st.markdown(f"""
<div class="chat-wrap" style="background:{C_SECONDARY}">
    <p class="chat-title">📱 Registro de Incidencias Operativas (Soporte)</p>
    <p class="chat-desc">Habilitado para la edición y actualización del equipo de Post-Venta al día siguiente.</p>
</div>
""", unsafe_allow_html=True)

# Simulación de protección estructural (Mapeado a la Fase 2 del Roadmap)
with st.expander("🛠️ Mesa de ayuda / Modificar Incidencias"):
    st.info("Módulo listo para recibir las actualizaciones de los choferes mediante los secretos del servidor.")

st.markdown(FOOTER, unsafe_allow_html=True)