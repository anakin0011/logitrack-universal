import sys
import pathlib
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.auth import login_requerido, logout, get_nombre, es_admin, es_demo, calcular_turno
from utils.db import actualizar_estado
from utils.turnos import turno_siguiente_id, incidencias_de, heredar_pendientes
from utils.styles import inject_css, badge, header_html, kpi_card, prio_level
import utils.styles as DS

st.set_page_config(
    page_title="Handoff · LogiTrack",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ESTADOS = {
    "pendiente":  {"label": "Pendiente",  "color": DS.WARNING,  "bg": DS.WARNING_BG},
    "en_gestion": {"label": "En gestión", "color": DS.WARNING,  "bg": DS.WARNING_BG},
    "resuelto":   {"label": "Resuelto",   "color": DS.SUCCESS,  "bg": DS.SUCCESS_BG},
    "cancelado":  {"label": "Cancelado",  "color": DS.MUTED,    "bg": DS.NEUTRAL_BG},
}
ESTADO_OPTS     = list(ESTADOS.keys())
ESTADOS_ACTIVOS = {"pendiente", "en_gestion"}

login_requerido()

_nombre           = get_nombre()
_turno, _turno_id = calcular_turno()
_next_id          = turno_siguiente_id(_turno, _turno_id)
_next_nombre      = _next_id.rsplit("_", 1)[1].capitalize()

# Guardamos en session_state para que on_change pueda leerlos
# (los callbacks se ejecutan antes de que las vars del módulo se re-evalúen)
st.session_state["_page_turno_id"] = _turno_id
st.session_state["_page_nombre"]   = _nombre


def _on_estado_change(prefix: str, tracking: str):
    key   = f"sel_{prefix}_{tracking}"
    nuevo = st.session_state.get(key)
    t_id  = st.session_state.get("_page_turno_id")
    nmb   = st.session_state.get("_page_nombre", "")
    if nuevo and t_id:
        actualizar_estado(t_id, tracking, nuevo, nmb)


def _render_incidencias(df: pd.DataFrame, prefix: str):
    """Tabla de incidencias con selectbox de estado por fila."""
    if df.empty:
        return

    h_cols = st.columns([1.4, 1.9, 0.8, 1.6, 0.75, 1.5])
    for col, lbl in zip(h_cols, ["Tracking", "Empresa / Cadete", "Zona", "Tipo", "Prioridad", "Estado"]):
        col.markdown(
            f"<span style='font-size:0.7rem; font-weight:600; text-transform:uppercase; "
            f"color:{DS.MUTED};'>{lbl}</span>",
            unsafe_allow_html=True,
        )

    for _, row in df.iterrows():
        tracking      = str(row.get("tracking", ""))
        empresa       = row.get("empresa",   "—") or "—"
        cadete        = row.get("cadete",    "—") or "—"
        zona          = row.get("zona",      "—") or "—"
        tipo          = row.get("tipo",      "—") or "—"
        prioridad     = row.get("prioridad", "—") or "—"
        estado_actual = row.get("estado", "pendiente")
        if estado_actual not in ESTADOS:
            estado_actual = "pendiente"

        est = ESTADOS[estado_actual]

        c_tr, c_emp, c_zon, c_tip, c_pri, c_sel = st.columns([1.4, 1.9, 0.8, 1.6, 0.75, 1.5])

        c_tr.markdown(
            f'<div style="border-left:3px solid {est["color"]}; background:{est["bg"]}; '
            f'border-radius:0 6px 6px 0; padding:0.32rem 0.5rem;">'
            f'<span class="tracking-id">{tracking}</span></div>',
            unsafe_allow_html=True,
        )
        c_emp.markdown(
            f'<div style="padding:0.32rem 0; font-size:0.83rem; color:{DS.TEXT};">'
            f'{empresa} / {cadete}</div>',
            unsafe_allow_html=True,
        )
        c_zon.markdown(
            f'<div style="padding:0.32rem 0; font-size:0.83rem; color:{DS.TEXT};">{zona}</div>',
            unsafe_allow_html=True,
        )
        c_tip.markdown(
            f'<div style="padding:0.32rem 0; font-size:0.81rem; color:{DS.TEXT};">{tipo}</div>',
            unsafe_allow_html=True,
        )
        c_pri.markdown(
            f'<div style="padding:0.32rem 0;">{badge(prioridad, prio_level(prioridad))}</div>',
            unsafe_allow_html=True,
        )

        with c_sel:
            sel_key = f"sel_{prefix}_{tracking}"
            idx_def = ESTADO_OPTS.index(estado_actual)
            st.selectbox(
                "Estado",
                options=ESTADO_OPTS,
                format_func=lambda x: ESTADOS[x]["label"],
                index=idx_def,
                key=sel_key,
                label_visibility="collapsed",
                on_change=_on_estado_change,
                args=(prefix, tracking),
                disabled=es_demo(),
            )

        st.markdown(
            "<hr style='margin:0.1rem 0 0.25rem; border:none; border-top:1px solid #F0F0F0;'>",
            unsafe_allow_html=True,
        )


inject_css()

# ─ Header ─────────────────────────────────────────────────────────────────────
col_hdr, col_salir = st.columns([6, 1])
with col_hdr:
    rol_badge = "Admin" if es_admin() else ("Demo" if es_demo() else "Coordinadora")
    st.markdown(
        header_html("🔄", "Handoff de Turno",
                    f"Turno {_turno.capitalize()} · {_turno_id} · {rol_badge} {_nombre}"),
        unsafe_allow_html=True,
    )
with col_salir:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()

# Flash messages
if "_flash" in st.session_state:
    tipo, texto = st.session_state.pop("_flash")
    {"success": st.success, "info": st.info, "warning": st.warning}.get(tipo, st.info)(texto)

# ─ Cargar datos ───────────────────────────────────────────────────────────────
df_all = incidencias_de(_turno_id)

# Excluir registros ya transferidos (turno cerrado anteriormente)
if not df_all.empty:
    df_all = df_all[df_all["estado"] != "transferido"]

df_heredadas = df_all[df_all["heredada_de"] != ""].copy() if not df_all.empty else pd.DataFrame()
df_nuevas    = df_all[df_all["heredada_de"] == ""].copy() if not df_all.empty else pd.DataFrame()

activos_hered  = int(df_heredadas["estado"].isin(ESTADOS_ACTIVOS).sum()) if not df_heredadas.empty else 0
cerrados_hered = int((~df_heredadas["estado"].isin(ESTADOS_ACTIVOS)).sum()) if not df_heredadas.empty else 0
activos_nuevas = int(df_nuevas["estado"].isin(ESTADOS_ACTIVOS).sum()) if not df_nuevas.empty else 0
total_nuevas   = len(df_nuevas)
total_heredar  = activos_hered + activos_nuevas

# ─ KPIs ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Resumen del turno</p>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
for col_k, num, lbl in [
    (k1, len(df_heredadas), "Heredadas del turno anterior"),
    (k2, cerrados_hered,    "Heredadas cerradas este turno"),
    (k3, total_nuevas,      "Nuevas registradas este turno"),
    (k4, total_heredar,     "Pasan al turno siguiente"),
]:
    with col_k:
        st.markdown(kpi_card(lbl, num), unsafe_allow_html=True)

st.divider()

# ─ A. Heredadas del turno anterior ────────────────────────────────────────────
st.markdown('<p class="section-lbl">⚠️ Heredadas del turno anterior — actualizá el estado</p>', unsafe_allow_html=True)

if df_heredadas.empty:
    st.success("✅ No hay incidencias heredadas en este turno.")
else:
    _render_incidencias(df_heredadas, "hered")

st.divider()

# ─ B. Incidencias nuevas del turno actual ─────────────────────────────────────
st.markdown('<p class="section-lbl">📋 Incidencias nuevas de este turno</p>', unsafe_allow_html=True)

if df_nuevas.empty:
    st.info("Sin incidencias registradas en este turno aún.")
else:
    _render_incidencias(df_nuevas, "nueva")

st.divider()

# ─ Cierre del turno ───────────────────────────────────────────────────────────
st.markdown('<p class="section-lbl">Cierre del turno</p>', unsafe_allow_html=True)

if total_heredar > 0:
    resumen_texto = (
        f"Al cerrar el turno <b>{_turno.capitalize()}</b>, pasarán "
        f"<b>{total_heredar} incidencia(s) activa(s)</b> al turno <b>{_next_nombre}</b>: "
        f"{activos_hered} heredada(s) aún activas + {activos_nuevas} nueva(s) de este turno. "
        f"Las resueltas y canceladas <b>no se heredan</b>."
    )
else:
    resumen_texto = (
        f"Al cerrar el turno <b>{_turno.capitalize()}</b>, el turno <b>{_next_nombre}</b> "
        f"<b>no recibirá incidencias activas</b>. ✅"
    )

st.markdown(f'<div class="resumen-box">{resumen_texto}</div>', unsafe_allow_html=True)

if es_demo():
    st.info("🔍 Modo demo: podés ver el estado del turno pero no podés cerrarlo.")
elif not st.session_state.get("_confirmar_cierre"):
    if st.button("🔒 Cerrar Turno y Pasar Pendientes →", use_container_width=True):
        st.session_state["_confirmar_cierre"] = True
        st.rerun()
else:
    accion = (
        f"pasar **{total_heredar}** incidencia(s) activa(s) al turno **{_next_nombre}**"
        if total_heredar > 0 else "cerrar el turno sin incidencias activas"
    )
    st.warning(f"⚠️ ¿Confirmás el cierre del turno **{_turno.capitalize()}**? Esto va a {accion}.")
    col_si, col_no = st.columns(2)
    with col_si:
        if st.button("✅ Sí, cerrar turno", type="primary", use_container_width=True):
            n = heredar_pendientes(_turno_id, _next_id, _nombre)
            st.session_state.pop("_confirmar_cierre", None)
            msg = (
                f"✅ Turno cerrado. Se pasaron **{n}** incidencia(s) al turno {_next_nombre}."
                if n > 0 else "✅ Turno cerrado sin incidencias activas."
            )
            st.session_state["_flash"] = ("success", msg)
            st.rerun()
    with col_no:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.pop("_confirmar_cierre", None)
            st.rerun()

st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
