import os
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

    # Paths Configuration
    base_path: str = os.getenv('BASE_PATH', '')
    mathias_path: str = os.getenv('MATHIAS_PATH', '')
    nittsu_path: str = os.getenv('NITTSU_PATH', '')
    kobe_path: str = os.getenv('KOBE_PATH', '')
    hakata_path: str = os.getenv('HAKATA_PATH', '')

    # Processing Configuration
    spec_value: int = int(os.getenv('SPEC_VALUE', '30'))
    tipo_default: str = os.getenv('TIPO_DEFAULT', 'CGC')

    def validate(self):
        """Valida que las configuraciones requeridas estén presentes"""
        if not self.project_id:
            raise ValueError("PROJECT_ID es requerido")
        if not self.google_credentials:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS es requerido")


settings = Settings()