import sys
import pathlib
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.auth import login_requerido, logout, get_nombre, es_demo

st.set_page_config(
    page_title="Asistente IA · LogiTrack",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

C_PRIMARY   = "#FF8C69"
C_SECONDARY = "#FFF3C4"
C_TEXT      = "#2D2D2D"
C_MUTED     = "#9E9E9E"

login_requerido()
_nombre = get_nombre()

st.markdown(f"""
<style>
[data-testid="collapsedControl"] {{ display: none !important; }}
.stApp {{ background: #FFFFFF; }}
.block-container {{ padding-top: 1.5rem !important; max-width: 860px; }}
.page-header {{
    background: {C_SECONDARY}; border-radius: 12px;
    padding: 0.75rem 1.2rem; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.75rem;
}}
.page-brand {{ font-size: 1.2rem; font-weight: 800; color: {C_TEXT}; margin: 0; }}
.page-meta  {{ font-size: 0.78rem; color: {C_MUTED}; margin: 0; }}
.app-footer {{
    margin-top: 3rem; padding-top: 1.2rem;
    border-top: 2px solid {C_SECONDARY};
    text-align: center; color: {C_MUTED}; font-size: 0.82rem;
}}
@media (max-width: 768px) {{
    .block-container {{ padding: 0.5rem 0.6rem 5rem !important; max-width: 100% !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ─ Header ─────────────────────────────────────────────────────────────────────
col_hdr, col_salir = st.columns([6, 1])
with col_hdr:
    demo_badge = " · 👁️ Demo" if es_demo() else ""
    st.markdown(f"""
    <div class="page-header">
        <span style="font-size:1.5rem">🤖</span>
        <div>
            <p class="page-brand">Asistente Logístico IA</p>
            <p class="page-meta">Análisis del corte operativo en lenguaje natural{demo_badge}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_salir:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir", use_container_width=True):
        logout()


# ─ Contexto del corte ─────────────────────────────────────────────────────────
def _norm(serie: pd.Series) -> pd.Series:
    return (serie.astype(str).str.lower().str.strip()
        .str.replace("á","a").str.replace("é","e")
        .str.replace("í","i").str.replace("ó","o").str.replace("ú","u"))


def construir_contexto(df: pd.DataFrame, col_map: dict, filename: str) -> str:
    total = len(df)
    estado_col  = col_map.get("Estado")
    cadete_col  = col_map.get("Cadete")
    zona_col    = col_map.get("Zona")
    empresa_col = col_map.get("Nombre Fantasia")

    lineas = [
        "=== CORTE OPERATIVO ===",
        f"Archivo: {filename}",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total envíos: {total}",
        "",
    ]

    if estado_col and estado_col in df.columns:
        s = _norm(df[estado_col])
        n_entr  = int(s.str.contains("entregado|entrega", na=False).sum())
        n_pend  = int(s.str.contains("pendiente", na=False, regex=False).sum())
        n_viaje = int(s.str.contains("en viaje|en camino", na=False).sum())
        n_rech  = int(s.str.contains("rechazado|devuelto|rebote", na=False).sum())
        otd     = f"{n_entr/total*100:.1f}%" if total else "0%"
        inc     = f"{(n_pend+n_viaje)/total*100:.1f}%" if total else "0%"

        lineas += [
            "── KPIs ──",
            f"Entregados: {n_entr} ({otd} OTD)",
            f"Pendientes: {n_pend}",
            f"En viaje:   {n_viaje}",
            f"Rechazados: {n_rech}",
            f"Tasa de incidencia: {inc}",
            "",
        ]

        # Top 5 cadetes con más pendientes
        if cadete_col and cadete_col in df.columns:
            mask_pend = s.str.contains("pendiente|en viaje|en camino", na=False)
            top_cad = (
                df[mask_pend].groupby(cadete_col, dropna=False)
                .size().nlargest(5)
            )
            if not top_cad.empty:
                lineas.append("── TOP 5 CADETES CON MÁS PENDIENTES/EN VIAJE ──")
                for cad, cnt in top_cad.items():
                    total_cad = int((df[cadete_col] == cad).sum())
                    lineas.append(f"  {cad}: {cnt} pendientes / {total_cad} total")
                lineas.append("")

        # Top 5 zonas con alertas
        if zona_col and zona_col in df.columns:
            mask_alerta = s.str.contains("pendiente|en viaje|en camino|rechazado|devuelto", na=False)
            top_zona = (
                df[mask_alerta].groupby(zona_col, dropna=False)
                .size().nlargest(5)
            )
            if not top_zona.empty:
                lineas.append("── TOP 5 ZONAS CON ALERTAS ──")
                for zona, cnt in top_zona.items():
                    lineas.append(f"  {zona}: {cnt} alertas")
                lineas.append("")

        # Top 5 empresas afectadas
        if empresa_col and empresa_col in df.columns:
            mask_alerta = s.str.contains("pendiente|en viaje|en camino|rechazado|devuelto", na=False)
            top_emp = (
                df[mask_alerta].groupby(empresa_col, dropna=False)
                .size().nlargest(5)
            )
            if not top_emp.empty:
                lineas.append("── TOP 5 EMPRESAS CON ENVÍOS EN RIESGO ──")
                for emp, cnt in top_emp.items():
                    lineas.append(f"  {emp}: {cnt} envíos en riesgo")
                lineas.append("")

    return "\n".join(lineas)


SYSTEM_PROMPT = """Sos un asistente de inteligencia artificial especializado en logística de última milla para el sistema LogiTrack.
Tu función es analizar el corte operativo del día y responder preguntas del equipo de coordinación en lenguaje claro y profesional.

Cuando respondas:
- Usá terminología logística precisa (OTD, tasa de incidencia, pendientes críticos, envíos en riesgo).
- Sé conciso pero completo. Priorizá los datos más relevantes para la operación.
- Si detectás problemas (alta tasa de rechazos, zona caliente, cadete con muchos pendientes), mencionalo proactivamente.
- Respondé siempre en español rioplatense.
- No inventes datos que no estén en el contexto proporcionado.

El contexto del corte actual te será proporcionado al inicio de cada conversación."""


def llamar_groq(mensajes: list) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes,
            temperature=0.4,
            max_tokens=1024,
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al conectar con el asistente: {e}"


# ─ Datos del corte ────────────────────────────────────────────────────────────
df       = st.session_state.get("df")
col_map  = st.session_state.get("col_map", {})
filename = st.session_state.get("filename", "sin archivo")

if df is None:
    st.info("ℹ️ No hay corte cargado. El asistente necesita datos para responder preguntas operativas.")
    st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Asistente IA · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
    st.stop()

contexto = construir_contexto(df, col_map, filename)

# ─ Estado del chat ────────────────────────────────────────────────────────────
if "chat_asistente" not in st.session_state:
    st.session_state["chat_asistente"] = []

# ─ Sugerencias rápidas ────────────────────────────────────────────────────────
SUGERENCIAS = [
    "¿Qué cadetes tienen más pendientes?",
    "¿Cuántos envíos están en riesgo?",
    "¿Cuál es la tasa de entrega efectiva?",
    "¿Qué zonas tienen más problemas hoy?",
    "Resumí el estado general del corte",
]

if not st.session_state["chat_asistente"]:
    st.markdown("**Preguntas frecuentes:**")
    cols = st.columns(len(SUGERENCIAS))
    for i, sug in enumerate(SUGERENCIAS):
        with cols[i]:
            if st.button(sug, use_container_width=True, key=f"sug_{i}"):
                st.session_state["_pregunta_rapida"] = sug
                st.rerun()

# ─ Historial del chat ─────────────────────────────────────────────────────────
for msg in st.session_state["chat_asistente"]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ─ Input ──────────────────────────────────────────────────────────────────────
pregunta_rapida = st.session_state.pop("_pregunta_rapida", None)
prompt = st.chat_input("Hacé una pregunta sobre el corte operativo…") or pregunta_rapida

if prompt:
    st.session_state["chat_asistente"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    mensajes_api = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{contexto}"},
        *st.session_state["chat_asistente"],
    ]

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analizando…"):
            respuesta = llamar_groq(mensajes_api)
        st.markdown(respuesta)

    st.session_state["chat_asistente"].append({"role": "assistant", "content": respuesta})

# ─ Botón limpiar chat ─────────────────────────────────────────────────────────
if st.session_state["chat_asistente"]:
    if st.button("🗑️ Limpiar conversación", use_container_width=False):
        st.session_state["chat_asistente"] = []
        st.rerun()

st.markdown('<div class="app-footer">🚚 LogiTrack Universal · Asistente IA · Desarrollado por Ayelen Anaquin</div>', unsafe_allow_html=True)
