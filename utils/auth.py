import hashlib
from datetime import datetime, timedelta
import streamlit as st

C_PRIMARY   = "#FF8C69"
C_SECONDARY = "#FFF3C4"
C_TEXT      = "#2D2D2D"
C_MUTED     = "#9E9E9E"


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def verificar_credenciales(usuario: str, password: str):
    try:
        usuarios = st.secrets.get("usuarios", {})
    except Exception:
        return None
    for nombre, datos in usuarios.items():
        if datos.get("usuario") == usuario and datos.get("password_hash") == _hash(password):
            return {
                "nombre": nombre,
                "usuario": usuario,
                "rol": datos.get("rol", "coordinadora"),
                "turno": datos.get("turno", ""),
            }
    return None


def login_requerido() -> bool:
    """Si no hay sesión activa muestra el login y detiene la ejecución."""
    if st.session_state.get("auth"):
        return True
    _mostrar_login()
    st.stop()
    return False


def _mostrar_login():
    st.markdown(f"""
    <style>
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stSidebarNav"] {{ display: none !important; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}
    .stApp {{ background: #FFFFFF; }}
    .block-container {{ padding-top: 4.5rem !important; max-width: 400px !important; margin: auto; }}
    .login-card {{
        background: {C_SECONDARY};
        border-radius: 18px;
        padding: 2.5rem 2rem 1.8rem;
        text-align: center;
        box-shadow: 0 4px 24px rgba(255,140,105,0.18);
    }}
    .login-icon  {{ font-size: 3.5rem; line-height: 1; margin-bottom: 0.5rem; }}
    .login-title {{ font-size: 1.9rem; font-weight: 800; color: {C_TEXT}; margin: 0 0 0.25rem; }}
    .login-sub   {{ font-size: 0.84rem; color: {C_MUTED}; margin: 0 0 1.8rem; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-card">
        <div class="login-icon">🚚</div>
        <p class="login-title">LogiTrack</p>
        <p class="login-sub">Control de Gestión · Turnos</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#E3F2FD; border-radius:10px; padding:0.75rem 1rem;
        border-left:4px solid #1565C0; font-size:0.83rem; color:#1565C0; margin-bottom:0.5rem;">
        <b>🔍 Acceso demo</b><br>
        Usuario: <b>demo</b> &nbsp;·&nbsp; Contraseña: <b>demo123</b>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_login"):
        usuario  = st.text_input("Usuario", placeholder="ingresá tu usuario")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        ingresar = st.form_submit_button("Ingresar →", use_container_width=True)

    if ingresar:
        if not usuario.strip() or not password.strip():
            st.warning("Completá usuario y contraseña.")
        else:
            datos = verificar_credenciales(usuario.strip(), password.strip())
            if datos:
                st.session_state["auth"] = datos
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")


def logout():
    st.session_state.clear()
    st.rerun()


def get_user() -> dict:
    return st.session_state.get("auth", {})


def get_nombre() -> str:
    return get_user().get("nombre", "Usuario")


def get_rol() -> str:
    return get_user().get("rol", "")


def get_turno() -> str:
    return get_user().get("turno", "")


def es_admin() -> bool:
    return get_rol() == "admin"


def es_demo() -> bool:
    return get_rol() == "demo"


def calcular_turno(ahora: datetime = None) -> tuple:
    """Retorna (nombre_turno, turno_id) según la hora.

    02:00–17:59  →  turno 'dia'   →  YYYY-MM-DD_dia
    18:00–01:59  →  turno 'noche' →  YYYY-MM-DD_noche
    La madrugada (00:00–01:59) ancla al día anterior para que toda la
    noche comparta el mismo turno_id aunque cruce la medianoche.
    """
    if ahora is None:
        ahora = datetime.now()
    hora = ahora.hour
    if hora < 2:
        fecha_base = (ahora - timedelta(days=1)).strftime("%Y-%m-%d")
        return "noche", f"{fecha_base}_noche"
    elif hora < 18:
        return "dia", f"{ahora.strftime('%Y-%m-%d')}_dia"
    else:
        return "noche", f"{ahora.strftime('%Y-%m-%d')}_noche"
