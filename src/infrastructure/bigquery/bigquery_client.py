from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from typing import List
import logging

from src.config.settings import settings
from src.excel_bigquery.core.models.archivo_model import ArchivoModel

logger = logging.getLogger(__name__)


class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client(project=settings.project_id)
        self.dataset_id = settings.dataset_id
        self.table_id = "T1_ARCHIVOS"

    def create_dataset_if_not_exists(self):
        """Crea el dataset si no existe"""
        dataset_ref = self.client.dataset(self.dataset_id)

        try:
            self.client.get_dataset(dataset_ref)
            logger.info(f"Dataset {self.dataset_id} ya existe")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = settings.location
            dataset = self.client.create_dataset(dataset, timeout=30)
            logger.info(f"Dataset {self.dataset_id} creado")

    def create_table_if_not_exists(self):
        """Crea la tabla T1_ARCHIVOS si no existe"""
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)

        try:
            self.client.get_table(table_ref)
            logger.info(f"Tabla {self.table_id} ya existe")
        except NotFound:
            schema = [
                bigquery.SchemaField("id_archivo", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("archivo", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("warehouse", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("puerto", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("buque", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("annio", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("semana", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("spec", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("tipo", "STRING", mode="NULLABLE"),
            ]

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"Tabla {self.table_id} creada")

    def upload_archivos(self, archivos: List[ArchivoModel]) -> bool:
        """
        Sube los datos de archivos a BigQuery

        Args:
            archivos: Lista de modelos ArchivoModel

        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        if not archivos:
            logger.warning("No hay archivos para subir")
            return False

        # Crear dataset y tabla si no existen
        self.create_dataset_if_not_exists()
        self.create_table_if_not_exists()

        # Convertir modelos a DataFrame
        df = self._models_to_dataframe(archivos)

        # Subir datos
        return self._upload_dataframe(df)

    def _models_to_dataframe(self, archivos: List[ArchivoModel]) -> pd.DataFrame:
        """Convierte lista de modelos a DataFrame"""
        data = []
        for archivo in archivos:
            data.append({
                'id_archivo': archivo.id_archivo,
                'archivo': archivo.archivo,
                'warehouse': archivo.warehouse,
                'puerto': archivo.puerto,
                'buque': archivo.buque,
                'annio': archivo.annio,
                'semana': archivo.semana,
                'spec': archivo.spec,
                'tipo': archivo.tipo
            })

        return pd.DataFrame(data)

    def _upload_dataframe(self, df: pd.DataFrame) -> bool:
        """Sube DataFrame a BigQuery"""
        try:
            table_id = f"{settings.project_id}.{self.dataset_id}.{self.table_id}"

            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",  # Agregar datos sin sobrescribir
                autodetect=False
            )

            job = self.client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )

            job.result()  # Esperar a que termine el job

            logger.info(f"Subidos {len(df)} registros a {table_id}")
            return True

        except Exception as e:
            logger.error(f"Error subiendo datos a BigQuery: {e}")
            return False

    def check_existing_files(self, archivos: List[ArchivoModel]) -> List[ArchivoModel]:
        """
        Verifica qué archivos ya existen en BigQuery para evitar duplicados

        Args:
            archivos: Lista de archivos a verificar

        Returns:
            Lista de archivos que no existen en BigQuery
        """
        if not archivos:
            return []

        # Crear lista de IDs para consultar
        ids_to_check = [archivo.id_archivo for archivo in archivos]
        ids_str = "', '".join(ids_to_check)

        query = f"""
        SELECT id_archivo 
        FROM `{settings.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE id_archivo IN ('{ids_str}')
        """

        try:
            results = self.client.query(query).result()
            existing_ids = {row.id_archivo for row in results}

            # Filtrar archivos que no existen
            new_archivos = [
                archivo for archivo in archivos
                if archivo.id_archivo not in existing_ids
            ]

            logger.info(f"Archivos existentes: {len(existing_ids)}, Archivos nuevos: {len(new_archivos)}")
            return new_archivos

        except Exception as e:
            logger.warning(f"Error verificando archivos existentes: {e}. Subiendo todos los archivos.")
            return archivos