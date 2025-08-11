import sys
import os
from typing import Dict, Optional

# Agregar src al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings
from src.excel_bigquery.core.services.upload_service import UploadService


class MenuPrincipal:
    def __init__(self):
        self.upload_service = UploadService()
        self.warehouses_disponibles = self._get_warehouses_disponibles()

    def _get_warehouses_disponibles(self) -> Dict[str, str]:
        """Obtiene los warehouses disponibles basado en rutas existentes"""
        warehouses = {}

        if settings.nittsu_path and os.path.exists(settings.nittsu_path):
            warehouses['1'] = {'nombre': 'NITTSU', 'path': settings.nittsu_path}

        if settings.kobe_path and os.path.exists(settings.kobe_path):
            warehouses['2'] = {'nombre': 'KOBE', 'path': settings.kobe_path}

        if settings.hakata_path and os.path.exists(settings.hakata_path):
            warehouses['3'] = {'nombre': 'HAKATA', 'path': settings.hakata_path}

        return warehouses

    def mostrar_menu(self):
        """Muestra el menú principal"""
        print("\n" + "=" * 50)
        print("🍌 SISTEMA DE CARGA DE ARCHIVOS BANANA - BigQuery 🍌")
        print("=" * 50)

        if not self.warehouses_disponibles:
            print("❌ No hay warehouses configurados o las rutas no existen.")
            print("   Por favor revisa tu archivo .env")
            return

        print("\n📂 Warehouses disponibles:")
        for key, warehouse in self.warehouses_disponibles.items():
            print(f"   {key}. {warehouse['nombre']}")

        print(f"   4. Procesar TODOS los warehouses")
        print(f"   5. Vista previa (sin subir a BigQuery)")
        print(f"   6. Procesar SOLO archivos (sin cajas)")
        print(f"   0. Salir")
        print("-" * 50)

    def procesar_opcion(self, opcion: str) -> bool:
        """
        Procesa la opción seleccionada

        Returns:
            True si debe continuar el menú, False si debe salir
        """
        if opcion == '0':
            print("👋 ¡Hasta luego!")
            return False

        elif opcion in self.warehouses_disponibles:
            warehouse = self.warehouses_disponibles[opcion]
            self._procesar_warehouse_individual(warehouse['nombre'], warehouse['path'])

        elif opcion == '4':
            self._procesar_todos_warehouses()

        elif opcion == '5':
            self._mostrar_vista_previa()

        elif opcion == '6':
            self._procesar_solo_archivos()

        else:
            print("❌ Opción no válida. Por favor intenta de nuevo.")

        return True

    def _procesar_warehouse_individual(self, nombre: str, path: str):
        """Procesa un warehouse individual con cajas"""
        print(f"\n🚀 Procesando warehouse: {nombre}")
        print(f"📁 Ruta: {path}")

        # Mostrar vista previa primero
        print("\n📋 Vista previa:")
        resumen = self.upload_service.get_processing_summary(path, include_cajas=True)

        if 'error' in resumen:
            print(f"❌ Error obteniendo vista previa: {resumen['error']}")
            return

        print(f"   📄 Archivos encontrados: {resumen['total_files']}")
        print(f"   📦 Cajas encontradas: {resumen.get('total_cajas', 0)}")
        print(f"   🏭 Warehouses: {', '.join(resumen['warehouses'])}")
        print(f"   📅 Años: {', '.join(map(str, resumen['years']))}")

        if 'cajas_summary' in resumen:
            print(f"   🍌 Total dedos: {resumen['cajas_summary']['total_dedos']}")
            print(f"   ⚖️ Peso total: {resumen['cajas_summary']['peso_total_kg']:.2f} kg")

        if resumen['total_files'] == 0:
            print("❌ No hay archivos para procesar.")
            return

        # Confirmar antes de subir
        confirmacion = input(
            f"\n¿Procesar y subir {resumen['total_files']} archivos y {resumen.get('total_cajas', 0)} cajas a BigQuery? (s/N): ").lower()

        if confirmacion in ['s', 'si', 'sí', 'y', 'yes']:
            print(f"\n⏳ Subiendo archivos y cajas de {nombre}...")
            exito = self.upload_service.process_and_upload_excel_files(path, include_cajas=True)

            if exito:
                print(f"✅ Archivos y cajas de {nombre} subidos exitosamente!")
            else:
                print(f"❌ Error procesando archivos de {nombre}")
        else:
            print("❌ Operación cancelada")

    def _procesar_solo_archivos(self):
        """Procesa todos los warehouses pero solo archivos, sin cajas"""
        print(f"\n📁 PROCESANDO SOLO ARCHIVOS (SIN CAJAS)")
        print("-" * 50)

        # Mostrar menú de warehouses
        print("\nSelecciona warehouse para procesar solo archivos:")
        for key, warehouse in self.warehouses_disponibles.items():
            print(f"   {key}. {warehouse['nombre']}")
        print("   0. Volver al menú principal")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == '0':
            return

        if opcion in self.warehouses_disponibles:
            warehouse = self.warehouses_disponibles[opcion]

            print(f"\n🚀 Procesando SOLO archivos de: {warehouse['nombre']}")
            resumen = self.upload_service.get_processing_summary(warehouse['path'], include_cajas=False)

            if 'error' in resumen:
                print(f"❌ Error: {resumen['error']}")
                return

            print(f"   📄 Archivos encontrados: {resumen['total_files']}")

            if resumen['total_files'] > 0:
                confirmacion = input(f"\n¿Subir solo {resumen['total_files']} archivos (sin cajas)? (s/N): ").lower()

                if confirmacion in ['s', 'si', 'sí', 'y', 'yes']:
                    print(f"\n⏳ Subiendo solo archivos...")
                    exito = self.upload_service.process_and_upload_excel_files(warehouse['path'], include_cajas=False)

                    if exito:
                        print(f"✅ Archivos subidos exitosamente!")
                    else:
                        print(f"❌ Error procesando archivos")
                else:
                    print("❌ Operación cancelada")
        else:
            print("❌ Opción no válida")

    def _procesar_todos_warehouses(self):
        """Procesa todos los warehouses disponibles con cajas"""
        print(f"\n🚀 Procesando TODOS los warehouses disponibles...")

        total_archivos = 0
        total_cajas = 0
        warehouses_procesados = []

        # Vista previa de todos
        for key, warehouse in self.warehouses_disponibles.items():
            print(f"\n📋 Vista previa - {warehouse['nombre']}:")
            resumen = self.upload_service.get_processing_summary(warehouse['path'], include_cajas=True)

            if 'error' not in resumen:
                print(f"   📄 Archivos: {resumen['total_files']}")
                print(f"   📦 Cajas: {resumen.get('total_cajas', 0)}")
                total_archivos += resumen['total_files']
                total_cajas += resumen.get('total_cajas', 0)
                warehouses_procesados.append(warehouse)
            else:
                print(f"   ❌ Error: {resumen['error']}")

        if total_archivos == 0:
            print("❌ No hay archivos para procesar en ningún warehouse.")
            return

        # Confirmar procesamiento masivo
        print(f"\n📊 RESUMEN TOTAL:")
        print(f"   🏭 Warehouses a procesar: {len(warehouses_procesados)}")
        print(f"   📄 Total de archivos: {total_archivos}")
        print(f"   📦 Total de cajas: {total_cajas}")

        confirmacion = input(f"\n¿Procesar y subir TODOS los archivos y cajas a BigQuery? (s/N): ").lower()

        if confirmacion in ['s', 'si', 'sí', 'y', 'yes']:
            exitos = 0
            for warehouse in warehouses_procesados:
                print(f"\n⏳ Procesando {warehouse['nombre']}...")
                exito = self.upload_service.process_and_upload_excel_files(warehouse['path'], include_cajas=True)

                if exito:
                    print(f"   ✅ {warehouse['nombre']} completado")
                    exitos += 1
                else:
                    print(f"   ❌ Error en {warehouse['nombre']}")

            print(f"\n🎉 Proceso completado: {exitos}/{len(warehouses_procesados)} warehouses exitosos")
        else:
            print("❌ Operación cancelada")

    def _mostrar_vista_previa(self):
        """Muestra vista previa de todos los warehouses sin procesar"""
        print(f"\n👀 VISTA PREVIA - Todos los warehouses")
        print("-" * 50)

        total_global_archivos = 0
        total_global_cajas = 0

        for key, warehouse in self.warehouses_disponibles.items():
            print(f"\n🏭 {warehouse['nombre']}:")
            print(f"   📁 Ruta: {warehouse['path']}")

            resumen = self.upload_service.get_processing_summary(warehouse['path'], include_cajas=True)

            if 'error' not in resumen:
                print(f"   📄 Archivos encontrados: {resumen['total_files']}")
                print(f"   📦 Cajas encontradas: {resumen.get('total_cajas', 0)}")

                if resumen['total_files'] > 0:
                    print(f"   📅 Años: {', '.join(map(str, resumen['years']))}")
                    print(f"   📋 Archivos:")
                    for archivo in resumen['files_detail'][:3]:  # Mostrar solo los primeros 3
                        cajas_count = archivo.get('cajas_count', 0)
                        print(
                            f"      - {archivo['archivo']} ({archivo['annio']}, Sem: {archivo['semana']}, Cajas: {cajas_count})")

                    if len(resumen['files_detail']) > 3:
                        print(f"      ... y {len(resumen['files_detail']) - 3} más")

                    if 'cajas_summary' in resumen:
                        print(f"   🍌 Total dedos: {resumen['cajas_summary']['total_dedos']}")
                        print(f"   ⚖️ Peso total: {resumen['cajas_summary']['peso_total_kg']:.2f} kg")

                total_global_archivos += resumen['total_files']
                total_global_cajas += resumen.get('total_cajas', 0)
            else:
                print(f"   ❌ Error: {resumen['error']}")

        print(f"\n📊 TOTAL GLOBAL:")
        print(f"   📄 Archivos: {total_global_archivos}")
        print(f"   📦 Cajas: {total_global_cajas}")

    def ejecutar(self):
        """Ejecuta el menú principal"""
        try:
            # Validar configuración
            settings.validate()

            while True:
                self.mostrar_menu()
                opcion = input("\nSelecciona una opción: ").strip()

                if not self.procesar_opcion(opcion):
                    break

                # Pausa antes de mostrar el menú nuevamente
                input("\nPresiona Enter para continuar...")

        except KeyboardInterrupt:
            print("\n\n👋 Proceso interrumpido por el usuario. ¡Hasta luego!")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            print("Por favor verifica tu configuración en el archivo .env")


def main():
    """Función principal del programa"""
    menu = MenuPrincipal()
    menu.ejecutar()


if __name__ == "__main__":
    main()