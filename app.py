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
}}
.dash-brand {{ font-size: 1.2rem; font-weight: 800; color: {C_TEXT}; margin: 0; }}
.dash-meta  {{ font-size: 0.78rem; color: {C_MUTED}; margin: 0; }}
.file-badge {{
    margin-left: auto; background: {C_PRIMARY}; color: white;
    border-radius: 999px; padding: 0.2rem 0.9rem;
    font-size: 0.74rem; font-weight: 700; white-space: nowrap;
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

/* Top 5 */
.top5-card {{
    background: {C_SECONDARY}; border-radius: 12px; padding: 1rem 0.75rem;
    text-align: center; border-bottom: 3px solid {C_PRIMARY}; height: 100%;
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
        _, col_c, _ = st.columns([1, 2, 1])
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

# ─ Header ────────────────────────────────────────────────────────────────────
fila_info = f" · encabezado en fila {header_row + 1}" if header_row > 0 else ""
col_h, col_btn = st.columns([5, 1])
with col_h:
    st.markdown(f"""
    <div class="dash-header">
        <span style="font-size:1.5rem">🚚</span>
        <div>
            <p class="dash-brand">LogiTrack</p>
            <p class="dash-meta">{len(df):,} envíos · {len(cols_reales)} columnas{fila_info}</p>
        </div>
        <span class="file-badge">📂 {filename}</span>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nuevo archivo", use_container_width=True):
        for k in ["df", "filename", "header_row", "col_map", "match_map"]:
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

# ─ Selectores ─────────────────────────────────────────────────────────────────
sel1, sel2 = st.columns([3, 2])

with sel1:
    st.markdown('<p class="section-lbl">¿Qué querés analizar?</p>', unsafe_allow_html=True)
    radio_opts, radio_map = [], {}
    for target, info in COLUMN_TARGETS.items():
        col = col_map[target]
        label = f"{info['emoji']}  {info['label']}" + ("  ⚠️" if col is None else "")
        radio_opts.append(label)
        radio_map[label] = (col, info["label"])

    analisis_label = st.radio("analisis", options=radio_opts, horizontal=True,
                              label_visibility="collapsed")
    col_agrup, analisis_nombre = radio_map[analisis_label]

with sel2:
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

# ─ Top 5 ──────────────────────────────────────────────────────────────────────
st.markdown(f'<p class="section-lbl">🏆 Top 5 — {analisis_nombre}</p>', unsafe_allow_html=True)

top5 = df_grouped.head(5)
MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

if len(top5) > 0:
    tcols = st.columns(len(top5))
    for i, (_, row) in enumerate(top5.iterrows()):
        with tcols[i]:
            st.markdown(f"""
            <div class="top5-card">
                <div class="top5-medal">{MEDALS[i]}</div>
                <div class="top5-name">{row[col_agrup]}</div>
                <div class="top5-count">{row['Cantidad']}</div>
                <div class="top5-lbl">envíos</div>
            </div>""", unsafe_allow_html=True)

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
LAYOUT = dict(
    showlegend=False,
    font_family="Inter, Arial, sans-serif",
    margin=dict(t=20, b=50, l=10, r=10),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=430,
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
    fig.update_layout(**{**LAYOUT, "height": 460})

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
    fig.update_layout(**{**LAYOUT, "height": max(400, len(df_grouped) * 38)},
                      yaxis_tickfont_size=11)

st.plotly_chart(fig, use_container_width=True)

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

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(FOOTER, unsafe_allow_html=True)
