import os
import re
import io
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from utils.auth import login_requerido, logout, get_nombre, get_rol, es_admin, es_demo

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

# ─── AUTENTICACIÓN ────────────────────────────────────────────────────────────
login_requerido()
_USUARIO = get_nombre()
_ROL     = get_rol()


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

# ─── RADAR DE PALABRAS CLAVE AMPLIADO ─────────────────────────────────────────
COLUMN_TARGETS = {
    "Cadete": {
        "label": "Chofer / Cadete", "emoji": "📦",
        "keywords": ["chofer", "cadete", "repartidor", "mensajero", "conductor", "delivery", "nombre", "chófer"],
    },
    "Zona": {
        "label": "Zona", "emoji": "🗺️",
        "keywords": ["zona", "localidad", "area", "área", "sector", "barrio", "destino"],
    },
    "Nombre Fantasia": {
        "label": "Empresa / Fantasía", "emoji": "🏢",
        "keywords": ["nombre fantasia", "fantasía", "fantasia", "empresa", "cliente", "comercio", "remitente"],
    },
    "Estado": {
        "label": "Estado", "emoji": "📋",
        "keywords": ["estado", "status", "situacion", "situación", "motivo", "condicion", "historial"],
    },
}

def detectar_df(archivo, es_csv=False):
    nombre_archivo = archivo.name.lower()
    df, header_encontrado = None, 0
    
    # 1. Intentar como HTML disfrazado (Lighdata crudo)
    if nombre_archivo.endswith('.xls'):
        try:
            archivo.seek(0)
            tablas = pd.read_html(archivo)
            if tablas and len(tablas) > 0:
                df = tablas[0]
                df.columns = [str(c).strip() for c in df.columns]
                return df, 0
        except Exception:
            pass

    # 2. Excel Viejo Tradicional
    if nombre_archivo.endswith('.xls') and df is None:
        for h in range(6):
            try:
                archivo.seek(0)
                temp_df = pd.read_excel(archivo, header=h, engine='xlrd')
                if temp_df is not None and not temp_df.empty and len(temp_df.columns) > 1:
                    df, header_encontrado = temp_df, h
                    break
            except Exception: continue

    # 3. CSV
    elif nombre_archivo.endswith('.csv'):
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

    # 4. Excel Moderno (.xlsx) — detección inteligente de fila de encabezado
    elif nombre_archivo.endswith('.xlsx'):
        try:
            archivo.seek(0)
            temp_df = pd.read_excel(archivo, header=None, engine='openpyxl')
            header_encontrado = 0
            for i, row in temp_df.iterrows():
                valores = [str(v).strip() for v in row.values]
                if "Cadete" in valores and "Estado" in valores and "Zona" in valores:
                    header_encontrado = i
                    break
            st.write(f"🔍 Fila de encabezado detectada: {header_encontrado}")
            archivo.seek(0)
            df = pd.read_excel(archivo, header=header_encontrado, engine='openpyxl')
        except Exception:
            pass

    # Salvavidas final
    if df is None or df.empty:
        try:
            archivo.seek(0)
            if nombre_archivo.endswith('.xls'): df = pd.read_excel(archivo, engine='xlrd', header=0)
            elif nombre_archivo.endswith('.csv'): df = pd.read_csv(archivo, encoding='latin-1', header=0)
            else: df = pd.read_excel(archivo, engine='openpyxl', header=0)
            header_encontrado = 0
        except Exception:
            return None, 0

    # Limpieza de columnas vacías o raras
    df.columns = [str(c).strip() for c in df.columns if c is not None]
    return df, header_encontrado

def buscar_columna(cols: list, target: str, keywords: list):
    pairs = [(c, str(c).lower().strip()) for c in cols]
    tl = target.lower().strip()

    # 1. Coincidencia exacta
    for col, cl in pairs:
        if cl == tl: return col

    # 2. Coincidencia parcial (target contenido en columna o viceversa)
    for col, cl in pairs:
        if tl in cl or cl in tl: return col

    # 3. Keywords
    for kw in keywords:
        kl = kw.lower()
        for col, cl in pairs:
            if kl in cl: return col

    return None
def generar_resumen(df: pd.DataFrame, col_agrup: str, estado_col, top_n: int = 5) -> list:
    try:
        counts = df.groupby(col_agrup, dropna=False).size().nlargest(top_n)
        lineas = []
        for nombre, total in counts.items():
            nombre_str = "Sin datos" if pd.isna(nombre) else str(nombre)
            lineas.append(f"<b>{nombre_str}</b> procesó un volumen de <b>{total}</b> unidades.")
        return lineas
    except Exception:
        return ["No se pudo procesar el desglose de esta columna."]

def norm_estados(serie):
    return (serie.astype(str).str.lower().str.strip()
        .str.replace("á","a",regex=False).str.replace("é","e",regex=False)
        .str.replace("í","i",regex=False).str.replace("ó","o",regex=False)
        .str.replace("ú","u",regex=False))

def tabla_dimension_estados(df, col_agrup, estado_col):
    s_e = norm_estados(df[estado_col])
    cat = pd.Series("Otros", index=df.index, dtype=object)
    cat[s_e.str.contains("rechazado|devuelto|rebote",      na=False)] = "Rechazados"
    cat[s_e.str.contains("pendiente|en viaje|en camino",   na=False)] = "Pendientes"
    cat[s_e.str.contains("entregado|entrega",              na=False)] = "Entregados"
    df_tmp = df[[col_agrup]].copy()
    df_tmp["__cat"] = cat.values
    pivot = df_tmp.groupby([col_agrup, "__cat"]).size().unstack(fill_value=0)
    for c in ["Entregados", "Pendientes", "Rechazados"]:
        if c not in pivot.columns: pivot[c] = 0
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot[["Total","Entregados","Pendientes","Rechazados"]].sort_values("Total", ascending=False).reset_index()
    pivot.columns.name = None
    pivot.rename(columns={col_agrup: "Nombre"}, inplace=True)
    return pivot

def guardar_incidencia(datos: dict):
    # ── Conexión Supabase ──────────────────────────────────────────────────
    # from supabase import create_client
    # url      = st.secrets["SUPABASE_URL"]
    # key      = st.secrets["SUPABASE_KEY"]
    # supabase = create_client(url, key)
    # supabase.table("incidencias").insert(datos).execute()
    # ──────────────────────────────────────────────────────────────────────
    ruta = "incidencias.csv"
    pd.DataFrame([datos]).to_csv(ruta, mode="a", header=not os.path.exists(ruta), index=False)
# ─── PANTALLA DE BIENVENIDA ───────────────────────────────────────────────────
if "df" not in st.session_state:
    if _ROL == "demo":
        from utils.demo_data import cargar_demo
        _df_demo = cargar_demo()
        _cm_demo = {
            t: buscar_columna(_df_demo.columns.tolist(), t, COLUMN_TARGETS[t]["keywords"])
            for t in COLUMN_TARGETS
        }
        st.session_state["df"]         = _df_demo
        st.session_state["filename"]   = "corte_demo.xlsx"
        st.session_state["header_row"] = 0
        st.session_state["col_map"]    = _cm_demo

    elif _ROL not in ("admin",):
        _, col_c, _ = st.columns([0.15, 3, 0.15])
        with col_c:
            st.markdown("""
            <div class="welcome-wrap">
                <div class="welcome-icon">⏳</div>
                <p class="welcome-title">Aguardando corte</p>
                <p class="welcome-sub">El administrador aún no cargó el corte operativo del día.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                logout()
        st.markdown(FOOTER, unsafe_allow_html=True)
        st.stop()

    else:
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

                archivo = st.file_uploader("Subí tu corte operativo de Lighdata o Flex", type=["xlsx", "xls", "csv"], label_visibility="collapsed")
                st.caption("Soporte nativo para cortes operativos: Excel Clásico (.xls) · Excel Moderno (.xlsx) · CSV")

        if archivo is not None:
            es_csv = archivo.name.lower().endswith(".csv")
            df_cargado, header_row = detectar_df(archivo, es_csv)

            if df_cargado is not None and not df_cargado.empty:
                col_map = {}
                for target, info in COLUMN_TARGETS.items():
                    col = buscar_columna(df_cargado.columns.tolist(), target, info["keywords"])
                    col_map[target] = col
                st.session_state.update({
                    "df": df_cargado, "filename": archivo.name, "header_row": header_row, "col_map": col_map
                })
                welcome_slot.empty()
                st.rerun()
            else:
                st.error("❌ No se pudo procesar el corte operativo. Verificá que tenga datos válidos.")
        st.markdown(FOOTER, unsafe_allow_html=True)
        st.stop()

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
df          = st.session_state["df"]
filename    = st.session_state["filename"]
col_map     = st.session_state["col_map"]

estado_col  = col_map.get("Estado")
cadete_col  = col_map.get("Cadete")
zona_col    = col_map.get("Zona")
empresa_col = col_map.get("Nombre Fantasia")

# ─ Pre-computar máscaras de estado ───────────────────────────────────────────
total_orders = len(df)
total_pendientes = total_rechazados = total_en_viaje = total_motivo = total_entregados = 0
df_alertas = pd.DataFrame()

if estado_col and estado_col in df.columns:
    s = norm_estados(df[estado_col])
    mask_pend_puro = s.str.contains("pendiente",                    na=False, regex=False)
    mask_en_viaje  = s.str.contains("en viaje|en camino",           na=False)
    mask_rech      = s.str.contains("rechazado|devuelto|rebote",    na=False)
    mask_motivo    = s.str.contains("motivo",                       na=False, regex=False)
    mask_entr      = s.str.contains("entregado|entrega",            na=False)

    total_pendientes = int(mask_pend_puro.sum())
    total_en_viaje   = int(mask_en_viaje.sum())
    total_rechazados = int(mask_rech.sum())
    total_motivo     = int(mask_motivo.sum())
    total_entregados = int(mask_entr.sum())
    mask_alerta      = mask_pend_puro | mask_en_viaje | mask_rech | mask_motivo
    df_alertas       = df[mask_alerta].copy()

total_anomalias = total_pendientes + total_en_viaje + total_rechazados + total_motivo
otd_pct = f"{(total_entregados / total_orders * 100):.1f}%" if total_orders > 0 else "0.0%"
inc_pct = f"{((total_pendientes + total_en_viaje) / total_orders * 100):.1f}%" if total_orders > 0 else "0.0%"
tracking_col = next((c for c in df.columns if "tracking" in str(c).lower()), None)

# Pendientes críticos: sin resolver más de 48hs
fecha_col = next((c for c in df.columns if any(kw in str(c).lower() for kw in ["fecha", "date", "hora", "timestamp", "creado", "ingreso"])), None)
pendientes_criticos = 0
if fecha_col and estado_col and estado_col in df.columns:
    try:
        fechas = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
        horas_transcurridas = (pd.Timestamp.now() - fechas).dt.total_seconds() / 3600
        mask_critico = (mask_pend_puro | mask_en_viaje) & (horas_transcurridas > 48)
        pendientes_criticos = int(mask_critico.sum())
    except Exception:
        pendientes_criticos = 0

# ─ Header ────────────────────────────────────────────────────────────────────
col_h, col_btn, col_out = st.columns([5, 1.1, 0.9])
with col_h:
    badge_name = filename if len(filename) <= 22 else filename[:22] + "…"
    rol_badge  = "👑 Admin" if _ROL == "admin" else ("👁️ Demo" if _ROL == "demo" else "👤 Coordinadora")
    st.markdown(f"""
    <div class="dash-header">
        <span style="font-size:1.5rem">📊</span>
        <div>
            <p class="dash-brand">LogiTrack - Panel Corporativo</p>
            <p class="dash-meta">{total_orders:,} unidades auditadas · {rol_badge} {_USUARIO}</p>
        </div>
        <span class="file-badge">📂 {badge_name}</span>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if es_admin() and st.button("🔄 Nuevo Corte", use_container_width=True):
        auth_data = st.session_state.get("auth")
        st.session_state.clear()
        st.session_state["auth"] = auth_data
        st.rerun()
with col_out:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()

# ─ Banner demo ───────────────────────────────────────────────────────────────
if _ROL == "demo":
    st.info("👁️ **Modo demo** — Estás viendo datos ficticios de ejemplo. No podés subir archivos ni registrar incidencias.", icon=None)

# ─ KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Indicadores Clave de Rendimiento (KPIs)</p>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_PRIMARY}">
        <div class="kpi-num" style="color:{C_PRIMARY}">{total_orders:,} <span style="font-size:1.2rem">un.</span></div>
        <div class="kpi-lbl">ORDER FILL RATE (OFR)</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_GREEN}">
        <div class="kpi-num" style="color:{C_GREEN}">{otd_pct}</div>
        <div class="kpi-lbl">% OTD — ENTREGAS EFECTIVAS</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_ACCENT}">
        <div class="kpi-num" style="color:{C_ACCENT}">{inc_pct}</div>
        <div class="kpi-lbl">TASA DE INCIDENCIA</div>
    </div>""", unsafe_allow_html=True)
with k4:
    _color_crit = "#C0392B" if pendientes_criticos > 0 else C_MUTED
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{_color_crit}">
        <div class="kpi-num" style="color:{_color_crit}">{pendientes_criticos}</div>
        <div class="kpi-lbl">PENDIENTES CRÍTICOS +48HS</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ─ LISTA NEGRA: Pendientes en Riesgo ─────────────────────────────────────────
if not df_alertas.empty and estado_col and estado_col in df.columns:
    s_riesgo = norm_estados(df_alertas[estado_col])
    prioridad = pd.Series(4, index=df_alertas.index)
    prioridad[s_riesgo.str.contains("rechazado|devuelto|rebote", na=False)] = 1
    prioridad[s_riesgo.str.contains("pendiente", na=False, regex=False)] = 2
    prioridad[s_riesgo.str.contains("en viaje|en camino", na=False)] = 3
    df_riesgo = df_alertas.copy()
    df_riesgo["__prio"] = prioridad.values
    df_riesgo = df_riesgo.sort_values("__prio")

    cols_sel = {k: v for k, v in [
        ("Tracking", tracking_col), ("Cadete", cadete_col),
        ("Empresa", empresa_col), ("Zona", zona_col), ("Estado", estado_col)
    ] if v and v in df_riesgo.columns}

    df_tabla_riesgo = (
        df_riesgo[[v for v in cols_sel.values()]]
        .rename(columns={v: k for k, v in cols_sel.items()})
        .reset_index(drop=True)
    )

    st.markdown("""
    <div style="background:#C0392B; color:white; padding:0.75rem 1.2rem;
        border-radius:10px 10px 0 0; font-weight:800; font-size:1.05rem; margin-top:0.5rem;">
        ⚠️ Pendientes en Riesgo
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df_tabla_riesgo.style.set_properties(**{
            "background-color": "#FFEBEE",
            "color": "#C0392B",
            "font-weight": "600",
        }),
        use_container_width=True, hide_index=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

# ─ 1. ALERTAS CRÍTICAS ───────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">🚨 Alertas Críticas del Corte</p>', unsafe_allow_html=True)
a1, a2, a3, a4 = st.columns(4)
for col_a, lbl, val, color in [
    (a1, "⏳ Pendientes", total_pendientes, "#FF6B6B"),
    (a2, "❌ Rechazados", total_rechazados, "#C0392B"),
    (a3, "🚚 En Viaje",   total_en_viaje,   "#F39C12"),
    (a4, "📌 Con Motivo", total_motivo,     "#E67E22"),
]:
    with col_a:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div class="kpi-num" style="color:{color}">{val}</div>
            <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

if not (estado_col and estado_col in df.columns):
    st.info("ℹ️ No se detectó columna de Estado — las alertas críticas no están disponibles.")
elif total_anomalias == 0:
    st.success("✅ Sin anomalías detectadas en este corte.")

st.divider()

# ─ 2. DESGLOSE POR DIMENSIÓN ─────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Dimensión de Análisis Logístico</p>', unsafe_allow_html=True)
radio_opts, radio_map = [], {}
for target, info in COLUMN_TARGETS.items():
    col = col_map.get(target)
    if col and col in df.columns:
        label = f"{info['emoji']}  {info['label']}"
        radio_opts.append(label)
        radio_map[label] = (col, info["label"], target)

if radio_opts:
    analisis_label = st.radio("analisis", options=radio_opts, horizontal=True, label_visibility="collapsed")
    col_agrup, analisis_nombre, target_key = radio_map[analisis_label]

    COLOR_ESTADOS = {"Entregados": C_GREEN, "Pendientes": "#FF6B6B", "Rechazados": "#C0392B"}

    if target_key in ("Cadete", "Nombre Fantasia") and estado_col and estado_col in df.columns:
        tabla = tabla_dimension_estados(df, col_agrup, estado_col)
        df_melt = tabla.melt(
            id_vars=["Nombre"], value_vars=["Entregados", "Pendientes", "Rechazados"],
            var_name="Estado", value_name="Cantidad"
        )

        if target_key == "Cadete":
            tabla["Efectividad %"] = (tabla["Entregados"] / tabla["Total"].replace(0, 1) * 100).round(1)
            tabla = tabla.sort_values("Efectividad %", ascending=False).reset_index(drop=True)
            tabla.insert(0, "Rank", range(1, len(tabla) + 1))
            fig = px.bar(df_melt, x="Nombre", y="Cantidad", color="Estado",
                color_discrete_map=COLOR_ESTADOS, template="plotly_white", text="Cantidad", barmode="stack")
            fig.update_layout(height=380, margin=dict(t=10, b=50, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown('<p class="section-lbl">Ranking de Efectividad por Cadete</p>', unsafe_allow_html=True)

            def color_cadete(row):
                if "Efectividad %" in row.index:
                    if row["Efectividad %"] < 80:
                        return ["background-color:#FFEBEE; color:#C0392B; font-weight:700;"] * len(row)
                    if row["Efectividad %"] > 95:
                        return ["background-color:#E8F5E9; color:#2E7D32; font-weight:700;"] * len(row)
                return [""] * len(row)

            st.dataframe(
                tabla.style.apply(color_cadete, axis=1).format({"Efectividad %": "{:.1f}%"}),
                use_container_width=True, hide_index=True
            )

        else:
            tabla["% Pendientes"] = (tabla["Pendientes"] / tabla["Total"].replace(0, 1) * 100).round(1)
            fig = px.bar(df_melt.head(45), x="Cantidad", y="Nombre", color="Estado",
                color_discrete_map=COLOR_ESTADOS, template="plotly_white", text="Cantidad",
                barmode="stack", orientation="h")
            fig.update_layout(
                height=max(300, min(len(tabla) * 38, 560)),
                margin=dict(t=10, b=10, l=10, r=10), yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown('<p class="section-lbl">Unidades por Empresa</p>', unsafe_allow_html=True)

            def color_empresa(row):
                if "% Pendientes" in row.index and row["% Pendientes"] > 20:
                    return ["background-color:#FFEBEE; color:#C0392B;"] * len(row)
                return [""] * len(row)

            st.dataframe(
                tabla.style.apply(color_empresa, axis=1).format({"% Pendientes": "{:.1f}%"}),
                use_container_width=True, hide_index=True
            )

    else:
        df_grouped = df.groupby(col_agrup, dropna=False).size().reset_index(name="Unidades").sort_values("Unidades", ascending=False)
        df_grouped[col_agrup] = df_grouped[col_agrup].fillna("Sin Datos").astype(str)
        fig = px.bar(df_grouped.head(15), x=col_agrup, y="Unidades", color=col_agrup,
            color_discrete_sequence=CHART_COLORS, template="plotly_white", text="Unidades")
        fig.update_layout(showlegend=False, height=350, margin=dict(t=10, b=40, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    lineas = generar_resumen(df, col_agrup, estado_col)
    if lineas:
        items_html = "".join(f'<div class="resumen-line">· {l}</div>' for l in lineas)
        st.markdown(f'<div class="resumen-box"><div class="resumen-titulo">📝 Resumen Ejecutivo Automatizado</div>{items_html}</div>', unsafe_allow_html=True)
else:
    st.warning("No se pudieron mapear las columnas para mostrar los gráficos de control.")

st.divider()

# ─ 3. RADAR DE CLIENTES AFECTADOS ────────────────────────────────────────────
if empresa_col and empresa_col in df.columns:
    st.markdown('<p class="section-lbl">🏢 Radar de Clientes Afectados</p>', unsafe_allow_html=True)
    if df_alertas.empty:
        st.info("✅ Sin clientes con alertas activas en este corte.")
    else:
        clientes_aff = (
            df_alertas.groupby(empresa_col, dropna=False)
            .size().reset_index(name="Órdenes con Alerta")
            .sort_values("Órdenes con Alerta", ascending=False)
        )
        clientes_aff[empresa_col] = clientes_aff[empresa_col].fillna("Sin Datos").astype(str)
        fig_cli = px.bar(
            clientes_aff.head(15), x="Órdenes con Alerta", y=empresa_col,
            orientation="h", color="Órdenes con Alerta",
            color_continuous_scale=["#FFF3C4", "#FF6B6B"],
            template="plotly_white", text="Órdenes con Alerta"
        )
        fig_cli.update_layout(
            showlegend=False, coloraxis_showscale=False,
            height=max(260, min(len(clientes_aff) * 36, 520)),
            margin=dict(t=10, b=10, l=10, r=10), yaxis_title=""
        )
        st.plotly_chart(fig_cli, use_container_width=True, config={"displayModeBar": False})

# ─ 4. ZONAS CALIENTES ────────────────────────────────────────────────────────
if zona_col and zona_col in df.columns:
    st.markdown('<p class="section-lbl">🔥 Zonas Calientes</p>', unsafe_allow_html=True)
    if df_alertas.empty:
        st.info("✅ Sin zonas con alertas activas en este corte.")
    else:
        zonas_hot = (
            df_alertas.groupby(zona_col, dropna=False)
            .size().reset_index(name="Problemas")
            .sort_values("Problemas", ascending=False)
        )
        zonas_hot[zona_col] = zonas_hot[zona_col].fillna("Sin Datos").astype(str)
        fig_zona = px.bar(
            zonas_hot.head(15), x=zona_col, y="Problemas",
            color="Problemas", color_continuous_scale=["#FFF3C4", "#FF6B6B"],
            template="plotly_white", text="Problemas"
        )
        fig_zona.update_layout(showlegend=False, coloraxis_showscale=False, height=320, margin=dict(t=10, b=50, l=10, r=10))
        st.plotly_chart(fig_zona, use_container_width=True, config={"displayModeBar": False})

st.markdown(FOOTER, unsafe_allow_html=True)