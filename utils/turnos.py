import os
from datetime import datetime, timedelta
import pandas as pd

RUTA_CSV = "incidencias_turnos.csv"
COLS_BASE = [
    "timestamp", "turno_id", "turno", "coordinadora",
    "tracking", "cadete", "empresa", "zona",
    "tipo", "descripcion", "prioridad", "estado",
    "heredada_de", "resuelto_por",
]


def turno_anterior_id(turno_nombre: str, turno_id: str) -> str:
    fecha_str = turno_id.rsplit("_", 1)[0]
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    if turno_nombre == "dia":
        return f"{(fecha - timedelta(days=1)).strftime('%Y-%m-%d')}_noche"
    return f"{fecha_str}_dia"


def turno_siguiente_id(turno_nombre: str, turno_id: str) -> str:
    fecha_str = turno_id.rsplit("_", 1)[0]
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    if turno_nombre == "dia":
        return f"{fecha_str}_noche"
    return f"{(fecha + timedelta(days=1)).strftime('%Y-%m-%d')}_dia"


def leer_csv() -> pd.DataFrame:
    if not os.path.exists(RUTA_CSV):
        return pd.DataFrame(columns=COLS_BASE)
    df = pd.read_csv(RUTA_CSV, dtype=str).fillna("")
    for col in COLS_BASE:
        if col not in df.columns:
            df[col] = ""
    return df


def incidencias_de(turno_id: str) -> pd.DataFrame:
    df = leer_csv()
    if df.empty:
        return pd.DataFrame(columns=COLS_BASE)
    return df[df["turno_id"] == turno_id].reset_index(drop=True)


def resolver_incidencias(tracking_list: list, turno_id: str, coordinadora: str):
    if not tracking_list:
        return
    df = leer_csv()
    if df.empty:
        return
    mask = (df["turno_id"] == turno_id) & (df["tracking"].isin([str(t) for t in tracking_list]))
    df.loc[mask, "estado"]       = "resuelto"
    df.loc[mask, "resuelto_por"] = coordinadora
    df.to_csv(RUTA_CSV, index=False)


def heredar_pendientes(turno_id_origen: str, turno_id_destino: str, coordinadora: str) -> int:
    """Copia los pendientes de un turno al siguiente y marca los originales como 'transferido'."""
    df = leer_csv()
    if df.empty:
        return 0

    pendientes = df[(df["turno_id"] == turno_id_origen) & (df["estado"] == "pendiente")]
    if pendientes.empty:
        return 0

    turno_dest_nombre = turno_id_destino.rsplit("_", 1)[1]
    nuevos = pendientes.copy()
    nuevos["turno_id"]     = turno_id_destino
    nuevos["turno"]        = turno_dest_nombre
    nuevos["heredada_de"]  = turno_id_origen
    nuevos["timestamp"]    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevos["coordinadora"] = coordinadora
    nuevos["resuelto_por"] = ""

    # Marcar originales como transferidos para no mostrarlos dos veces
    mask_src = (df["turno_id"] == turno_id_origen) & (df["estado"] == "pendiente")
    df.loc[mask_src, "estado"] = "transferido"
    df.to_csv(RUTA_CSV, index=False)

    nuevos.to_csv(RUTA_CSV, mode="a", header=False, index=False)
    return len(nuevos)
