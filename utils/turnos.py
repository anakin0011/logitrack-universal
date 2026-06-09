from datetime import datetime, timedelta
import pandas as pd
from utils.db import insertar, leer, actualizar_estado, marcar_transferidos


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


def incidencias_de(turno_id: str) -> pd.DataFrame:
    return leer(turno_id)


def resolver_incidencias(tracking_list: list, turno_id: str, coordinadora: str):
    for tracking in tracking_list:
        actualizar_estado(turno_id, str(tracking), "resuelto", coordinadora)


def heredar_pendientes(turno_id_origen: str, turno_id_destino: str, coordinadora: str) -> int:
    """Copia los pendientes al turno siguiente y marca los originales como transferido."""
    df = leer(turno_id_origen)
    if df.empty:
        return 0

    pendientes = df[df["estado"] == "pendiente"]
    if pendientes.empty:
        return 0

    turno_dest_nombre = turno_id_destino.rsplit("_", 1)[1]
    ahora = datetime.now().isoformat()

    for _, row in pendientes.iterrows():
        insertar({
            **row.to_dict(),
            "turno_id":    turno_id_destino,
            "turno":       turno_dest_nombre,
            "heredada_de": turno_id_origen,
            "timestamp":   ahora,
            "coordinadora": coordinadora,
            "resuelto_por": "",
            "estado":      "pendiente",
        })

    marcar_transferidos(turno_id_origen)
    return len(pendientes)
