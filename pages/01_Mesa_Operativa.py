import sys
import pathlib
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.auth import login_requerido, logout, get_nombre, es_admin, es_demo, calcular_turno
from utils.db import insertar, leer, leer_todo
from utils.styles import inject_css, badge, header_html, prio_level
import utils.styles as DS

st.set_page_config(
    page_title="Mesa Operativa · LogiTrack",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TIPOS_NOVEDAD = [
    "Demora en entrega",
    "Destinatario ausente",
    "Dirección incorrecta / no encontrada",
    "Rechazo de mercadería",
    "Paquete dañado",
    "Faltante",
    "Problema con cadete",
    "Otro",
]

login_requerido()

_nombre   = get_nombre()
_turno, _turno_id = calcular_turno()

inject_css()

# ─ Header ─────────────────────────────────────────────────────────────────────
col_hdr, col_salir = st.columns([6, 1])
with col_hdr:
    rol_badge = "Admin" if es_admin() else ("Demo" if es_demo() else "Coordinadora")
    st.markdown(
        header_html("📋", "Mesa Operativa",
                    f"Turno {_turno.capitalize()} · {rol_badge} {_nombre}"),
        unsafe_allow_html=True,
    )
with col_salir:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()

# Mensaje de éxito tras registrar
if "_ok_msg" in st.session_state:
    st.success(st.session_state.pop("_ok_msg"))

# ─ Búsqueda de tracking ───────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Buscar tracking en el corte operativo</p>', unsafe_allow_html=True)

df_corte     = st.session_state.get("df")
col_map      = st.session_state.get("col_map", {})
tracking_col = next((c for c in (df_corte.columns if df_corte is not None else []) if "tracking" in str(c).lower()), None)
cadete_col   = col_map.get("Cadete")
empresa_col  = col_map.get("Nombre Fantasia")
zona_col     = col_map.get("Zona")
estado_col   = col_map.get("Estado")

col_inp, col_btn = st.columns([4, 1])
with col_inp:
    nro_tracking = st.text_input(
        "tracking_search", label_visibility="collapsed",
        placeholder="Ingresá el número de tracking…",
        value=st.session_state.get("_last_search", ""),
    )
with col_btn:
    buscar = st.button("🔍 Buscar", use_container_width=True)

if buscar and nro_tracking.strip():
    st.session_state["_last_search"] = nro_tracking.strip()
    resultado = {"tracking": nro_tracking.strip(), "cadete": "", "empresa": "", "zona": "", "estado": ""}
    if df_corte is not None and tracking_col and tracking_col in df_corte.columns:
        match = df_corte[df_corte[tracking_col].astype(str).str.strip() == nro_tracking.strip()]
        if not match.empty:
            row = match.iloc[0]
            resultado.update({
                "cadete":  str(row[cadete_col])  if cadete_col  and cadete_col  in df_corte.columns else "",
                "empresa": str(row[empresa_col]) if empresa_col and empresa_col in df_corte.columns else "",
                "zona":    str(row[zona_col])    if zona_col    and zona_col    in df_corte.columns else "",
                "estado":  str(row[estado_col])  if estado_col  and estado_col  in df_corte.columns else "",
            })
        else:
            st.warning("⚠️ Tracking no encontrado en el corte — completá los datos manualmente.")
    elif df_corte is None:
        st.info("ℹ️ No hay corte cargado. Completá los datos manualmente.")
    st.session_state["_lookup"] = resultado

lookup = st.session_state.get("_lookup", {})

if lookup.get("tracking"):
    campos = [
        ("📦", "Tracking", lookup["tracking"]),
        ("🚴", "Cadete",   lookup.get("cadete",  "—") or "—"),
        ("🏢", "Empresa",  lookup.get("empresa", "—") or "—"),
        ("🗺️", "Zona",    lookup.get("zona",    "—") or "—"),
        ("📋", "Estado en corte", lookup.get("estado", "—") or "—"),
    ]
    filas = "".join(
        f'<div class="lookup-row">{icono} <b>{campo}:</b> {valor}</div>'
        for icono, campo, valor in campos
    )
    st.markdown(f'<div class="lookup-box">{filas}</div>', unsafe_allow_html=True)

# ─ Formulario ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Nueva incidencia</p>', unsafe_allow_html=True)

with st.form("form_incidencia", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        f_tracking = st.text_input("Tracking *",  value=lookup.get("tracking", ""), placeholder="nro. de tracking")
        f_cadete   = st.text_input("Cadete",      value=lookup.get("cadete",   ""), placeholder="nombre del cadete")
        f_empresa  = st.text_input("Empresa",     value=lookup.get("empresa",  ""), placeholder="empresa remitente")
    with col_b:
        f_zona      = st.text_input("Zona",       value=lookup.get("zona",     ""), placeholder="zona de entrega")
        f_tipo      = st.selectbox("Tipo de novedad *", TIPOS_NOVEDAD)
        f_prioridad = st.radio("Prioridad *", ["Alta", "Media", "Baja"], horizontal=True)

    f_desc    = st.text_area("Descripción *", height=90, placeholder="Describí la novedad con detalle…")
    registrar = st.form_submit_button("📋 Registrar Incidencia", use_container_width=True)

if registrar:
    if not f_tracking.strip():
        st.warning("⚠️ El número de tracking es obligatorio.")
    elif not f_desc.strip():
        st.warning("⚠️ La descripción es obligatoria.")
    elif es_demo():
        st.success("✅ Incidencia registrada (modo demo — no se guardó en base de datos)")
    else:
        nueva = {
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "turno_id":     _turno_id,
            "turno":        _turno,
            "coordinadora": _nombre,
            "tracking":     f_tracking.strip(),
            "cadete":       f_cadete.strip(),
            "empresa":      f_empresa.strip(),
            "zona":         f_zona.strip(),
            "tipo":         f_tipo,
            "descripcion":  f_desc.strip(),
            "prioridad":    f_prioridad,
            "estado":       "pendiente",
            "heredada_de":  "",
            "resuelto_por": "",
        }
        insertar(nueva)
        st.session_state.pop("_lookup", None)
        st.session_state.pop("_last_search", None)
        st.session_state["_ok_msg"] = f"✅ Incidencia registrada · Tracking **{f_tracking.strip()}** · Prioridad **{f_prioridad}**"
        st.rerun()

# ─ Tabla del turno ────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p class="section-lbl">Incidencias del turno</p>', unsafe_allow_html=True)

_ESTILOS_PRIO = {
    "Alta":  f"background-color:{DS.CRITICAL_BG}; color:{DS.CRITICAL}; font-weight:600;",
    "Media": f"background-color:{DS.WARNING_BG};  color:{DS.WARNING};  font-weight:500;",
    "Baja":  f"background-color:{DS.SUCCESS_BG};  color:{DS.SUCCESS};",
}

def _style_fila(row):
    return [_ESTILOS_PRIO.get(row.get("Prioridad", ""), "")] * len(row)

hist = leer_todo() if es_admin() else leer(_turno_id)
if es_admin() and not hist.empty and "turno_id" in hist.columns:
    hoy  = datetime.now().strftime("%Y-%m-%d")
    hist = hist[hist["turno_id"].str.startswith(hoy)]

if hist.empty:
    st.info("Sin incidencias registradas en este turno.")
else:
    cols_vis = ["timestamp", "tracking", "cadete", "empresa", "zona", "tipo", "prioridad", "estado"]
    cols_vis  = [c for c in cols_vis if c in hist.columns]
    tabla     = (
        hist[cols_vis]
        .rename(columns=str.capitalize)
        .sort_values("Timestamp", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(
        tabla.style.apply(_style_fila, axis=1),
        use_container_width=True, hide_index=True,
    )
    altas = (hist["prioridad"] == "Alta").sum()
    if es_demo():
        st.caption(f"Total: **{len(hist)}** incidencia(s) · Alta prioridad: **{altas}** · Turno {_turno.capitalize()}")
    else:
        col_info, col_dl = st.columns([3, 1])
        with col_info:
            st.caption(f"Total: **{len(hist)}** incidencia(s) · Alta prioridad: **{altas}** · Turno {_turno.capitalize()}")
        with col_dl:
            csv_bytes = hist.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Exportar CSV", data=csv_bytes,
                file_name=f"incidencias_{_turno_id}.csv",
                mime="text/csv", use_container_width=True,
            )

st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Mesa Operativa · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
