import os
import streamlit as st
import pandas as pd
import plotly.express as px
import io

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
.kpi-num {{ font-size: 2.4rem; font-weight: 800; line-height: 1; }}
.kpi-lbl {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: {C_MUTED}; margin-top: 0.35rem;
}}

/* Top 5 — scroll container (desktop: stretch; mobile: scroll) */
.top5-scroll {{
    display: flex;
    gap: 0.75rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    align-items: stretch;
}}
.top5-scroll::-webkit-scrollbar {{ display: none; }}
.top5-card {{
    flex: 1 1 0;
    min-width: 0;
    background: {C_SECONDARY}; border-radius: 12px; padding: 1rem 0.75rem;
    text-align: center; border-bottom: 3px solid {C_PRIMARY};
}}
.top5-medal {{ font-size: 1.5rem; line-height: 1; }}
.top5-name  {{
    font-size: 0.78rem; font-weight: 700; color: {C_TEXT};
    margin: 0.3rem 0 0.2rem; word-break: break-word; line-height: 1.2;
}}
.top5-count {{ font-size: 1.6rem; font-weight: 800; color: {C_ACCENT}; line-height: 1; }}
.top5-lbl   {{
    font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em;
    color: {C_MUTED}; font-weight: 600;
}}

/* Resumen natural */
.resumen-box {{
    background: {C_SECONDARY}; border-left: 4px solid {C_PRIMARY};
    border-radius: 0 10px 10px 0; padding: 1rem 1.2rem; margin: 0.8rem 0 1rem;
}}
.resumen-titulo {{
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: {C_PRIMARY}; margin-bottom: 0.55rem;
}}
.resumen-line {{ font-size: 0.88rem; color: {C_TEXT}; margin: 0.22rem 0; }}

/* Labels de sección */
.section-lbl {{
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: {C_MUTED}; margin: 1.4rem 0 0.5rem;
}}

/* Footer */
.app-footer {{
    margin-top: 3rem; padding-top: 1.2rem;
    border-top: 2px solid {C_SECONDARY};
    text-align: center; color: {C_MUTED}; font-size: 0.82rem;
}}

/* Chat */
.chat-wrap {{
    background: {C_SECONDARY}; border-radius: 14px;
    padding: 1.4rem 1.5rem 1rem; margin-top: 0.5rem;
}}
.chat-title {{ font-size: 1.1rem; font-weight: 800; color: {C_TEXT}; margin: 0 0 0.25rem; }}
.chat-desc  {{ font-size: 0.85rem; color: {C_MUTED}; margin: 0 0 0.9rem; }}
.chat-ex-label {{
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: {C_MUTED}; display: block; margin-bottom: 0.4rem;
}}
.chat-ex {{
    display: inline-block; background: white; border: 1.5px solid {C_PRIMARY};
    color: {C_PRIMARY}; border-radius: 999px; padding: 0.22rem 0.75rem;
    margin: 0.15rem 0.2rem 0.15rem 0; font-size: 0.78rem; font-weight: 600;
}}
.no-key-box {{
    background: white; border: 1.5px solid {C_PRIMARY};
    border-radius: 10px; padding: 0.9rem 1.2rem;
    font-size: 0.88rem; color: {C_TEXT}; margin-top: 0.75rem; line-height: 1.7;
}}

/* ─── MOBILE RESPONSIVE ──────────────────────────────────────────────── */
@media (max-width: 768px) {{
    /* Padding extra abajo para el teclado del chat */
    .block-container {{
        padding: 0.5rem 0.6rem 5.5rem !important;
        max-width: 100% !important;
    }}

    /* Bienvenida */
    .welcome-wrap {{ padding: 1.5rem 0.25rem 1rem; }}
    .welcome-icon {{ font-size: 3rem; }}
    .welcome-title {{ font-size: 1.75rem; }}
    .welcome-sub {{ font-size: 0.9rem; }}
    .welcome-steps {{ padding: 1rem 1rem; border-radius: 12px; }}
    .welcome-step {{ font-size: 0.88rem; }}

    /* Header — badge debajo en pantallas chicas */
    .dash-header {{ padding: 0.6rem 0.85rem; gap: 0.3rem; }}
    .dash-brand {{ font-size: 1.05rem; }}
    .dash-meta {{ font-size: 0.7rem; }}
    .file-badge {{
        margin-left: 0;
        max-width: calc(100% - 1rem);
        font-size: 0.7rem;
    }}

    /* KPIs */
    .kpi-card {{ padding: 0.85rem 0.3rem; border-radius: 10px; }}
    .kpi-num {{ font-size: 1.85rem; }}
    .kpi-lbl {{ font-size: 0.6rem; }}

    /* Top 5 — cards con ancho fijo para scroll táctil */
    .top5-scroll {{ scroll-snap-type: x mandatory; }}
    .top5-card {{
        flex: 0 0 auto;
        min-width: 115px;
        scroll-snap-align: start;
        padding: 0.75rem 0.5rem;
    }}
    .top5-name {{ font-size: 0.72rem; }}
    .top5-count {{ font-size: 1.35rem; }}
    .top5-medal {{ font-size: 1.3rem; }}

    /* Section labels */
    .section-lbl {{ font-size: 0.62rem; margin: 1rem 0 0.35rem; }}

    /* Resumen */
    .resumen-box {{ padding: 0.8rem 0.9rem; }}
    .resumen-line {{ font-size: 0.82rem; }}

    /* Radio buttons — que hagan wrap en pantalla chica */
    div[data-testid="stRadio"] > div {{
        flex-wrap: wrap !important;
        gap: 0.35rem !important;
    }}
    div[data-testid="stRadio"] label {{
        min-height: 44px;
        display: flex;
        align-items: center;
    }}

    /* Tap targets grandes (mínimo 48px alto) */
    .stButton > button {{
        min-height: 48px !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 0.8rem !important;
        width: 100% !important;
    }}
    [data-testid="stDownloadButton"] > button {{
        min-height: 48px !important;
        font-size: 0.88rem !important;
        width: 100% !important;
    }}

    /* Uploader — área de toque más grande */
    [data-testid="stFileUploadDropzone"] {{
        min-height: 100px !important;
        padding: 1.5rem 1rem !important;
        cursor: pointer;
    }}

    /* Tabla con scroll horizontal */
    [data-testid="stDataFrame"] {{
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }}
    [data-testid="stDataFrame"] > div {{
        min-width: 0;
    }}

    /* Plotly: altura reducida en mobile */
    .js-plotly-plot .plotly {{ max-height: 320px; }}

    /* Chat */
    .chat-wrap {{ padding: 1rem 0.9rem 0.75rem; }}
    .chat-title {{ font-size: 0.95rem; }}
    .chat-desc {{ font-size: 0.78rem; }}
    .chat-ex {{
        font-size: 0.73rem;
        padding: 0.25rem 0.6rem;
        margin: 0.18rem 0.12rem;
    }}
    .no-key-box {{ font-size: 0.8rem; }}
    .no-key-box code {{ word-break: break-all; font-size: 0.72rem; }}

    /* Input del chat — accesible con teclado mobile */
    [data-testid="stChatInput"] textarea {{
        font-size: 1rem !important;
    }}

    /* Expander */
    .streamlit-expanderContent {{ padding: 0.5rem !important; }}

    /* Footer */
    .app-footer {{ font-size: 0.72rem; padding-top: 0.8rem; }}
}}

@media (max-width: 400px) {{
    .welcome-title {{ font-size: 1.45rem; }}
    .kpi-num {{ font-size: 1.55rem; }}
    .dash-brand {{ font-size: 0.95rem; }}
    .top5-card {{ min-width: 100px; }}
    .block-container {{ padding-left: 0.4rem !important; padding-right: 0.4rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

FOOTER = '<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>'

# ─── Detección de columnas ────────────────────────────────────────────────────
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
        "keywords": ["nombre fantasia", "fantasía", "fantasia", "empresa", "cliente", "comercio",
                     "negocio", "razon social", "razón social", "nombre cuenta", "cuenta"],
    },
    "Estado": {
        "label": "Estado", "emoji": "📋",
        "keywords": ["estado", "status", "situacion", "situación", "estatus", "condicion", "condición"],
    },
}


def _contar_reales(df: pd.DataFrame) -> int:
    return sum(
        1 for c in df.columns
        if not str(c).startswith("Unnamed") and not str(c).strip().replace(".", "").isdigit()
    )


def detectar_df(archivo, es_csv: bool):
    best_df, best_score, best_h = None, -1, 0
    for h in range(6):
        try:
            archivo.seek(0)
            candidate = pd.read_csv(archivo, header=h) if es_csv else pd.read_excel(archivo, header=h)
            score = _contar_reales(candidate)
            if score > best_score:
                best_df, best_score, best_h = candidate, score, h
        except Exception:
            pass
    archivo.seek(0)
    return best_df, best_h


def buscar_columna(cols: list, target: str, keywords: list):
    pairs = [(c, str(c).lower().strip()) for c in cols]
    tl = target.lower().strip()
    for col, cl in pairs:
        if cl == tl:
            return col, "exacta"
    for col, cl in pairs:
        if tl in cl or cl in tl:
            return col, "parcial"
    for kw in keywords:
        kl = kw.lower()
        for col, cl in pairs:
            if kl in cl or cl in kl:
                return col, "similar"
    return None, None


def construir_contexto(df: pd.DataFrame, col_map: dict) -> str:
    partes = [f"Total de envíos en el archivo: {len(df)}"]

    estado_col = col_map.get("Estado")
    if estado_col:
        dist = df[estado_col].value_counts()
        partes.append("\nDistribución por estado:")
        for estado, cnt in dist.items():
            partes.append(f"  - {estado}: {cnt}")

    for target, info in COLUMN_TARGETS.items():
        col = col_map.get(target)
        if not col:
            continue
        conteos = df.groupby(col, dropna=False).size().sort_values(ascending=False).head(10)
        partes.append(f"\nEnvíos por {info['label']}:")
        for nombre, total in conteos.items():
            es_nulo = pd.isna(nombre) if not isinstance(nombre, str) else False
            nombre_str = "Sin datos" if es_nulo else str(nombre)
            linea = f"  - {nombre_str}: {total} envíos"
            if estado_col:
                mask = df[col].isna() if es_nulo else df[col] == nombre
                est = df[mask][estado_col].astype(str).str.lower()
                pend = int(est.str.contains("pendiente", na=False).sum())
                entr = int(est.str.contains("entregado", na=False).sum())
                linea += f" ({pend} pendientes, {entr} entregados)"
            partes.append(linea)

    return "\n".join(partes)


def generar_resumen(df: pd.DataFrame, col_agrup: str, estado_col, top_n: int = 5) -> list:
    counts = df.groupby(col_agrup, dropna=False).size().nlargest(top_n)
    lineas = []
    for nombre, total in counts.items():
        es_nulo = pd.isna(nombre) if not isinstance(nombre, str) else False
        nombre_str = "Sin datos" if es_nulo else str(nombre)

        if estado_col:
            subset = df[df[col_agrup].isna()] if es_nulo else df[df[col_agrup] == nombre]
            est = subset[estado_col].astype(str).str.lower()
            pend = int(est.str.contains("pendiente", na=False).sum())
            entr = int(est.str.contains("entregado", na=False).sum())
            lineas.append(
                f"<b>{nombre_str}</b> tiene <b>{total}</b> envíos "
                f"· {pend} pendientes · {entr} entregados"
            )
        else:
            lineas.append(f"<b>{nombre_str}</b> tiene <b>{total}</b> envíos")
    return lineas


# ─── PANTALLA DE BIENVENIDA ───────────────────────────────────────────────────
if "df" not in st.session_state:
    welcome_slot = st.empty()

    with welcome_slot.container():
        # Ratio amplio para que en mobile el contenido use casi todo el ancho
        _, col_c, _ = st.columns([0.15, 3, 0.15])
        with col_c:
            st.markdown("""
            <div class="welcome-wrap">
                <div class="welcome-icon">🚚</div>
                <p class="welcome-title">Bienvenido a LogiTrack 👋</p>
                <p class="welcome-sub">Tu dashboard interactivo de envíos</p>
                <div class="welcome-steps">
                    <div class="welcome-step">
                        <span class="step-num">1</span>
                        <span>Subí tu archivo Excel o CSV con los datos de tus envíos</span>
                    </div>
                    <div class="welcome-step">
                        <span class="step-num">2</span>
                        <span>Elegí qué querés ver: por cadete, zona, empresa o estado</span>
                    </div>
                    <div class="welcome-step">
                        <span class="step-num">3</span>
                        <span>¡Listo! Gráficos, KPIs y resúmenes automáticos al instante</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            archivo = st.file_uploader(
                "Subí tu archivo de envíos",
                type=["xlsx", "csv"],
                label_visibility="collapsed",
            )
            st.caption("Formatos aceptados: Excel (.xlsx) · CSV (.csv)")

    if archivo is not None:
        es_csv = archivo.name.lower().endswith(".csv")
        df_cargado, header_row = detectar_df(archivo, es_csv)

        if df_cargado is None or df_cargado.empty:
            st.error("El archivo está vacío o no se pudo leer.")
        else:
            col_map, match_map = {}, {}
            for target, info in COLUMN_TARGETS.items():
                col, mtype = buscar_columna(df_cargado.columns.tolist(), target, info["keywords"])
                col_map[target]   = col
                match_map[target] = mtype

            st.session_state.update({
                "df":         df_cargado,
                "filename":   archivo.name,
                "header_row": header_row,
                "col_map":    col_map,
                "match_map":  match_map,
            })
            welcome_slot.empty()
            st.rerun()

    st.markdown(FOOTER, unsafe_allow_html=True)
    st.stop()


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
df          = st.session_state["df"]
filename    = st.session_state["filename"]
header_row  = st.session_state["header_row"]
col_map     = st.session_state["col_map"]
match_map   = st.session_state["match_map"]
cols_reales = df.columns.tolist()

# ─ Header ─────────────────────────────────────────────────────────────────────
fila_info = f" · encabezado en fila {header_row + 1}" if header_row > 0 else ""
col_h, col_btn = st.columns([5, 1])
with col_h:
    # Nombre de archivo truncado con title para ver completo en tooltip
    fname_display = filename if len(filename) <= 28 else filename[:25] + "…"
    st.markdown(f"""
    <div class="dash-header">
        <span style="font-size:1.5rem">🚚</span>
        <div>
            <p class="dash-brand">LogiTrack</p>
            <p class="dash-meta">{len(df):,} envíos · {len(cols_reales)} columnas{fila_info}</p>
        </div>
        <span class="file-badge" title="{filename}">📂 {fname_display}</span>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nuevo", use_container_width=True, help="Cargar otro archivo"):
        for k in ["df", "filename", "header_row", "col_map", "match_map", "chat_history"]:
            st.session_state.pop(k, None)
        st.rerun()

# ─ Columnas detectadas ────────────────────────────────────────────────────────
BADGE = {"exacta": "✅ exacta", "parcial": "🔶 parcial", "similar": "🔷 similar"}
with st.expander("🔍 Columnas detectadas", expanded=False):
    filas = [
        {
            "Análisis":              info["label"],
            "Columna en tu archivo": col_map[t] or "—",
            "Coincidencia":          BADGE.get(match_map[t], "❌ no encontrada"),
        }
        for t, info in COLUMN_TARGETS.items()
    ]
    st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
    st.caption(
        f"Encabezado en fila {header_row + 1} · "
        f"Columnas disponibles: {', '.join(str(c) for c in cols_reales)}"
    )

# ─ KPIs ───────────────────────────────────────────────────────────────────────
estado_col_real = col_map.get("Estado")
total = len(df)
pendientes = entregados = 0

if estado_col_real:
    estados = df[estado_col_real].astype(str).str.lower().str.strip()
    pendientes = int(estados.str.contains("pendiente", na=False).sum())
    entregados = int(estados.str.contains("entregado", na=False).sum())

st.markdown('<p class="section-lbl">KPIs del período</p>', unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_PRIMARY}">
        <div class="kpi-num" style="color:{C_PRIMARY}">{total:,}</div>
        <div class="kpi-lbl">Total envíos</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_ACCENT}">
        <div class="kpi-num" style="color:{C_ACCENT}">{pendientes:,}</div>
        <div class="kpi-lbl">Pendientes</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{C_GREEN}">
        <div class="kpi-num" style="color:{C_GREEN}">{entregados:,}</div>
        <div class="kpi-lbl">Entregados</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ─ Selectores — full width, apilados para que sean usables en mobile ──────────
st.markdown('<p class="section-lbl">¿Qué querés analizar?</p>', unsafe_allow_html=True)
radio_opts, radio_map = [], {}
for target, info in COLUMN_TARGETS.items():
    col = col_map[target]
    label = f"{info['emoji']}  {info['label']}" + ("  ⚠️" if col is None else "")
    radio_opts.append(label)
    radio_map[label] = (col, info["label"])

analisis_label = st.radio(
    "analisis", options=radio_opts, horizontal=True, label_visibility="collapsed"
)
col_agrup, analisis_nombre = radio_map[analisis_label]

st.markdown('<p class="section-lbl">Tipo de gráfico</p>', unsafe_allow_html=True)
tipo_grafico = st.radio(
    "grafico",
    options=["📊 Barras", "🥧 Torta", "📈 Línea", "📉 Barras horiz."],
    horizontal=True,
    label_visibility="collapsed",
)

if col_agrup is None:
    st.warning(
        f"No se encontró una columna para **{analisis_nombre}**. "
        f"Columnas disponibles: {', '.join(str(c) for c in cols_reales)}"
    )
    st.markdown(FOOTER, unsafe_allow_html=True)
    st.stop()

# ─ Datos agrupados ────────────────────────────────────────────────────────────
df_grouped = (
    df.groupby(col_agrup, dropna=False)
    .size()
    .reset_index(name="Cantidad")
    .sort_values("Cantidad", ascending=False)
)
df_grouped[col_agrup] = df_grouped[col_agrup].fillna("Sin datos").astype(str)

st.divider()

# ─ Top 5 — HTML puro con scroll táctil en mobile ──────────────────────────────
st.markdown(f'<p class="section-lbl">🏆 Top 5 — {analisis_nombre}</p>', unsafe_allow_html=True)

top5 = df_grouped.head(5)
MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

if len(top5) > 0:
    cards_html = ""
    for i, (_, row) in enumerate(top5.iterrows()):
        cards_html += f"""
        <div class="top5-card">
            <div class="top5-medal">{MEDALS[i]}</div>
            <div class="top5-name">{row[col_agrup]}</div>
            <div class="top5-count">{row['Cantidad']}</div>
            <div class="top5-lbl">envíos</div>
        </div>"""
    st.markdown(f'<div class="top5-scroll">{cards_html}</div>', unsafe_allow_html=True)

# ─ Resumen en lenguaje natural ────────────────────────────────────────────────
lineas = generar_resumen(df, col_agrup, estado_col_real, top_n=5)
if lineas:
    items_html = "".join(f'<div class="resumen-line">{l}</div>' for l in lineas)
    st.markdown(f"""
    <div class="resumen-box">
        <div class="resumen-titulo">📝 Resumen automático</div>
        {items_html}
    </div>
    """, unsafe_allow_html=True)

# ─ Gráfico ────────────────────────────────────────────────────────────────────
st.markdown(f'<p class="section-lbl">Gráfico — {analisis_nombre}</p>', unsafe_allow_html=True)

tick_angle = -30 if df_grouped[col_agrup].str.len().max() > 10 else 0
# Altura reducida para que quepa bien en mobile sin ser demasiado chica en desktop
CHART_HEIGHT = 380
LAYOUT = dict(
    showlegend=False,
    font_family="Inter, Arial, sans-serif",
    margin=dict(t=20, b=50, l=10, r=10),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=CHART_HEIGHT,
)

if tipo_grafico == "📊 Barras":
    fig = px.bar(
        df_grouped, x=col_agrup, y="Cantidad", color=col_agrup,
        color_discrete_sequence=CHART_COLORS, template="plotly_white",
        text="Cantidad", labels={col_agrup: analisis_nombre, "Cantidad": "Envíos"},
    )
    fig.update_traces(textposition="outside", textfont_size=12)
    fig.update_layout(**LAYOUT, xaxis_tickangle=tick_angle)

elif tipo_grafico == "🥧 Torta":
    fig = px.pie(
        df_grouped, names=col_agrup, values="Cantidad",
        color_discrete_sequence=CHART_COLORS, hole=0.35,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(**{**LAYOUT, "height": CHART_HEIGHT + 30})

elif tipo_grafico == "📈 Línea":
    df_line = df_grouped.sort_values(col_agrup)
    fig = px.line(
        df_line, x=col_agrup, y="Cantidad", markers=True,
        color_discrete_sequence=[C_PRIMARY], template="plotly_white",
        labels={col_agrup: analisis_nombre, "Cantidad": "Envíos"},
    )
    fig.update_traces(line_width=3, marker_size=8, line_color=C_PRIMARY)
    fig.update_layout(**LAYOUT, xaxis_tickangle=tick_angle)

else:  # 📉 Barras horiz.
    df_horiz = df_grouped.sort_values("Cantidad", ascending=True)
    fig = px.bar(
        df_horiz, x="Cantidad", y=col_agrup, orientation="h",
        color=col_agrup, color_discrete_sequence=CHART_COLORS,
        template="plotly_white", text="Cantidad",
        labels={col_agrup: analisis_nombre, "Cantidad": "Envíos"},
    )
    fig.update_traces(textposition="outside", textfont_size=12)
    fig.update_layout(**{**LAYOUT, "height": max(CHART_HEIGHT, len(df_grouped) * 38)},
                      yaxis_tickfont_size=11)

# responsive=True hace que Plotly reescale el gráfico al ancho del contenedor
st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": False})

# ─ Exportar PNG ───────────────────────────────────────────────────────────────
try:
    img_bytes = fig.to_image(format="png", width=1400, height=520, scale=2)
    st.download_button(
        "📷 Exportar gráfico como PNG",
        data=img_bytes,
        file_name=f"logitrack_{analisis_nombre.lower().replace(' ', '_').replace('/', '-')}.png",
        mime="image/png",
    )
except Exception:
    st.caption("💡 Para exportar el gráfico como imagen instalá: `pip install kaleido`")

st.divider()

# ─ Tabla detalle ──────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Detalle de envíos</p>', unsafe_allow_html=True)

cols_tabla = [col_agrup]
for extra_target, extra_kw in [
    ("Nombre Destinatario", ["destinatario", "nombre destinatario", "receptor", "cliente destino"]),
    ("Localidad",           ["localidad", "ciudad", "municipio", "partido"]),
    ("Provincia",           ["provincia", "prov"]),
    ("Fecha estado",        ["fecha estado", "fecha", "date", "fecha_estado"]),
]:
    extra_col, _ = buscar_columna(cols_reales, extra_target, extra_kw)
    if extra_col and extra_col != col_agrup and extra_col not in cols_tabla:
        cols_tabla.append(extra_col)

if estado_col_real and estado_col_real != col_agrup and estado_col_real not in cols_tabla:
    cols_tabla.append(estado_col_real)

df_tabla = df[cols_tabla] if len(cols_tabla) > 1 else df
st.dataframe(df_tabla, use_container_width=True, height=300, hide_index=True)

# ─ Exportar Excel ─────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Exportar datos</p>', unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
    df_grouped.to_excel(writer, sheet_name="Resumen", index=False)
    df.to_excel(writer, sheet_name="Datos completos", index=False)
buf.seek(0)

st.download_button(
    "📥 Descargar resumen en Excel",
    data=buf,
    file_name="logitrack_resumen.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# ─── Chat con IA ──────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div class="chat-wrap">
    <p class="chat-title">💬 Preguntale a tus datos</p>
    <p class="chat-desc">Hacé preguntas sobre tus envíos y obtendrás respuestas basadas en tu archivo.</p>
    <span class="chat-ex-label">Ejemplos</span>
    <span class="chat-ex">¿Cuál es el chofer con más pendientes?</span>
    <span class="chat-ex">¿Qué zona tiene más problemas?</span>
    <span class="chat-ex">Dame un resumen del día</span>
    <span class="chat-ex">¿Cuántos envíos entregó cada empresa?</span>
</div>
""", unsafe_allow_html=True)

groq_key = os.environ.get("GROQ_API_KEY")

if not groq_key:
    st.markdown(f"""
    <div class="no-key-box">
        🔑 <strong>Para activar el chat</strong> configurá tu API key de Groq:<br>
        <code>$env:GROQ_API_KEY = "tu-api-key"</code> &nbsp;(PowerShell, antes de ejecutar la app)<br>
        <small>Obtené tu key gratis en <strong>console.groq.com</strong></small>
    </div>
    """, unsafe_allow_html=True)
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribí tu pregunta sobre los envíos..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                try:
                    from groq import Groq  # lazy import — no rompe si no está instalado
                    client = Groq(api_key=groq_key)

                    contexto = construir_contexto(df, col_map)
                    system_msg = (
                        "Sos un asistente de análisis logístico. "
                        "Respondé siempre en español, de forma concisa y directa. "
                        "Usá los datos reales del Excel para responder con números concretos. "
                        "Si no podés responder con los datos disponibles, decilo claramente. "
                        "No respondas preguntas fuera del tema logístico o de los envíos.\n\n"
                        f"DATOS DEL EXCEL:\n{contexto}"
                    )

                    messages_groq = [{"role": "system", "content": system_msg}]
                    for h in st.session_state.chat_history[:-1]:
                        messages_groq.append({"role": h["role"], "content": h["content"]})
                    messages_groq.append({"role": "user", "content": prompt})

                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages_groq,
                        max_tokens=600,
                        temperature=0.4,
                    )
                    answer = resp.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

                except ImportError:
                    msg = "Instalá el paquete de Groq: `pip install groq`"
                    st.warning(msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": msg})
                except Exception as e:
                    msg = f"Error al conectar con Groq: {e}"
                    st.error(msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": msg})

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(FOOTER, unsafe_allow_html=True)
