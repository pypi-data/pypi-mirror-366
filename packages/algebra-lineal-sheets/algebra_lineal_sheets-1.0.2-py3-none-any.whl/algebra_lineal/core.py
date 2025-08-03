"""
📚 ALGEBRA LINEAL - Módulo Core
==============================

Funciones principales para trabajar con álgebra lineal y Google Sheets.
Este módulo contiene toda la lógica del sistema.

Instalado desde PyPI: pip install algebra-lineal-sheets
"""

import gspread
from google.auth import default
import numpy as np
import re
import inspect

# Variables globales del paquete
gc = None
spreadsheet_name = 'matrices'


class MatrixLoader:
    """Clase auxiliar para cargar y gestionar matrices."""

    def __init__(self):
        self._datos = {}

    def __getattr__(self, name):
        if name in self._datos:
            return self._datos[name]
        raise AttributeError(f"No se encontró la matriz '{name}'")

    def __repr__(self):
        return f"MatrixLoader con matrices: {list(self._datos.keys())}"

    def listar_matrices(self):
        """Muestra todas las matrices disponibles."""
        if not self._datos:
            print("⚠️  No hay matrices cargadas")
            return

        print("📊 Matrices cargadas:")
        for nombre, matriz in self._datos.items():
            if isinstance(matriz, np.ndarray):
                print(f"  • {nombre}: {matriz.shape}")
            else:
                print(f"  • {nombre}: {matriz} (escalar)")


def configurar():
    """
    🔧 Configuración inicial del sistema.

    Autentica con Google y establece la conexión con Google Sheets.
    Ejecutar UNA VEZ al inicio de cada sesión.

    Returns:
        bool: True si la configuración fue exitosa
    """
    global gc

    try:
        # Verificar si estamos en Google Colab
        try:
            from google.colab import auth
            auth.authenticate_user()
            print("✅ Autenticación de Google Colab completada")
        except ImportError:
            print("ℹ️  Configurando autenticación local...")

        # Establecer conexión con Google Sheets
        creds, _ = default()
        gc = gspread.authorize(creds)

        print("✅ Conexión con Google Sheets establecida")
        print("📝 Asegúrate de tener un Google Sheet llamado 'matrices'")
        print("📋 Con pestañas nombradas: A, B, v, etc.")
        print("📖 Usa ayuda() para ver todos los comandos disponibles")

        return True

    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print("💡 Soluciones:")
        print("   • En Google Colab: Reinicia runtime y vuelve a intentar")
        print("   • Localmente: Configura credenciales de Google Cloud")
        print("   • Verifica conexión a internet")
        return False


def cambiar_sheet(nombre):
    """
    📝 Cambiar el Google Sheet de trabajo.

    Args:
        nombre (str): Nombre del Google Sheet
    """
    global spreadsheet_name
    spreadsheet_name = nombre
    print(f"📋 Ahora trabajando con el sheet: '{nombre}'")


def _verificar_configuracion():
    """Verifica que el sistema esté configurado."""
    if gc is None:
        print("❌ Sistema no configurado.")
        print("🔧 Ejecuta: configurar()")
        print("📦 Instalado desde: pip install algebra-lineal-sheets")
        return False
    return True


def _limpiar_nombre_variable(nombre):
    """Convierte nombre de pestaña en variable válida de Python."""
    if not nombre:
        return "variable_sin_nombre"

    nombre_limpio = re.sub(r'[^a-zA-Z0-9_]', '_', nombre)
    if nombre_limpio and nombre_limpio[0].isdigit():
        nombre_limpio = f"var_{nombre_limpio}"
    return nombre_limpio or "variable_sin_nombre"


def _procesar_datos_mixtos(data):
    """Procesa datos que pueden contener valores no numéricos."""
    try:
        resultado = []
        for fila in data:
            fila_procesada = []
            for celda in fila:
                if celda == '' or celda is None:
                    fila_procesada.append(0.0)
                else:
                    try:
                        fila_procesada.append(float(celda))
                    except ValueError:
                        fila_procesada.append(0.0)
            resultado.append(fila_procesada)
        return np.array(resultado)
    except Exception:
        raise ValueError("No se pudieron procesar los datos")


def workspace(sheet_name=None):
    """
    🏢 Muestra todas las matrices disponibles en Google Sheets.

    Args:
        sheet_name (str, optional): Nombre del sheet. Si None, usa el configurado.

    Returns:
        dict: Información del workspace
    """
    if not _verificar_configuracion():
        return {}

    nombre_sheet = sheet_name or spreadsheet_name

    try:
        spreadsheet = gc.open(nombre_sheet)
        print(f"🏢 WORKSPACE: '{nombre_sheet}'")
        print("=" * 75)
        print(f"{'#':<3} {'NOMBRE':<20} {'DIMENSIONES':<12} {'TIPO':<15}")
        print("-" * 75)

        workspace_info = {}

        for i, worksheet in enumerate(spreadsheet.worksheets(), 1):
            nombre = worksheet.title

            try:
                data = worksheet.get_all_values()

                if not data:
                    print(f"{i:<3} {nombre:<20} {'VACÍA':<12} {'⚠️  Vacía':<15}")
                    workspace_info[nombre] = {
                        'tipo': 'vacía', 'dimensiones': None}
                    continue

                # Filtrar datos y obtener dimensiones ORIGINALES de Google Sheets
                datos_filtrados = []
                for fila in data:
                    fila_filtrada = [
                        celda for celda in fila if celda.strip() != '']
                    if fila_filtrada:
                        datos_filtrados.append(fila_filtrada)

                if not datos_filtrados:
                    print(f"{i:<3} {nombre:<20} {'VACÍA':<12} {'⚠️  Vacía':<15}")
                    workspace_info[nombre] = {
                        'tipo': 'vacía', 'dimensiones': None}
                    continue

                # DIMENSIONES REALES en Google Sheets (esto es lo que importa)
                filas_sheets = len(datos_filtrados)
                cols_sheets = max(len(fila) for fila in datos_filtrados)

                # Determinar tipo basado en LAYOUT ORIGINAL en Google Sheets
                if filas_sheets == 1 and cols_sheets == 1:
                    tipo = "📊 Escalar"
                    dimensiones_str = "1×1"
                    workspace_info[nombre] = {
                        'tipo': 'escalar', 'dimensiones': (1, 1)}

                elif filas_sheets == 1 and cols_sheets > 1:
                    # DATOS EN UNA FILA HORIZONTAL → Vector fila
                    tipo = "📈 Vector fila"
                    dimensiones_str = f"1×{cols_sheets}"
                    workspace_info[nombre] = {
                        'tipo': 'vector_fila', 'dimensiones': (1, cols_sheets)}

                elif filas_sheets > 1 and cols_sheets == 1:
                    # DATOS EN UNA COLUMNA VERTICAL → Vector columna
                    tipo = "📉 Vector columna"
                    dimensiones_str = f"{filas_sheets}×1"
                    workspace_info[nombre] = {
                        'tipo': 'vector_columna', 'dimensiones': (filas_sheets, 1)}

                else:
                    # MATRIZ (múltiples filas Y columnas)
                    tipo = "📋 Matriz"
                    dimensiones_str = f"{filas_sheets}×{cols_sheets}"
                    workspace_info[nombre] = {
                        'tipo': 'matriz', 'dimensiones': (filas_sheets, cols_sheets)}

                print(f"{i:<3} {nombre:<20} {dimensiones_str:<12} {tipo:<15}")

            except Exception:
                print(f"{i:<3} {nombre:<20} {'ERROR':<12} {'❌ Error':<15}")
                workspace_info[nombre] = {'tipo': 'error', 'dimensiones': None}

        print("=" * 75)
        print("💡 Usa importar('nombre') para traer matrices específicas")

        return workspace_info

    except Exception as e:
        print(f"❌ Error: No se pudo abrir '{nombre_sheet}'")
        print("💡 Verifica que el Google Sheet existe y tienes acceso")
        return {}


def importar(*nombres_matrices, sheet_name=None):
    """
    📥 Importa matrices desde Google Sheets a variables globales.
    ACTUALIZADO: Preserva formato de vectores fila/columna

    Ejemplos:
        importar()           # Importa TODAS las matrices
        importar('A')        # Importa solo A
        importar('A', 'B')   # Importa A y B

    Args:
        *nombres_matrices: Nombres de matrices a importar
        sheet_name (str, optional): Nombre del sheet

    Returns:
        dict: Diccionario con las variables importadas
    """
    if not _verificar_configuracion():
        return {}

    nombre_sheet = sheet_name or spreadsheet_name

    try:
        spreadsheet = gc.open(nombre_sheet)
    except Exception as e:
        print(f"❌ No se pudo abrir '{nombre_sheet}'")
        print("💡 Verifica que el archivo existe y tienes permisos")
        return {}

    if not nombres_matrices:
        print("🔄 Importando TODAS las matrices...")
        return _cargar_todas_matrices(spreadsheet)

    print(f"🔄 Importando: {', '.join(nombres_matrices)}")
    print("=" * 50)

    datos_cargados = {}
    pestanas_disponibles = {ws.title: ws for ws in spreadsheet.worksheets()}

    for nombre_solicitado in nombres_matrices:
        pestaña_encontrada = None

        # Búsqueda exacta
        if nombre_solicitado in pestanas_disponibles:
            pestaña_encontrada = pestanas_disponibles[nombre_solicitado]
        else:
            # Búsqueda case-insensitive
            for nombre_pestaña, worksheet in pestanas_disponibles.items():
                if nombre_pestaña.lower() == nombre_solicitado.lower():
                    pestaña_encontrada = worksheet
                    break

        if pestaña_encontrada:
            try:
                data = pestaña_encontrada.get_all_values()

                if not data:
                    print(f"⚠️  '{nombre_solicitado}' está vacía")
                    continue

                # Procesar datos PRESERVANDO formato original
                try:
                    array_np = np.array(data).astype(float)
                except ValueError:
                    array_np = _procesar_datos_mixtos(data)

                # DETERMINAR TIPO Y VALOR PRESERVANDO FORMATO
                if array_np.size == 1:
                    valor = array_np.item()
                    tipo = "escalar"
                elif array_np.shape[0] == 1 and array_np.shape[1] > 1:
                    # VECTOR FILA: mantener como (1, n)
                    valor = array_np  # NO usar flatten()
                    tipo = "vector fila"
                elif array_np.shape[0] > 1 and array_np.shape[1] == 1:
                    # VECTOR COLUMNA: mantener como (n, 1)
                    valor = array_np  # NO usar flatten()
                    tipo = "vector columna"
                elif array_np.ndim == 1 or (array_np.ndim == 2 and min(array_np.shape) == 1):
                    # CASO AMBIGUO: convertir a vector columna por defecto
                    if array_np.ndim == 1:
                        # Convertir a columna (n, 1)
                        valor = array_np.reshape(-1, 1)
                    else:
                        valor = array_np
                    tipo = "vector"
                else:
                    # MATRIZ
                    valor = array_np
                    tipo = "matriz"

                nombre_variable = _limpiar_nombre_variable(nombre_solicitado)
                datos_cargados[nombre_variable] = valor

                print(f"✅ {nombre_solicitado} → {tipo} {valor.shape}")

            except Exception as e:
                print(f"❌ Error: {nombre_solicitado} - {e}")
        else:
            print(f"❌ No encontré '{nombre_solicitado}'")
            print(f"💡 Disponibles: {', '.join(pestanas_disponibles.keys())}")

    if datos_cargados:
        # Crear variables en el frame del llamador (notebook del usuario)
        frame = inspect.currentframe().f_back
        if frame:
            frame.f_globals.update(datos_cargados)

        print(
            f"\n🎯 ¡Listo! Variables disponibles: {', '.join(datos_cargados.keys())}")

    print("=" * 50)
    return datos_cargados


def _cargar_todas_matrices(spreadsheet):
    """Carga todas las matrices del spreadsheet. ACTUALIZADO: Preserva formato de vectores"""
    datos_cargados = {}

    print("=" * 50)
    for worksheet in spreadsheet.worksheets():
        nombre_hoja = worksheet.title
        nombre_variable = _limpiar_nombre_variable(nombre_hoja)

        try:
            data = worksheet.get_all_values()
            if not data:
                continue

            try:
                array_np = np.array(data).astype(float)
            except ValueError:
                array_np = _procesar_datos_mixtos(data)

            # PRESERVAR FORMATO ORIGINAL
            if array_np.size == 1:
                valor = array_np.item()
                tipo = "escalar"
            elif array_np.shape[0] == 1 and array_np.shape[1] > 1:
                # VECTOR FILA: mantener como (1, n)
                valor = array_np
                tipo = "vector fila"
            elif array_np.shape[0] > 1 and array_np.shape[1] == 1:
                # VECTOR COLUMNA: mantener como (n, 1)
                valor = array_np
                tipo = "vector columna"
            elif array_np.ndim == 1 or (array_np.ndim == 2 and min(array_np.shape) == 1):
                # CASO AMBIGUO: convertir a vector columna por defecto
                if array_np.ndim == 1:
                    valor = array_np.reshape(-1, 1)
                else:
                    valor = array_np
                tipo = "vector"
            else:
                # MATRIZ
                valor = array_np
                tipo = "matriz"

            datos_cargados[nombre_variable] = valor
            print(f"✅ {nombre_hoja} → {tipo} {valor.shape}")

        except Exception as e:
            print(f"❌ Error en {nombre_hoja}: {e}")

    if datos_cargados:
        # Crear variables en el frame del llamador
        frame = inspect.currentframe().f_back.f_back  # Dos niveles arriba
        if frame:
            frame.f_globals.update(datos_cargados)

        print(f"\n🎯 Variables creadas: {', '.join(datos_cargados.keys())}")

    print("=" * 50)


def exportar(*nombres_variables, sheet_name=None, sobrescribir=True):
    """
    📤 Exporta variables a Google Sheets.

    Ejemplos:
        exportar()              # Exporta TODAS las variables numpy
        exportar('C')           # Exporta solo C
        exportar('C', 'Ainv')   # Exporta C y Ainv

    Args:
        *nombres_variables: Nombres de variables a exportar
        sheet_name (str, optional): Nombre del sheet
        sobrescribir (bool): Si sobrescribir pestañas existentes

    Returns:
        list: Lista de variables exportadas exitosamente
    """
    if not _verificar_configuracion():
        return []

    nombre_sheet = sheet_name or spreadsheet_name

    try:
        spreadsheet = gc.open(nombre_sheet)
    except Exception as e:
        print(f"❌ No se pudo abrir '{nombre_sheet}'")
        return []

    # Obtener variables del frame del llamador
    frame = inspect.currentframe().f_back
    todas_variables = frame.f_globals if frame else {}

    # Detectar variables exportables
    variables_disponibles = {}
    for nombre, valor in todas_variables.items():
        if (isinstance(valor, (np.ndarray, np.number, int, float)) and
            not nombre.startswith('_') and
                nombre not in ['np', 'numpy', 'gspread', 'gc', 'creds', 'spreadsheet']):
            variables_disponibles[nombre] = valor

    if not nombres_variables:
        variables_a_exportar = variables_disponibles
        print("📤 Exportando TODAS las variables numpy...")
    else:
        variables_a_exportar = {}
        variables_no_encontradas = []

        for nombre in nombres_variables:
            if nombre in variables_disponibles:
                variables_a_exportar[nombre] = variables_disponibles[nombre]
            else:
                variables_no_encontradas.append(nombre)

        if variables_no_encontradas:
            print(
                f"⚠️  Variables no encontradas: {', '.join(variables_no_encontradas)}")
            print(
                f"💡 Variables disponibles: {list(variables_disponibles.keys())}")

        if not variables_a_exportar:
            print("❌ No hay variables válidas para exportar")
            return []

    print("=" * 50)
    pestanas_existentes = {ws.title: ws for ws in spreadsheet.worksheets()}
    exportadas = []

    for nombre_var, valor in variables_a_exportar.items():
        try:
            # Preparar datos para Google Sheets
            datos = _preparar_datos_para_sheets(valor)
            if datos is None:
                print(f"⚠️  {nombre_var}: Tipo no soportado")
                continue

            # Crear o actualizar pestaña
            if nombre_var in pestanas_existentes:
                if sobrescribir:
                    worksheet = pestanas_existentes[nombre_var]
                    worksheet.clear()
                    accion = "actualizada"
                else:
                    print(f"⚠️  {nombre_var}: Ya existe (sobrescribir=False)")
                    continue
            else:
                worksheet = spreadsheet.add_worksheet(
                    title=nombre_var, rows=50, cols=20)
                accion = "creada"

            # Escribir datos
            if datos:
                worksheet.update('A1', datos)

            exportadas.append(nombre_var)
            print(f"✅ {nombre_var} → {accion}")

        except Exception as e:
            print(f"❌ Error exportando {nombre_var}: {e}")

    print("=" * 50)
    if exportadas:
        print(f"🎯 ¡Exportadas exitosamente!: {', '.join(exportadas)}")
    print(f"🔗 Revisa tu Google Sheet: '{nombre_sheet}'")

    return exportadas


def _preparar_datos_para_sheets(valor):
    """
    Convierte una variable en formato adecuado para Google Sheets.
    ACTUALIZADO: Preserva formato de vectores fila/columna
    """
    if isinstance(valor, (int, float, np.number)):
        return [[float(valor)]]
    elif isinstance(valor, np.ndarray):
        if valor.ndim == 0:
            # Escalar en array
            return [[float(valor.item())]]
        elif valor.ndim == 1:
            # Vector 1D: convertir a columna por defecto
            return [[float(x)] for x in valor]
        elif valor.ndim == 2:
            if valor.shape[0] == 1:
                # VECTOR FILA (1, n): exportar horizontalmente
                return [valor[0].tolist()]
            elif valor.shape[1] == 1:
                # VECTOR COLUMNA (n, 1): exportar verticalmente
                return [[float(valor[i, 0])] for i in range(valor.shape[0])]
            else:
                # MATRIZ: exportar normalmente
                return [[float(x) for x in fila] for fila in valor]
    return None


def listar_variables_exportables():
    """
    🔍 Lista todas las variables que se pueden exportar.
    ACTUALIZADO: Muestra formato correcto de vectores

    Returns:
        dict: Variables exportables
    """
    frame = inspect.currentframe().f_back
    todas_variables = frame.f_globals if frame else {}

    print("🔍 VARIABLES EXPORTABLES:")
    print("=" * 50)

    variables_numpy = {}
    for nombre, valor in todas_variables.items():
        if (isinstance(valor, (np.ndarray, np.number, int, float)) and
            not nombre.startswith('_') and
                nombre not in ['np', 'numpy', 'gspread', 'gc', 'creds', 'spreadsheet']):
            variables_numpy[nombre] = valor

    if variables_numpy:
        print(f"{'NOMBRE':<15} {'DIMENSIONES':<12} {'TIPO':<15}")
        print("-" * 50)

        for nombre, valor in variables_numpy.items():
            if isinstance(valor, np.ndarray):
                if valor.ndim == 0:
                    tipo = "📊 Escalar"
                    dimensiones = "1×1"
                elif valor.ndim == 1:
                    tipo = "📉 Vector columna"  # 1D se trata como columna
                    dimensiones = f"{len(valor)}×1"
                elif valor.ndim == 2:
                    if valor.shape[0] == 1:
                        tipo = "📈 Vector fila"
                        dimensiones = f"1×{valor.shape[1]}"
                    elif valor.shape[1] == 1:
                        tipo = "📉 Vector columna"
                        dimensiones = f"{valor.shape[0]}×1"
                    else:
                        tipo = "📋 Matriz"
                        dimensiones = f"{valor.shape[0]}×{valor.shape[1]}"
                else:
                    tipo = "❓ Array ND"
                    dimensiones = str(valor.shape)
            else:
                tipo = "📊 Escalar"
                dimensiones = "1×1"

            print(f"{nombre:<15} {dimensiones:<12} {tipo:<15}")

        print("=" * 50)
        print(f"📊 Total: {len(variables_numpy)} variables exportables")
        print(
            f"💡 Uso: exportar() para todas, o exportar('{list(variables_numpy.keys())[0]}') para específicas")
    else:
        print("⚠️  No hay variables numpy disponibles para exportar")
        print("💡 Crea algunas variables primero:")
        print("   A = np.array([[1, 2], [3, 4]])")
        print("   C = A @ B")

    return variables_numpy


def ayuda():
    """
    📖 Muestra la ayuda completa del sistema.
    """
    print("📚 ALGEBRA LINEAL - GUÍA COMPLETA")
    print("=" * 60)
    print("📦 Instalación:")
    print("   pip install algebra-lineal-sheets")
    print()
    print("🔧 CONFIGURACIÓN:")
    print("   configurar()                 # Configurar una vez al inicio")
    print("   cambiar_sheet('mi_sheet')    # Cambiar archivo de trabajo")
    print()
    print("🏢 VER CONTENIDO:")
    print("   workspace()                  # Ver matrices en Google Sheets")
    print()
    print("📥 IMPORTAR:")
    print("   importar()                   # Importar todas las matrices")
    print("   importar('A')                # Importar solo A")
    print("   importar('A', 'B', 'v')      # Importar A, B y v")
    print()
    print("🧮 OPERACIONES (después de importar):")
    print("   C = A @ B                    # Multiplicación matricial")
    print("   suma = A + B                 # Suma")
    print("   Ainv = np.linalg.inv(A)      # Matriz inversa")
    print("   det_A = np.linalg.det(A)     # Determinante")
    print("   norma = np.linalg.norm(v)    # Norma de vector")
    print()
    print("📤 EXPORTAR:")
    print("   exportar()                   # Exportar todas las variables")
    print("   exportar('C')                # Exportar solo C")
    print("   exportar('C', 'Ainv')        # Exportar C y Ainv")
    print()
    print("🔍 UTILIDADES:")
    print("   listar_variables_exportables() # Ver qué se puede exportar")
    print("   version()                    # Información del paquete")
    print("   ayuda()                      # Esta ayuda")
    print("=" * 60)


def version():
    """Muestra información del paquete."""
    from . import __version__, __author__, __description__, __url__
    print(f"📦 ALGEBRA LINEAL v{__version__}")
    print(f"👨‍🏫 Autor: {__author__}")
    print(f"📚 {__description__}")
    print(f"🔗 PyPI: {__url__}")
    print(f"🛠️  Instalación: pip install algebra-lineal-sheets")
