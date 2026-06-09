import sys
import pathlib
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.auth import login_requerido, logout, get_nombre, es_admin, calcular_turno
from utils.turnos import (
    turno_siguiente_id,
    incidencias_de,
    resolver_incidencias,
    heredar_pendientes,
)

st.set_page_config(
    page_title="Handoff · LogiTrack",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

C_PRIMARY   = "#FF8C69"
C_SECONDARY = "#FFF3C4"
C_ACCENT    = "#FF6B6B"
C_TEXT      = "#2D2D2D"
C_MUTED     = "#9E9E9E"
C_GREEN     = "#52B788"

login_requerido()

_nombre          = get_nombre()
_turno, _turno_id = calcular_turno()
_next_id         = turno_siguiente_id(_turno, _turno_id)
_next_nombre     = _next_id.rsplit("_", 1)[1].capitalize()

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
    background: white; border-radius: 12px; padding: 1.2rem 1rem;
    border-top: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
}}
.kpi-num {{ font-size: 2.2rem; font-weight: 800; line-height: 1; }}
.kpi-lbl {{ font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: {C_MUTED}; margin-top: 0.35rem; }}
.resumen-box {{
    background: {C_SECONDARY}; border-radius: 12px;
    padding: 1.1rem 1.4rem; margin: 0.8rem 0;
    border-left: 4px solid {C_PRIMARY};
    font-size: 0.92rem; color: {C_TEXT};
    line-height: 1.7;
}}
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
        <span style="font-size:1.5rem">🔄</span>
        <div>
            <p class="page-brand">Handoff de Turno</p>
            <p class="page-meta">Turno actual: <b>{_turno.capitalize()}</b> · {_turno_id} · {rol_badge} {_nombre}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_salir:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()

# Mensajes flash (post-rerun)
if "_flash" in st.session_state:
    tipo, texto = st.session_state.pop("_flash")
    {"success": st.success, "info": st.info, "warning": st.warning}.get(tipo, st.info)(texto)

# ─ Datos del turno ────────────────────────────────────────────────────────────
df_all = incidencias_de(_turno_id)

df_heredadas = df_all[df_all["heredada_de"] != ""].copy() if not df_all.empty else pd.DataFrame()
df_nuevas    = df_all[df_all["heredada_de"] == ""].copy() if not df_all.empty else pd.DataFrame()

pend_heredadas = int((df_heredadas["estado"] == "pendiente").sum()) if not df_heredadas.empty else 0
res_heredadas  = int((df_heredadas["estado"] == "resuelto").sum())  if not df_heredadas.empty else 0
pend_nuevas    = int((df_nuevas["estado"]    == "pendiente").sum()) if not df_nuevas.empty    else 0
total_nuevas   = len(df_nuevas)
total_heredar  = pend_heredadas + pend_nuevas

# ─ KPIs ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Resumen del turno</p>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
for col_k, num, lbl, color in [
    (k1, len(df_heredadas), "Heredadas del turno anterior",   C_ACCENT),
    (k2, res_heredadas,     "Heredadas resueltas este turno", C_GREEN),
    (k3, total_nuevas,      "Nuevas registradas este turno",  C_PRIMARY),
    (k4, total_heredar,     "Pasan al turno siguiente",       "#C0392B" if total_heredar > 0 else C_MUTED),
]:
    with col_k:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div class="kpi-num" style="color:{color}">{num}</div>
            <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ─ A. Pendientes heredados ────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">⚠️ Heredados del turno anterior — marcá los que resolviste</p>', unsafe_allow_html=True)

ESTILOS_PRIO = {
    "Alta":  "background-color:#FFEBEE; color:#C0392B; font-weight:700;",
    "Media": "background-color:#FFF8E1; color:#E65100; font-weight:600;",
    "Baja":  "background-color:#E8F5E9; color:#2E7D32;",
}
ESTILOS_EST = {
    "resuelto": "background-color:#E8F5E9; color:#2E7D32; font-weight:600;",
}

def _style_tabla(row):
    est = row.get("Estado", "")
    if est == "resuelto":
        return [ESTILOS_EST["resuelto"]] * len(row)
    return [ESTILOS_PRIO.get(row.get("Prioridad", ""), "")] * len(row)

if df_heredadas.empty:
    st.success("✅ No hay pendientes heredados en este turno.")
else:
    COLS_ED = ["tracking", "cadete", "empresa", "zona", "tipo", "prioridad", "estado", "heredada_de"]
    COLS_ED  = [c for c in COLS_ED if c in df_heredadas.columns]
    df_edit  = df_heredadas[COLS_ED].rename(columns=str.capitalize).reset_index(drop=True)
    df_edit.insert(0, "Resuelto", df_edit["Estado"] == "resuelto")

    edited = st.data_editor(
        df_edit,
        column_config={
            "Resuelto":    st.column_config.CheckboxColumn("✅", help="Marcá si lo resolviste"),
            "Heredada_de": st.column_config.TextColumn("Turno origen", width="medium"),
            "Estado":      st.column_config.TextColumn("Estado", width="small"),
            "Prioridad":   st.column_config.TextColumn("Prioridad", width="small"),
        },
        disabled=[c for c in df_edit.columns if c != "Resuelto"],
        use_container_width=True,
        hide_index=True,
        key="editor_heredadas",
    )

    # Detectar cambios: filas donde el checkbox pasó a True y el estado era pendiente
    nuevos_resueltos = edited[
        (edited["Resuelto"] == True) & (edited["Estado"] == "pendiente")
    ]["Tracking"].tolist() if "Tracking" in edited.columns else []

    if nuevos_resueltos:
        if st.button(f"✅ Marcar {len(nuevos_resueltos)} como resuelto(s)", type="primary"):
            resolver_incidencias(nuevos_resueltos, _turno_id, _nombre)
            st.session_state["_flash"] = ("success", f"✅ {len(nuevos_resueltos)} incidencia(s) marcada(s) como resuelta(s).")
            st.rerun()

st.divider()

# ─ B. Nuevas del turno actual ─────────────────────────────────────────────────
st.markdown('<p class="section-lbl">📋 Incidencias nuevas de este turno</p>', unsafe_allow_html=True)

if df_nuevas.empty:
    st.info("Sin incidencias registradas en este turno aún.")
else:
    COLS_NUE = ["tracking", "cadete", "empresa", "zona", "tipo", "prioridad", "estado"]
    COLS_NUE  = [c for c in COLS_NUE if c in df_nuevas.columns]
    tabla_nue = df_nuevas[COLS_NUE].rename(columns=str.capitalize).reset_index(drop=True)
    st.dataframe(
        tabla_nue.style.apply(_style_tabla, axis=1),
        use_container_width=True, hide_index=True,
    )

st.divider()

# ─ Resumen y cierre ───────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Cierre del turno</p>', unsafe_allow_html=True)

origen_label = _turno_id.replace("_", " · ")
if total_heredar > 0:
    resumen_texto = (
        f"Al cerrar el turno <b>{_turno.capitalize()}</b>, pasarán <b>{total_heredar} pendiente(s)</b> "
        f"al turno <b>{_next_nombre}</b>: "
        f"{pend_heredadas} heredado(s) sin resolver + {pend_nuevas} nuevo(s) de este turno."
    )
else:
    resumen_texto = (
        f"Al cerrar el turno <b>{_turno.capitalize()}</b>, el turno <b>{_next_nombre}</b> "
        f"<b>no recibirá pendientes</b>. ✅"
    )

st.markdown(f'<div class="resumen-box">{resumen_texto}</div>', unsafe_allow_html=True)

if not st.session_state.get("_confirmar_cierre"):
    if st.button("🔒 Cerrar Turno y Pasar Pendientes →", use_container_width=True):
        st.session_state["_confirmar_cierre"] = True
        st.rerun()
else:
    accion = f"pasar **{total_heredar}** pendiente(s) al turno **{_next_nombre}**" if total_heredar > 0 else "cerrar el turno sin pendientes"
    st.warning(f"⚠️ ¿Confirmás el cierre del turno **{_turno.capitalize()}**? Esto va a {accion}.")
    col_si, col_no = st.columns(2)
    with col_si:
        if st.button("✅ Sí, cerrar turno", type="primary", use_container_width=True):
            n = heredar_pendientes(_turno_id, _next_id, _nombre)
            st.session_state.pop("_confirmar_cierre", None)
            msg = f"✅ Turno cerrado. Se pasaron **{n}** pendiente(s) al turno {_next_nombre}." if n > 0 else "✅ Turno cerrado sin pendientes."
            st.session_state["_flash"] = ("success", msg)
            st.rerun()
    with col_no:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.pop("_confirmar_cierre", None)
            st.rerun()

st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
