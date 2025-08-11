import os
from typing import List, Tuple
from enum import Enum


class WarehouseType(Enum):
    NITTSU = "NITTSU"
    KOBE = "KOBE"
    HAKATA = "HAKATA"
    DESCONOCIDO = "DESCONOCIDO"


def excel_reader(path: str) -> Tuple[List[Tuple[str, str]], str]:
    """
    Lee los archivos Excel de un directorio y determina el warehouse

    Args:
        path: Ruta del directorio

    Returns:
        Tupla con lista de archivos y nombre del warehouse
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"La ruta {path} no existe")

    archivos = [f for f in os.listdir(path) if f.endswith(('.xlsx', '.xls'))]

    if not archivos:
        raise ValueError(f"No se encontraron archivos Excel en {path}")

    carpeta_padre = os.path.basename(os.path.normpath(path))
    warehouse = _determinar_warehouse(carpeta_padre)

    # Validar que no sea Nittsu Mathias (que no procesamos aún)
    if "MATIAS" in carpeta_padre.upper() or "MATHIAS" in carpeta_padre.upper():
        raise ValueError(f"Nittsu Mathias no está configurado aún. Carpeta: {carpeta_padre}")

    return [(archivo, os.path.join(path, archivo)) for archivo in archivos], warehouse


def _determinar_warehouse(carpeta_nombre: str) -> str:
    """Determina el tipo de warehouse basado en el nombre de la carpeta"""
    carpeta_upper = carpeta_nombre.upper()

    # Excluir Nittsu Mathias por ahora
    if "MATIAS" in carpeta_upper or "MATHIAS" in carpeta_upper:
        return "NITTSU_MATHIAS_NO_CONFIGURADO"
    elif "NITTSU" in carpeta_upper:
        return WarehouseType.NITTSU.value
    elif "KOBE" in carpeta_upper:
        return WarehouseType.KOBE.value
    elif "HAKATA" in carpeta_upper:
        return WarehouseType.HAKATA.value
    else:
        return WarehouseType.DESCONOCIDO.value