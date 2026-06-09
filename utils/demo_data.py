import pandas as pd
import random
from datetime import datetime, timedelta

_CADETES = [
    "Lucas Fernández",
    "Matías García",
    "Romina López",
    "Sebastián Torres",
    "Carolina Ruiz",
    "Nicolás Pereyra",
]

_ZONAS = [
    "Palermo", "Belgrano", "Recoleta", "Caballito", "Flores",
    "Villa Urquiza", "Almagro", "Boedo", "Barracas", "San Telmo",
    "Villa Crespo", "Mataderos", "Liniers", "Microcentro", "Devoto",
    "Balvanera", "Núñez", "Saavedra",
]

_EMPRESAS = [
    "ELUMILED", "TechStore BA", "Moda & Co.", "FarmaPlus",
    "LibroMundo", "SportMax", "HomeDecor BA", "GourmetBox",
    "PetWorld", "OfficeHub", "DistribuidoraNorte", "LogísticaSur",
]

_ESTADOS = (
    ["Entregado"] * 28
    + ["Pendiente"] * 10
    + ["En viaje"] * 8
    + ["Rechazado"] * 4
)


def cargar_demo() -> pd.DataFrame:
    rng = random.Random(42)
    estados = _ESTADOS[:]
    rng.shuffle(estados)

    hoy = datetime.now()
    filas = []
    for i in range(50):
        delta = timedelta(
            days=rng.randint(0, 2),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        fecha = hoy - delta
        filas.append({
            "Tracking":        f"LT{20000 + i:05d}",
            "Cadete":          rng.choice(_CADETES),
            "Zona":            rng.choice(_ZONAS),
            "Nombre Fantasia": rng.choice(_EMPRESAS),
            "Estado":          estados[i],
            "Fecha":           fecha.strftime("%Y-%m-%d %H:%M"),
        })

    return pd.DataFrame(filas)
