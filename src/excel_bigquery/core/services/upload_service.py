import logging

from src.excel_bigquery.core.services.excel_processor_service import ExcelProcessorService
from src.infrastructure.bigquery.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self):
        self.excel_processor = ExcelProcessorService()
        self.bigquery_client = BigQueryClient()

    def process_and_upload_excel_files(self, path: str, check_duplicates: bool = True) -> bool:
        """
        Procesa archivos Excel y los sube a BigQuery

        Args:
            path: Ruta del directorio con archivos Excel
            check_duplicates: Si verificar duplicados antes de subir

        Returns:
            True si el proceso fue exitoso
        """
        try:
            logger.info(f"Iniciando procesamiento de archivos en: {path}")

            # Procesar archivos Excel
            archivos = self.excel_processor.process_excel_files(path)

            if not archivos:
                logger.warning("No se encontraron archivos para procesar")
                return False

            logger.info(f"Procesados {len(archivos)} archivos")

            # Verificar duplicados si está habilitado
            if check_duplicates:
                archivos = self.bigquery_client.check_existing_files(archivos)

                if not archivos:
                    logger.info("Todos los archivos ya existen en BigQuery")
                    return True

            # Subir a BigQuery
            success = self.bigquery_client.upload_archivos(archivos)

            if success:
                logger.info("Proceso completado exitosamente")
            else:
                logger.error("Error en el proceso de subida")

            return success

        except Exception as e:
            logger.error(f"Error en el proceso: {e}")
            return False

    def get_processing_summary(self, path: str) -> dict:
        """
        Obtiene un resumen del procesamiento sin subir datos

        Args:
            path: Ruta del directorio con archivos Excel

        Returns:
            Diccionario con resumen del procesamiento
        """
        try:
            archivos = self.excel_processor.process_excel_files(path)

            return {
                "total_files": len(archivos),
                "warehouses": list(set(archivo.warehouse for archivo in archivos)),
                "years": list(set(archivo.annio for archivo in archivos)),
                "files_detail": [
                    {
                        "archivo": archivo.archivo,
                        "warehouse": archivo.warehouse,
                        "puerto": archivo.puerto,
                        "buque": archivo.buque,
                        "annio": archivo.annio,
                        "semana": archivo.semana
                    }
                    for archivo in archivos
                ]
            }

        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {"error": str(e)}