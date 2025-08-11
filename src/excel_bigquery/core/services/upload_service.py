import logging
from typing import Tuple, List

from src.excel_bigquery.core.services.excel_processor_service import ExcelProcessorService
from src.infrastructure.bigquery.bigquery_client import BigQueryClient
from src.infrastructure.bigquery.caja_bigquery_client import CajaBigQueryClient
from src.excel_bigquery.core.domain.models.archivo_model import ArchivoModel
from src.excel_bigquery.core.domain.models.caja_model import CajaModel

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self):
        self.excel_processor = ExcelProcessorService()
        self.bigquery_client = BigQueryClient()
        self.caja_bigquery_client = CajaBigQueryClient()

    def process_and_upload_excel_files(self, path: str, check_duplicates: bool = True,
                                       include_cajas: bool = True) -> bool:
        """
        Procesa archivos Excel y los sube a BigQuery (incluyendo cajas si está habilitado)

        Args:
            path: Ruta del directorio con archivos Excel
            check_duplicates: Si verificar duplicados antes de subir
            include_cajas: Si procesar y subir también las cajas

        Returns:
            True si el proceso fue exitoso
        """
        try:
            logger.info(f"Iniciando procesamiento de archivos en: {path}")

            if include_cajas:
                # Procesar archivos y cajas
                archivos, cajas = self.excel_processor.process_excel_files_with_cajas(path)
                logger.info(f"Procesados {len(archivos)} archivos y {len(cajas)} cajas")
            else:
                # Solo procesar archivos
                archivos = self.excel_processor.process_excel_files(path)
                cajas = []
                logger.info(f"Procesados {len(archivos)} archivos")

            if not archivos:
                logger.warning("No se encontraron archivos para procesar")
                return False

            # Verificar duplicados si está habilitado
            if check_duplicates:
                archivos = self.bigquery_client.check_existing_files(archivos)

                if not archivos:
                    logger.info("Todos los archivos ya existen en BigQuery")
                    return True

            # Subir archivos a BigQuery
            archivos_success = self.bigquery_client.upload_archivos(archivos)

            if not archivos_success:
                logger.error("Error subiendo archivos")
                return False

            # Subir cajas si están habilitadas
            if include_cajas and cajas:
                # Filtrar cajas que pertenecen a archivos que se subieron exitosamente
                archivos_ids = {archivo.id_archivo for archivo in archivos}
                cajas_filtradas = [caja for caja in cajas if caja.id_archivo in archivos_ids]

                if cajas_filtradas:
                    cajas_success = self.caja_bigquery_client.upload_cajas(cajas_filtradas)
                    if not cajas_success:
                        logger.error("Error subiendo cajas")
                        return False

            logger.info("Proceso completado exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error en el proceso: {e}")
            return False

    def get_processing_summary(self, path: str, include_cajas: bool = True) -> dict:
        """
        Obtiene un resumen del procesamiento sin subir datos

        Args:
            path: Ruta del directorio con archivos Excel
            include_cajas: Si incluir información de cajas en el resumen

        Returns:
            Diccionario con resumen del procesamiento
        """
        try:
            if include_cajas:
                archivos, cajas = self.excel_processor.process_excel_files_with_cajas(path)

                # Estadísticas de cajas por archivo
                cajas_por_archivo = {}
                for caja in cajas:
                    if caja.id_archivo not in cajas_por_archivo:
                        cajas_por_archivo[caja.id_archivo] = 0
                    cajas_por_archivo[caja.id_archivo] += 1

                return {
                    "total_files": len(archivos),
                    "total_cajas": len(cajas),
                    "warehouses": list(set(archivo.warehouse for archivo in archivos)),
                    "years": list(set(archivo.annio for archivo in archivos)),
                    "files_detail": [
                        {
                            "archivo": archivo.archivo,
                            "warehouse": archivo.warehouse,
                            "puerto": archivo.puerto,
                            "buque": archivo.buque,
                            "annio": archivo.annio,
                            "semana": archivo.semana,
                            "cajas_count": cajas_por_archivo.get(archivo.id_archivo, 0)
                        }
                        for archivo in archivos
                    ],
                    "cajas_summary": {
                        "total_dedos": sum(caja.dedos_totales for caja in cajas),
                        "peso_total_kg": sum(caja.peso_total_kg for caja in cajas),
                        "promedio_peso_caja": sum(caja.peso_promedio for caja in cajas) / len(cajas) if cajas else 0,
                        "total_uw": sum(caja.uw for caja in cajas),
                        "total_ow": sum(caja.ow for caja in cajas)
                    }
                }
            else:
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