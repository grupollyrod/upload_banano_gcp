import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # GCP Configuration
    google_credentials: str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    project_id: str = os.getenv('PROJECT_ID', '')
    dataset_id: str = os.getenv('DATASET_ID', 'bd_banano')
    location: str = os.getenv('LOCATION', 'US')

    # Paths Configuration - Solo las que vamos a usar
    base_path: str = os.getenv('BASE_PATH', '')
    nittsu_path: str = os.getenv('NITTSU_PATH', '')
    kobe_path: str = os.getenv('KOBE_PATH', '')
    hakata_path: str = os.getenv('HAKATA_PATH', '')

    # Processing Configuration
    spec_value: int = int(os.getenv('SPEC_VALUE', '30'))
    tipo_default: str = os.getenv('TIPO_DEFAULT', 'CGC')

    # Logging Configuration
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'logs/app.log')

    def get_available_paths(self) -> dict:
        """Retorna las rutas disponibles para procesar"""
        paths = {
            'nittsu': self.nittsu_path,
            'kobe': self.kobe_path,
            'hakata': self.hakata_path
        }
        # Filtrar solo las rutas que existen y no están vacías
        return {k: v for k, v in paths.items() if v and os.path.exists(v)}

    def validate(self):
        """Valida que las configuraciones requeridas estén presentes"""
        if not self.project_id:
            raise ValueError("PROJECT_ID es requerido")
        if not self.google_credentials:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS es requerido")

    def setup_logging(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )


settings = Settings()
settings.setup_logging()