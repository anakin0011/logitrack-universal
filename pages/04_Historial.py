import sys
import io
import pathlib
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.auth import login_requerido, logout, get_nombre, es_admin
from utils.turnos import leer_csv

st.set_page_config(
    page_title="Historial · LogiTrack",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

C_PRIMARY   = "#FF8C69"
C_SECONDARY = "#FFF3C4"
C_TEXT      = "#2D2D2D"
C_MUTED     = "#9E9E9E"
C_GREEN     = "#52B788"

login_requerido()
_nombre = get_nombre()

st.markdown(f"""
<style>
[data-testid="collapsedControl"] {{ display: none !important; }}
.stApp {{ background: #FFFFFF; }}
.block-container {{ padding-top: 1.5rem !important; max-width: 1100px; }}
.page-header {{
    background: {C_SECONDARY}; border-radius: 12px;
    padding: 0.75rem 1.2rem; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
}}
.page-brand {{ font-size: 1.2rem; font-weight: 800; color: {C_TEXT}; margin: 0; }}
.page-meta  {{ font-size: 0.78rem; color: {C_MUTED}; margin: 0; }}
.section-lbl {{
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: {C_MUTED}; margin: 1.2rem 0 0.4rem;
}}
.kpi-card {{
    background: white; border-radius: 12px; padding: 1rem 0.8rem;
    border-top: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
}}
.kpi-num {{ font-size: 1.9rem; font-weight: 800; line-height: 1; }}
.kpi-lbl {{ font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: {C_MUTED}; margin-top: 0.3rem; }}
.app-footer {{
    margin-top: 3rem; padding-top: 1.2rem;
    border-top: 2px solid {C_SECONDARY};
    text-align: center; color: {C_MUTED}; font-size: 0.82rem;
}}
</style>
""", unsafe_allow_html=True)

# ─ Header ─────────────────────────────────────────────────────────────────────
col_hdr, col_salir = st.columns([6, 1])
with col_hdr:
    rol_badge = "👑 Admin" if es_admin() else "👤 Coordinadora"
    st.markdown(f"""
    <div class="page-header">
        <span style="font-size:1.5rem">📁</span>
        <div>
            <p class="page-brand">Historial de Turnos</p>
            <p class="page-meta">{rol_badge} {_nombre}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_salir:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()

# ─ Cargar datos ───────────────────────────────────────────────────────────────
df_raw = leer_csv()

if df_raw.empty:
    st.info("Sin historial disponible aún. Las incidencias registradas aparecerán acá.")
    st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
    st.stop()

df_raw["_fecha"] = df_raw["turno_id"].str.rsplit("_", n=1).str[0]
df_raw["_turno"] = df_raw["turno_id"].str.rsplit("_", n=1).str[1]

# ─ Filtros ────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Filtros</p>', unsafe_allow_html=True)
cf1, cf2, cf3 = st.columns([2, 1, 1.5])

with cf1:
    hoy       = datetime.now().date()
    rango     = st.date_input(
        "Período",
        value=(hoy - timedelta(days=7), hoy),
        format="DD/MM/YYYY",
        label_visibility="collapsed",
    )
    fecha_desde = rango[0] if isinstance(rango, (list, tuple)) and len(rango) == 2 else hoy - timedelta(days=7)
    fecha_hasta = rango[1] if isinstance(rango, (list, tuple)) and len(rango) == 2 else hoy

with cf2:
    turno_opciones = ["Todos"] + sorted(df_raw["_turno"].dropna().unique().tolist())
    turno_filtro   = st.selectbox("Turno", turno_opciones, label_visibility="collapsed")

with cf3:
    coords_unicas   = ["Todos"] + sorted(df_raw["coordinadora"].dropna().unique().tolist())
    coord_filtro    = st.selectbox("Coordinadora", coords_unicas, label_visibility="collapsed")

# Aplicar filtros
mask = (
    (df_raw["_fecha"] >= str(fecha_desde)) &
    (df_raw["_fecha"] <= str(fecha_hasta))
)
if turno_filtro != "Todos":
    mask &= df_raw["_turno"] == turno_filtro
if coord_filtro != "Todos":
    mask &= df_raw["coordinadora"] == coord_filtro

df = df_raw[mask].copy()

if df.empty:
    st.warning("Sin datos para el período y filtros seleccionados.")
    st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
    st.stop()

# ─ KPIs globales del período ──────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Totales del período</p>', unsafe_allow_html=True)
g1, g2, g3, g4, g5 = st.columns(5)
turnos_unicos    = df["turno_id"].nunique()
total_inc        = len(df)
total_res        = int((df["estado"] == "resuelto").sum())
total_pend       = int((df["estado"] == "pendiente").sum())
tasa_res         = f"{total_res / total_inc * 100:.0f}%" if total_inc > 0 else "—"

for col_g, num, lbl, color in [
    (g1, turnos_unicos, "Turnos en el período",  C_PRIMARY),
    (g2, total_inc,     "Incidencias totales",   "#7B68EE"),
    (g3, total_res,     "Resueltas",             C_GREEN),
    (g4, total_pend,    "Pendientes activos",    "#C0392B" if total_pend > 0 else C_MUTED),
    (g5, tasa_res,      "Tasa de resolución",    C_GREEN),
]:
    with col_g:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div class="kpi-num" style="color:{color}">{num}</div>
            <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ─ Tabla resumen por turno ────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Resumen por turno</p>', unsafe_allow_html=True)

def _coords(series):
    vals = series[series != ""].unique()
    return ", ".join(sorted(vals)) if len(vals) > 0 else "—"

resumen = (
    df.groupby("turno_id")
    .agg(
        Fecha=("_fecha",       "first"),
        Turno=("_turno",       "first"),
        Total=("tracking",     "count"),
        Resueltas=("estado",   lambda x: int((x == "resuelto").sum())),
        Transferidas=("estado",lambda x: int((x == "transferido").sum())),
        Pendientes=("estado",  lambda x: int((x == "pendiente").sum())),
        Heredadas=("heredada_de", lambda x: int((x != "").sum())),
        Coordinadora=("coordinadora", _coords),
    )
    .reset_index()
)

resumen["Estado turno"] = resumen.apply(
    lambda r: "✅ Cerrado"  if r["Transferidas"] > 0 or (r["Pendientes"] == 0 and r["Total"] > 0)
              else "⏳ Abierto",
    axis=1,
)
resumen["Turno"] = resumen["Turno"].str.capitalize()
resumen = resumen.sort_values("turno_id", ascending=False).reset_index(drop=True)
resumen = resumen.drop(columns=["turno_id"])

COLS_RESUMEN = ["Fecha", "Turno", "Coordinadora", "Total", "Resueltas", "Heredadas", "Transferidas", "Pendientes", "Estado turno"]

def _style_resumen(row):
    if row["Pendientes"] > 0:
        return ["background-color:#FFF8E1; color:#E65100; font-weight:600;"] * len(row)
    if "Cerrado" in str(row.get("Estado turno", "")):
        return ["background-color:#F1F8E9; color:#2E7D32;"] * len(row)
    return [""] * len(row)

st.dataframe(
    resumen[COLS_RESUMEN].style.apply(_style_resumen, axis=1),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ─ Detalle de turno ───────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Detalle de incidencias por turno</p>', unsafe_allow_html=True)

turnos_disponibles = (
    df.groupby("turno_id")
    .agg(fecha=("_fecha", "first"), turno=("_turno", "first"))
    .reset_index()
    .sort_values("turno_id", ascending=False)
)
opciones_label = {
    row["turno_id"]: f"{row['fecha']}  ·  {row['turno'].capitalize()}"
    for _, row in turnos_disponibles.iterrows()
}

turno_sel_id = st.selectbox(
    "Seleccioná un turno para ver el detalle",
    options=list(opciones_label.keys()),
    format_func=lambda x: opciones_label[x],
    label_visibility="collapsed",
)

if turno_sel_id:
    df_det = df[df["turno_id"] == turno_sel_id].copy()
    COLS_DET = ["timestamp", "coordinadora", "tracking", "cadete", "empresa", "zona",
                "tipo", "prioridad", "estado", "descripcion", "heredada_de", "resuelto_por"]
    COLS_DET  = [c for c in COLS_DET if c in df_det.columns]
    df_det    = df_det[COLS_DET].rename(columns=str.capitalize).sort_values("Timestamp", ascending=False).reset_index(drop=True)

    ESTILOS_EST = {
        "resuelto":    "background-color:#E8F5E9; color:#2E7D32; font-weight:600;",
        "transferido": "background-color:#E3F2FD; color:#1565C0; font-weight:600;",
        "pendiente":   "background-color:#FFEBEE; color:#C0392B; font-weight:700;",
    }

    def _style_det(row):
        return [ESTILOS_EST.get(row.get("Estado", "").lower(), "")] * len(row)

    st.dataframe(
        df_det.style.apply(_style_det, axis=1),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"{len(df_det)} incidencia(s) · Turno {opciones_label[turno_sel_id]}")

st.divider()

# ─ Exportar ───────────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Exportar</p>', unsafe_allow_html=True)

def _a_excel(df_resumen, df_completo) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df_resumen.to_excel(writer, sheet_name="Resumen por turno", index=False)
        df_completo.to_excel(writer, sheet_name="Detalle completo", index=False)
        for sheet in writer.sheets.values():
            sheet.set_column(0, 20, 18)
    return buf.getvalue()

df_completo_exp = df[
    [c for c in ["turno_id", "timestamp", "coordinadora", "tracking", "cadete",
                 "empresa", "zona", "tipo", "prioridad", "estado",
                 "descripcion", "heredada_de", "resuelto_por"] if c in df.columns]
].sort_values(["turno_id", "timestamp"], ascending=[False, False])

nombre_archivo = f"historial_{fecha_desde}_{fecha_hasta}.xlsx"

ex1, ex2 = st.columns([1, 3])
with ex1:
    st.download_button(
        "⬇️ Descargar Excel",
        data=_a_excel(resumen[COLS_RESUMEN], df_completo_exp),
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with ex2:
    st.caption(f"Exporta **Resumen por turno** + **Detalle completo** en dos hojas · {len(df_completo_exp)} registros filtrados")

st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
