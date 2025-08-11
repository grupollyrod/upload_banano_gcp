from dataclasses import dataclass


@dataclass
class ArchivoModel:
    id_archivo: str
    archivo: str
    warehouse: str
    puerto: str
    buque: str
    annio: int
    semana: int
    spec: int
    tipo: str

    def __post_init__(self):
        # Validaciones básicas
        if not self.id_archivo:
            raise ValueError("id_archivo no puede estar vacío")
        if not self.archivo:
            raise ValueError("archivo no puede estar vacío")