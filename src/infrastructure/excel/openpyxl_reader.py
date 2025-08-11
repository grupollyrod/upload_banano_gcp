import sys
import os
import pandas as pd

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.excel_bigquery.core.services.upload_service import UploadService


def load_excel_to_dataframe(path: str) -> pd.DataFrame:
    """
    Procesa archivos Excel y retorna un DataFrame con los datos

    Args:
        path: Ruta del directorio con archivos Excel

    Returns:
        DataFrame con los datos procesados
    """
    from src.excel_bigquery.core.services.excel_processor_service import ExcelProcessorService

    processor = ExcelProcessorService()
    archivos_models = processor.process_excel_files(path)

    if not archivos_models:
        return pd.DataFrame()

    # Convertir modelos a diccionarios para DataFrame
    data_list = []
    for modelo in archivos_models:
        data_list.append({
            'id_archivo': modelo.id_archivo,
            'archivo': modelo.archivo,
            'warehouse': modelo.warehouse,
            'puerto': modelo.puerto,
            'buque': modelo.buque,
            'annio': modelo.annio,
            'semana': modelo.semana,
            'spec': modelo.spec,
            'tipo': modelo.tipo
        })

    return pd.DataFrame(data_list)


def process_and_upload_to_bigquery(path: str, check_duplicates: bool = True) -> bool:
    """
    Procesa archivos Excel y los sube a BigQuery

    Args:
        path: Ruta del directorio con archivos Excel
        check_duplicates: Si verificar duplicados antes de subir

    Returns:
        True si el proceso fue exitoso
    """
    upload_service = UploadService()
    return upload_service.process_and_upload_excel_files(path, check_duplicates)


def get_processing_preview(path: str) -> dict:
    """
    Obtiene una vista previa del procesamiento sin subir datos

    Args:
        path: Ruta del directorio con archivos Excel

    Returns:
        Diccionario con información del procesamiento
    """
    upload_service = UploadService()
    return upload_service.get_processing_summary(path)