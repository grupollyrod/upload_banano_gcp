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
        Tupla con lista de archivos (nombre_limpio, ruta_completa) y nombre del warehouse
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"La ruta {path} no existe")

    # Filtrar archivos Excel excluyendo temporales
    todos_archivos = os.listdir(path)
    archivos_excel = []

    for archivo in todos_archivos:
        # Filtrar archivos temporales de Excel (empiezan con ~$)
        if archivo.startswith('~$'):
            continue

        # Solo archivos Excel
        if archivo.endswith(('.xlsx', '.xls')):
            # Limpiar nombre del archivo (quitar los primeros 3 caracteres)
            nombre_limpio = _limpiar_nombre_archivo(archivo)
            ruta_completa = os.path.join(path, archivo)
            archivos_excel.append((nombre_limpio, ruta_completa))

    if not archivos_excel:
        raise ValueError(f"No se encontraron archivos Excel válidos en {path}")

    carpeta_padre = os.path.basename(os.path.normpath(path))
    warehouse = _determinar_warehouse(carpeta_padre)

    # Validar que no sea Nittsu Mathias (que no procesamos aún)
    if "MATIAS" in carpeta_padre.upper() or "MATHIAS" in carpeta_padre.upper():
        raise ValueError(f"Nittsu Mathias no está configurado aún. Carpeta: {carpeta_padre}")

    return archivos_excel, warehouse


def _limpiar_nombre_archivo(nombre_archivo: str) -> str:
    """
    Limpia el nombre del archivo quitando los primeros 3 caracteres
    Ejemplo: "日通 WK26 MYNY.xlsx" -> "WK26 MYNY.xlsx"

    Args:
        nombre_archivo: Nombre original del archivo

    Returns:
        Nombre del archivo sin los primeros 3 caracteres
    """
    if len(nombre_archivo) > 3:
        nombre_limpio = nombre_archivo[3:]
        # Limpiar espacios adicionales al inicio
        nombre_limpio = nombre_limpio.lstrip()
        return nombre_limpio
    else:
        # Si el archivo tiene menos de 3 caracteres, devolver original
        return nombre_archivo


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


def get_excel_files_info(path: str) -> dict:
    """
    Obtiene información detallada de los archivos Excel en una ruta

    Args:
        path: Ruta del directorio

    Returns:
        Diccionario con información de los archivos
    """
    try:
        archivos, warehouse = excel_reader(path)

        archivos_info = []
        for nombre_limpio, ruta_completa in archivos:
            nombre_original = os.path.basename(ruta_completa)
            archivos_info.append({
                'nombre_original': nombre_original,
                'nombre_limpio': nombre_limpio,
                'ruta_completa': ruta_completa,
                'tamaño_kb': round(os.path.getsize(ruta_completa) / 1024, 2)
            })

        return {
            'warehouse': warehouse,
            'total_archivos': len(archivos_info),
            'archivos': archivos_info
        }

    except Exception as e:
        return {'error': str(e)}