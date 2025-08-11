from typing import List
from openpyxl import load_workbook

from src.excel_bigquery.core.domain.models.archivo_model import ArchivoModel
from src.excel_bigquery.core.use_cases.interfaces.excel_reader import excel_reader
from src.config.settings import settings


class ExcelProcessorService:

    def process_excel_files(self, path: str) -> List[ArchivoModel]:
        """
        Procesa todos los archivos Excel en el directorio especificado

        Args:
            path: Ruta del directorio con archivos Excel

        Returns:
            Lista de modelos ArchivoModel
        """
        excel_files, warehouse = excel_reader(path)
        archivos_models = []

        for nombre_limpio, ruta_archivo in excel_files:
            try:
                archivo_model = self._process_single_file(
                    nombre_limpio, ruta_archivo, warehouse
                )
                archivos_models.append(archivo_model)
            except Exception as e:
                print(f"Error procesando {nombre_limpio}: {e}")
                continue

        return archivos_models

    def _process_single_file(self, nombre_archivo: str, ruta_archivo: str, warehouse: str) -> ArchivoModel:
        """
        Procesa un archivo Excel individual

        Args:
            nombre_archivo: Nombre limpio del archivo (sin los primeros 3 caracteres)
            ruta_archivo: Ruta completa del archivo
            warehouse: Tipo de warehouse

        Returns:
            Modelo ArchivoModel con los datos extraídos
        """
        wb_obj = load_workbook(ruta_archivo)
        sheet_obj = wb_obj.active

        # Extraer datos según las celdas especificadas
        puerto = str(sheet_obj["G1"].value).upper() if sheet_obj["G1"].value else ""
        buque = str(sheet_obj["B1"].value) if sheet_obj["B1"].value else ""
        semana = int(sheet_obj["T1"].value) if sheet_obj["T1"].value else 0
        n_archivo = str(sheet_obj["Q1"].value) if sheet_obj["Q1"].value else ""

        # Extraer año de A2 (formato: "Year 2025")
        anio_texto = str(sheet_obj["A2"].value) if sheet_obj["A2"].value else ""
        annio = self._extract_year(anio_texto)

        # Crear ID del archivo usando el nombre limpio
        id_archivo = f"{warehouse}_{annio}_{nombre_archivo}_{n_archivo}"

        return ArchivoModel(
            id_archivo=id_archivo,
            archivo=nombre_archivo,  # Usar nombre limpio
            warehouse=warehouse,
            puerto=puerto,
            buque=buque,
            annio=annio,
            semana=semana,
            spec=settings.spec_value,
            tipo=settings.tipo_default
        )

    def _extract_year(self, anio_texto: str) -> int:
        """
        Extrae el año de un texto como 'Year 2025'

        Args:
            anio_texto: Texto que contiene el año

        Returns:
            Año como entero
        """
        try:
            if "Year" in anio_texto:
                return int(anio_texto.split()[-1])
            else:
                # Si no tiene formato esperado, intentar extraer los últimos 4 dígitos
                return int(anio_texto[-4:])
        except (ValueError, IndexError):
            return 0