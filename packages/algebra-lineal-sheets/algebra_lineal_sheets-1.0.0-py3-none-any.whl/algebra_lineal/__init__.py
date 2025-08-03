"""
📚 ALGEBRA LINEAL - Paquete para Google Sheets
==============================================

Álgebra lineal simplificada con Google Sheets integration.
Perfecto para estudiantes y profesores.

Instalación:
    pip install algebra-lineal-sheets

Uso básico:
    from algebra_lineal import *
    configurar()
    importar('A', 'B')
    C = A @ B
    exportar('C')

Autor: Francisco Pérez Mogollón
Email: fperez9@utpl.edu.ec
Versión: 1.0.0
"""

# Importar todas las funciones principales del módulo core
from .core import (
    configurar,
    workspace,
    importar,
    exportar,
    cambiar_sheet,
    ayuda,
    version,
    listar_variables_exportables
)

# Definir qué se importa cuando alguien hace "from algebra_lineal import *"
__all__ = [
    'configurar',
    'workspace',
    'importar',
    'exportar',
    'cambiar_sheet',
    'ayuda',
    'version',
    'listar_variables_exportables'
]

# Metadatos del paquete (IMPORTANTE: mantener sincronizado con pyproject.toml)
__version__ = "1.0.0"
__author__ = "Francisco Pérez Mogollón"
__email__ = "fperez9@utpl.edu.ec"
__description__ = "Álgebra lineal simplificada con integración a Google Sheets"
__url__ = "https://pypi.org/project/algebra-lineal-sheets/"

# Mensaje de bienvenida al importar (más profesional para PyPI)
print("📚 ALGEBRA LINEAL v1.0.0")
print("🎓 Para estudiantes de álgebra lineal")
print("🔧 Ejecuta: configurar() para empezar")
print("📖 Ayuda completa: ayuda()")
print("🔗 PyPI: https://pypi.org/project/algebra-lineal-sheets/")

# Función de conveniencia para verificar instalación


def verificar_instalacion():
    """
    Verifica que el paquete esté instalado correctamente.
    """
    try:
        import numpy
        import gspread
        from google.auth import default
        print("✅ Todas las dependencias están instaladas correctamente")
        print("🚀 ¡Listo para usar algebra_lineal!")
        return True
    except ImportError as e:
        print(f"❌ Error: Dependencia faltante - {e}")
        print("💡 Ejecuta: pip install --upgrade algebra-lineal-sheets")
        return False
