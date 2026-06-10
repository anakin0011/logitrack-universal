import hashlib
from datetime import datetime, timedelta
import streamlit as st

C_PRIMARY = "#185FA5"
C_TEXT    = "#1A1F2B"
C_MUTED   = "#5F6672"


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
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    *, *::before, *::after { font-family: 'Inter', sans-serif !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarNav"]     { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    .stApp { background: #F4F5F7; }
    .block-container {
        padding-top: 4.5rem !important;
        max-width: 400px !important;
        margin: auto;
    }
    .login-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 2.4rem 2rem 1.8rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E4E6EA;
        margin-bottom: 1rem;
    }
    .login-icon  { font-size: 2.8rem; line-height: 1; margin-bottom: 0.55rem; }
    .login-title { font-size: 1.6rem; font-weight: 700; color: #1A1F2B;
                   margin: 0 0 0.2rem; letter-spacing: -0.02em; }
    .login-sub   { font-size: 0.82rem; color: #5F6672; margin: 0; }
    .demo-hint {
        background: #EBF3FC;
        border: 1px solid #185FA5;
        border-radius: 8px;
        padding: 0.65rem 0.9rem;
        font-size: 0.8rem;
        color: #185FA5;
        margin-bottom: 0.75rem;
        text-align: left;
    }
    .login-version {
        text-align: center;
        font-size: 0.72rem;
        color: #5F6672;
        margin-top: 0.75rem;
    }
    .stButton > button {
        background: #185FA5 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stButton > button:hover { background: #0C447C !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-card">
        <div class="login-icon">🚚</div>
        <p class="login-title">LogiTrack</p>
        <p class="login-sub">Control de Gestión · Turnos</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-hint">
        <b>Acceso demo</b> &nbsp;·&nbsp;
        Usuario: <b>demo</b> &nbsp;·&nbsp; Contraseña: <b>demo123</b>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_login"):
        usuario  = st.text_input("Usuario", placeholder="ingresá tu usuario")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        ingresar = st.form_submit_button("Ingresar →", use_container_width=True)

    st.markdown('<p class="login-version">LogiTrack Universal · v2.0 · prod</p>', unsafe_allow_html=True)

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
