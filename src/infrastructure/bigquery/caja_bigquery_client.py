from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from typing import List
import logging

from src.config.settings import settings
from src.excel_bigquery.core.domain.models.caja_model import CajaModel

logger = logging.getLogger(__name__)


class CajaBigQueryClient:
    def __init__(self):
        self.client = bigquery.Client(project=settings.project_id)
        self.dataset_id = settings.dataset_id
        self.table_id = "T2_CAJAS"

    def create_table_if_not_exists(self):
        """Crea la tabla T2_CAJAS si no existe"""
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)

        try:
            self.client.get_table(table_ref)
            logger.info(f"Tabla {self.table_id} ya existe")
        except NotFound:
            schema = [
                bigquery.SchemaField("id_caja", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("id_archivo", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("nombre_caja", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("codigo_container", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("codigo_hacienda", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("codigo_trazabilidad", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("nombre_hacienda", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("temperatura", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("dedos_totales", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("peso_bruto_kg", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("peso_total_kg", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("cantidad_observaciones", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("dedos_afectados_totales", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("peso_promedio", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("week_code", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("year_code", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("spec", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("uw", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("ow", "INTEGER", mode="NULLABLE"),
            ]

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"Tabla {self.table_id} creada")

    def upload_cajas(self, cajas: List[CajaModel]) -> bool:
        """
        Sube los datos de cajas a BigQuery

        Args:
            cajas: Lista de modelos CajaModel

        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        if not cajas:
            logger.warning("No hay cajas para subir")
            return False

        # Crear tabla si no existe
        self.create_table_if_not_exists()

        # Convertir modelos a DataFrame
        df = self._models_to_dataframe(cajas)

        # Subir datos
        return self._upload_dataframe(df)

    def _models_to_dataframe(self, cajas: List[CajaModel]) -> pd.DataFrame:
        """Convierte lista de modelos a DataFrame"""
        data = []
        for caja in cajas:
            data.append({
                'id_caja': caja.id_caja,
                'id_archivo': caja.id_archivo,
                'nombre_caja': caja.nombre_caja,
                'codigo_container': caja.codigo_container,
                'codigo_hacienda': caja.codigo_hacienda,
                'codigo_trazabilidad': caja.codigo_trazabilidad,
                'nombre_hacienda': caja.nombre_hacienda,
                'temperatura': caja.temperatura,
                'dedos_totales': caja.dedos_totales,
                'peso_bruto_kg': caja.peso_bruto_kg,
                'peso_total_kg': caja.peso_total_kg,
                'cantidad_observaciones': caja.cantidad_observaciones,
                'dedos_afectados_totales': caja.dedos_afectados_totales,
                'peso_promedio': caja.peso_promedio,
                'week_code': caja.week_code,
                'year_code': caja.year_code,
                'spec': caja.spec,
                'uw': caja.uw,
                'ow': caja.ow
            })

        return pd.DataFrame(data)

    def _upload_dataframe(self, df: pd.DataFrame) -> bool:
        """Sube DataFrame a BigQuery"""
        try:
            table_id = f"{settings.project_id}.{self.dataset_id}.{self.table_id}"

            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                autodetect=False
            )

            job = self.client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )

            job.result()  # Esperar a que termine el job

            logger.info(f"Subidas {len(df)} cajas a {table_id}")
            return True

        except Exception as e:
            logger.error(f"Error subiendo cajas a BigQuery: {e}")
            return False