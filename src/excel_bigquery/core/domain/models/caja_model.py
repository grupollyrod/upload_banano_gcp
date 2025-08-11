from dataclasses import dataclass
from typing import Optional


@dataclass
class CajaModel:
    id_caja: str
    id_archivo: str
    nombre_caja: str
    codigo_container: str
    codigo_hacienda: int
    codigo_trazabilidad: str
    nombre_hacienda: str
    temperatura: float
    dedos_totales: int
    peso_bruto_kg: float
    peso_total_kg: float
    cantidad_observaciones: int
    dedos_afectados_totales: int
    peso_promedio: float
    week_code: int
    year_code: int
    spec: int
    uw: int
    ow: int

    def __post_init__(self):
        # Validaciones básicas
        if not self.id_caja:
            raise ValueError("id_caja no puede estar vacío")
        if not self.id_archivo:
            raise ValueError("id_archivo no puede estar vacío")