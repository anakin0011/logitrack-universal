import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

TABLA = "incidencias"

# Columnas mínimas de la tabla en Supabase
# Las marcadas con * son extra — agregarlas en Supabase para que funcione el handoff:
#   zona TEXT, estado TEXT DEFAULT 'pendiente', heredada_de TEXT,
#   turno_id TEXT, resuelto_por TEXT
COLS_INTERNAS = [
    "timestamp", "turno_id", "turno", "coordinadora",
    "tracking", "cadete", "empresa", "zona",
    "tipo", "descripcion", "prioridad", "estado",
    "heredada_de", "resuelto_por",
]


@st.cache_resource
def _client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except KeyError:
        claves_disponibles = list(st.secrets.keys()) if hasattr(st.secrets, "keys") else "—"
        raise KeyError(
            f"No se encontró SUPABASE_URL o SUPABASE_KEY. "
            f"Claves disponibles en secrets: {claves_disponibles}"
        )
    return create_client(url, key)


# ─── Mapeo de nombres internos ↔ columnas de Supabase ─────────────────────────
# Supabase:  tipo_novedad  quien_reporta  fecha
# Interno:   tipo          coordinadora   timestamp

def _a_supabase(d: dict) -> dict:
    return {
        "tracking":      d.get("tracking",     ""),
        "cadete":        d.get("cadete",        ""),
        "empresa":       d.get("empresa",       ""),
        "tipo_novedad":  d.get("tipo",          d.get("tipo_novedad",  "")),
        "descripcion":   d.get("descripcion",   ""),
        "quien_reporta": d.get("coordinadora",  d.get("quien_reporta", "")),
        "prioridad":     d.get("prioridad",     ""),
        "turno":         d.get("turno",         ""),
        "fecha":         d.get("timestamp",     d.get("fecha", datetime.now().isoformat())),
        "zona":          d.get("zona",          ""),
        "estado":        d.get("estado",        "pendiente"),
        "heredada_de":   d.get("heredada_de",   ""),
        "turno_id":      d.get("turno_id",      ""),
        "resuelto_por":  d.get("resuelto_por",  ""),
    }


def _normalizar(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas Supabase → nombres internos y rellena faltantes."""
    df = df.rename(columns={
        "tipo_novedad":  "tipo",
        "quien_reporta": "coordinadora",
        "fecha":         "timestamp",
    })
    for col, default in [
        ("estado",      "pendiente"),
        ("heredada_de", ""),
        ("turno_id",    ""),
        ("resuelto_por",""),
        ("zona",        ""),
        ("turno",       ""),
        ("coordinadora",""),
        ("timestamp",   ""),
    ]:
        if col not in df.columns:
            df[col] = default
    return df.fillna("")


# ─── CRUD ─────────────────────────────────────────────────────────────────────

def insertar(fila: dict) -> bool:
    try:
        _client().table(TABLA).insert(_a_supabase(fila)).execute()
        return True
    except Exception as e:
        st.error(f"Supabase — error al guardar: {e}")
        return False


def leer(turno_id: str = None) -> pd.DataFrame:
    """Lee incidencias, opcionalmente filtradas por turno_id."""
    try:
        q = _client().table(TABLA).select("*").order("fecha", desc=False)
        if turno_id:
            q = q.eq("turno_id", turno_id)
        data = q.execute().data
        if not data:
            return pd.DataFrame(columns=COLS_INTERNAS)
        return _normalizar(pd.DataFrame(data))
    except Exception as e:
        st.error(f"Supabase — error al leer: {e}")
        return pd.DataFrame(columns=COLS_INTERNAS)


def leer_todo() -> pd.DataFrame:
    return leer()


def actualizar_estado(turno_id: str, tracking: str, estado: str, resuelto_por: str = "") -> bool:
    try:
        upd = {"estado": estado}
        if resuelto_por:
            upd["resuelto_por"] = resuelto_por
        (
            _client().table(TABLA)
            .update(upd)
            .eq("turno_id", turno_id)
            .eq("tracking", tracking)
            .execute()
        )
        return True
    except Exception as e:
        st.error(f"Supabase — error al actualizar estado: {e}")
        return False


def marcar_transferidos(turno_id: str) -> bool:
    """Marca como transferido todo lo activo (pendiente + en_gestion) del turno."""
    try:
        for estado_orig in ("pendiente", "en_gestion"):
            (
                _client().table(TABLA)
                .update({"estado": "transferido"})
                .eq("turno_id", turno_id)
                .eq("estado", estado_orig)
                .execute()
            )
        return True
    except Exception as e:
        st.error(f"Supabase — error al marcar transferidos: {e}")
        return False
