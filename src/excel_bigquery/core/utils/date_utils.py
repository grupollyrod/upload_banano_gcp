from datetime import datetime
import re


def extract_week_and_year_from_trazabilidad(codigo_trazabilidad: str) -> tuple[int, int]:
    """
    Extrae la semana y año del código de trazabilidad

    Ejemplo: 020214260625 => 260625 => 26/06/25 => semana 26, año 2025

    Args:
        codigo_trazabilidad: Código de trazabilidad

    Returns:
        Tupla (week_code, year_code)
    """
    try:
        if not codigo_trazabilidad or len(codigo_trazabilidad) < 6:
            return 0, 0

        # Tomar los últimos 6 caracteres
        fecha_str = codigo_trazabilidad[-6:]

        # Extraer día, mes, año (DDMMYY)
        if len(fecha_str) == 6:
            dia = int(fecha_str[:2])
            mes = int(fecha_str[2:4])
            anio_corto = int(fecha_str[4:6])

            # Convertir año de 2 dígitos a 4 dígitos
            # Asumimos que años 00-30 son 2000-2030, y 31-99 son 1931-1999
            if anio_corto <= 30:
                anio_completo = 2000 + anio_corto
            else:
                anio_completo = 1900 + anio_corto

            # Crear fecha y obtener semana ISO
            fecha = datetime(anio_completo, mes, dia)
            semana_iso = fecha.isocalendar()[1]

            return semana_iso, anio_completo
        else:
            return 0, 0

    except (ValueError, IndexError) as e:
        print(f"Error procesando código trazabilidad {codigo_trazabilidad}: {e}")
        return 0, 0


def is_valid_date(dia: int, mes: int, anio: int) -> bool:
    """Valida si una fecha es válida"""
    try:
        datetime(anio, mes, dia)
        return True
    except ValueError:
        return False