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


# ─── TABLA ENVIOS (corte operativo del admin) ─────────────────────────────────

TABLA_ENVIOS = "envios"


def _filas_envios(df: pd.DataFrame, col_map: dict, tracking_col: str) -> list:
    estado_col  = col_map.get("Estado")
    cadete_col  = col_map.get("Cadete")
    zona_col    = col_map.get("Zona")
    empresa_col = col_map.get("Nombre Fantasia")
    ahora = datetime.now().isoformat()
    filas = []
    for _, row in df.iterrows():
        t = str(row.get(tracking_col, "")).strip() if tracking_col else ""
        if not t or t in ("nan", "None", ""):
            continue
        filas.append({
            "tracking": t,
            "cadete":   str(row.get(cadete_col,  "")).strip() if cadete_col  else "",
            "zona":     str(row.get(zona_col,    "")).strip() if zona_col    else "",
            "empresa":  str(row.get(empresa_col, "")).strip() if empresa_col else "",
            "estado":   str(row.get(estado_col,  "")).strip() if estado_col  else "",
            "corte_at": ahora,
        })
    return filas


def guardar_envios(df: pd.DataFrame, col_map: dict, tracking_col: str) -> tuple:
    """
    Upserta todos los envíos del corte en la tabla envios.
    Retorna (ok: bool, n_filas: int, error: str | None).
    """
    filas = _filas_envios(df, col_map, tracking_col)
    n = len(filas)
    if not filas:
        return False, 0, None
    try:
        for i in range(0, n, 500):
            _client().table(TABLA_ENVIOS).upsert(
                filas[i:i + 500], on_conflict="tracking"
            ).execute()
        return True, n, None
    except Exception as e:
        return False, n, str(e)


def leer_envios() -> pd.DataFrame:
    """Lee el corte guardado por el admin (para coordinadoras)."""
    try:
        data = _client().table(TABLA_ENVIOS).select("*").execute().data
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data).fillna("")
    except Exception:
        return pd.DataFrame()


def comparar_envios(df_nuevo: pd.DataFrame, col_map: dict, tracking_col: str) -> tuple:
    """
    Compara el Excel nuevo contra los envíos guardados en Supabase.
    Retorna (df_nuevos, df_cambios).
    """
    estado_col  = col_map.get("Estado")
    cadete_col  = col_map.get("Cadete")
    zona_col    = col_map.get("Zona")
    empresa_col = col_map.get("Nombre Fantasia")

    cols_display = {k: v for k, v in {
        "Tracking": tracking_col,
        "Cadete":   cadete_col,
        "Zona":     zona_col,
        "Empresa":  empresa_col,
        "Estado":   estado_col,
    }.items() if v and v in df_nuevo.columns}

    df_actual = leer_envios()

    if df_actual.empty:
        df_n = df_nuevo[[v for v in cols_display.values()]].rename(
            columns={v: k for k, v in cols_display.items()}
        ).fillna("")
        return df_n, pd.DataFrame()

    existentes = set(df_actual["tracking"].astype(str).str.strip())

    # Nuevos trackings
    if tracking_col and tracking_col in df_nuevo.columns:
        mask_nuevo = ~df_nuevo[tracking_col].astype(str).str.strip().isin(existentes)
        df_n = df_nuevo[mask_nuevo][[v for v in cols_display.values()]].rename(
            columns={v: k for k, v in cols_display.items()}
        ).fillna("").reset_index(drop=True)
    else:
        df_n = pd.DataFrame()

    # Cambios de estado
    cambios = []
    if tracking_col and estado_col and tracking_col in df_nuevo.columns and estado_col in df_nuevo.columns:
        mapa_estado = df_actual.set_index("tracking")["estado"].to_dict()
        for _, row in df_nuevo.iterrows():
            t = str(row.get(tracking_col, "")).strip()
            if t not in mapa_estado:
                continue
            estado_viejo = str(mapa_estado[t]).strip()
            estado_nuevo = str(row.get(estado_col, "")).strip()
            if estado_viejo.lower() != estado_nuevo.lower():
                cambios.append({
                    "Tracking":         t,
                    "Estado anterior":  estado_viejo,
                    "Estado nuevo":     estado_nuevo,
                    "Cadete": str(row.get(cadete_col, "")).strip() if cadete_col else "",
                    "Zona":   str(row.get(zona_col,   "")).strip() if zona_col   else "",
                })

    return df_n, pd.DataFrame(cambios)
