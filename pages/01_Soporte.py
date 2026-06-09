import os
import sys
import pathlib
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.auth import login_requerido, logout, get_nombre, get_rol, es_admin

st.set_page_config(
    page_title="Mesa de Soporte · LogiTrack",
    page_icon="🛠️",
    layout="centered",
)

# ─── Paleta (consistente con app principal) ───────────────────────────────────
C_PRIMARY   = "#FF8C69"
C_SECONDARY = "#FFF3C4"
C_TEXT      = "#2D2D2D"
C_MUTED     = "#9E9E9E"

st.markdown(f"""
<style>
[data-testid="collapsedControl"] {{ display: none !important; }}
.stApp {{ background: #FFFFFF; }}
.block-container {{ padding-top: 2rem !important; max-width: 680px; }}
.form-header {{
    background: {C_SECONDARY}; border-radius: 12px;
    padding: 1rem 1.4rem; margin-bottom: 1.4rem;
}}
.form-title {{ font-size: 1.3rem; font-weight: 800; color: {C_TEXT}; margin: 0 0 0.2rem; }}
.form-sub   {{ font-size: 0.82rem; color: {C_MUTED}; margin: 0; }}
.success-box {{
    background: #E8F5E9; border-left: 4px solid #52B788;
    border-radius: 0 10px 10px 0; padding: 0.85rem 1.1rem; margin-top: 1rem;
    font-size: 0.9rem; color: {C_TEXT};
}}
.app-footer {{
    margin-top: 3rem; padding-top: 1.2rem;
    border-top: 2px solid {C_SECONDARY};
    text-align: center; color: {C_MUTED}; font-size: 0.82rem;
}}
</style>
""", unsafe_allow_html=True)

login_requerido()

RUTA_CSV = "incidencias.csv"

TIPOS_NOVEDAD = [
    "Envío demorado",
    "Destinatario ausente",
    "Dirección incorrecta",
    "Paquete dañado",
    "Rechazo de mercadería",
    "Otro",
]

def guardar_incidencia(datos: dict):
    # ── Conexión Supabase ──────────────────────────────────────────────────
    # from supabase import create_client
    # url      = st.secrets["SUPABASE_URL"]
    # key      = st.secrets["SUPABASE_KEY"]
    # supabase = create_client(url, key)
    # supabase.table("incidencias").insert(datos).execute()
    # ──────────────────────────────────────────────────────────────────────
    fila = pd.DataFrame([datos])
    fila.to_csv(RUTA_CSV, mode="a", header=not os.path.exists(RUTA_CSV), index=False)

# ─── Encabezado ───────────────────────────────────────────────────────────────
_col_hdr, _col_salir = st.columns([5, 1])
with _col_hdr:
    _rol_badge = "👑 Admin" if es_admin() else "👤 Coordinadora"
    st.markdown(f"""
    <div class="form-header">
        <p class="form-title">🛠️ Mesa de Soporte Operativo</p>
        <p class="form-sub">Registro de novedades y gestión de incidencias logísticas · {_rol_badge} {get_nombre()}</p>
    </div>
    """, unsafe_allow_html=True)
with _col_salir:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()

# ─── Formulario ───────────────────────────────────────────────────────────────
with st.form("form_incidencia", clear_on_submit=True):
    tracking    = st.text_input("Número de Tracking")
    cadete      = st.text_input("Cadete / Chofer")
    empresa     = st.text_input("Empresa")
    tipo        = st.selectbox("Tipo de novedad", TIPOS_NOVEDAD)
    descripcion = st.text_area("Descripción de la novedad", height=120,
                               placeholder="Detallá la novedad con la mayor precisión posible.")
    quien       = st.text_input("Quién reporta")

    enviado = st.form_submit_button("📋 Registrar Novedad", use_container_width=True)

if enviado:
    if not tracking.strip():
        st.warning("⚠️ El Número de Tracking es obligatorio.")
    elif not quien.strip():
        st.warning("⚠️ Indicá quién reporta la novedad.")
    else:
        guardar_incidencia({
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tracking":    tracking.strip(),
            "cadete":      cadete.strip(),
            "empresa":     empresa.strip(),
            "tipo":        tipo,
            "descripcion": descripcion.strip(),
            "quien":       quien.strip(),
        })
        st.markdown(f"""
        <div class="success-box">
            ✅ <b>Novedad registrada correctamente.</b><br>
            Tracking <b>{tracking.strip()}</b> · {tipo} · Reportado por <b>{quien.strip()}</b>
        </div>
        """, unsafe_allow_html=True)

# ─── Historial del día ────────────────────────────────────────────────────────
st.divider()
st.markdown(f'<p style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{C_MUTED};margin-bottom:0.5rem">Novedades registradas en este corte</p>', unsafe_allow_html=True)

if os.path.exists(RUTA_CSV):
    historial = pd.read_csv(RUTA_CSV)
    if not historial.empty:
        st.dataframe(historial[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        st.info("Sin novedades registradas aún.")
else:
    st.info("Sin novedades registradas aún.")

st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
