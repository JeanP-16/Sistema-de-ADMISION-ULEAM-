"""
Servicio de Registros - Sistema de Admisión ULEAM
Maneja la lógica de negocio para registros nacionales
"""

from datetime import datetime


class RegistroService:
    """
    Servicio que maneja la lógica de negocio de registros
    Actúa como capa intermedia entre rutas y base de datos
    """
    
    def __init__(self, db_manager):
        """
        Inicializa el servicio
        
        Args:
            db_manager: Instancia de ExcelManager
        """
        self.db = db_manager
    
    def obtener_nombre_completo(self, registro):
        """
        Formatea el nombre completo de un registro
        
        Args:
            registro: Diccionario con datos del registro
            
        Returns:
            str: Nombre completo formateado
        """
        partes = [
            registro.get('primer_nombre', ''),
            registro.get('segundo_nombre', ''),
            registro.get('apellido_paterno', ''),
            registro.get('apellido_materno', '')
        ]
        
        return ' '.join([p for p in partes if p]).strip()
    
    def verificar_registro_completo(self, cedula):
        """
        Verifica si un registro está completo
        
        Args:
            cedula: Cédula del registro
            
        Returns:
            tuple: (bool completo, list campos_faltantes)
        """
        registro = self.db.obtener_registro_por_cedula(cedula)
        
        if not registro:
            return False, ["Registro no existe"]
        
        campos_requeridos = {
            'primer_nombre': 'Primer nombre',
            'apellido_paterno': 'Apellido paterno',
            'apellido_materno': 'Apellido materno',
            'correo': 'Correo electrónico',
            'celular': 'Número de celular',
            'calificacion': 'Calificación'
        }
        
        campos_faltantes = []
        
        for campo, descripcion in campos_requeridos.items():
            valor = registro.get(campo)
            if not valor or (isinstance(valor, str) and not valor.strip()):
                campos_faltantes.append(descripcion)
        
        return len(campos_faltantes) == 0, campos_faltantes
    
    def crear_registro_nuevo(self, datos):
        """
        Crea un nuevo registro con validaciones adicionales
        
        Args:
            datos: Diccionario con datos del registro
            
        Returns:
            tuple: (bool exito, str mensaje, dict registro)
        """
        # Verificar que no exista
        if self.db.existe_registro(datos.get('cedula')):
            return False, "Ya existe un registro con esta cédula", None
        
        # Formatear datos antes de insertar
        datos_formateados = self._formatear_datos_registro(datos)
        
        # Insertar en base de datos
        exito, mensaje = self.db.insertar_registro(datos_formateados)
        
        if exito:
            # Obtener el registro recién creado
            registro = self.db.obtener_registro_por_cedula(datos['cedula'])
            return True, mensaje, registro
        else:
            return False, mensaje, None
    
    def actualizar_registro_existente(self, cedula, datos):
        """
        Actualiza un registro existente con validaciones
        
        Args:
            cedula: Cédula del registro a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            tuple: (bool exito, str mensaje, dict registro)
        """
        # Verificar que existe
        if not self.db.existe_registro(cedula):
            return False, "Registro no encontrado", None
        
        # Formatear datos
        datos_formateados = self._formatear_datos_registro(datos)
        
        # Actualizar
        exito, mensaje = self.db.actualizar_registro(cedula, datos_formateados)
        
        if exito:
            # Obtener el registro actualizado
            registro = self.db.obtener_registro_por_cedula(cedula)
            return True, mensaje, registro
        else:
            return False, mensaje, None
    
    def eliminar_registro_completo(self, cedula):
        """
        Elimina un registro y todas sus dependencias
        
        Args:
            cedula: Cédula del registro a eliminar
            
        Returns:
            tuple: (bool exito, str mensaje, dict info_eliminado)
        """
        # Obtener información antes de eliminar
        registro = self.db.obtener_registro_por_cedula(cedula)
        
        if not registro:
            return False, "Registro no encontrado", None
        
        # Contar dependencias
        info_eliminado = {
            'registro': registro,
            'nombre_completo': self.obtener_nombre_completo(registro),
            'inscripciones': 1 if self.db.obtener_inscripcion_por_cedula(cedula) else 0,
            'evaluaciones': 1 if self.db.obtener_evaluacion_por_cedula(cedula) else 0,
            'asignaciones': 1 if self.db.obtener_asignacion_por_cedula(cedula) else 0,
            'puntajes': 1 if self.db.obtener_puntaje_por_cedula(cedula) else 0
        }
        
        # Eliminar
        exito, mensaje = self.db.eliminar_registro(cedula)
        
        if exito:
            return True, mensaje, info_eliminado
        else:
            return False, mensaje, None
    
    def buscar_registros(self, criterios):
        """
        Busca registros según criterios
        
        Args:
            criterios: Diccionario con criterios de búsqueda
            
        Returns:
            list: Lista de registros que cumplen criterios
        """
        todos_registros = self.db.listar_todos_registros()
        
        if not criterios:
            return todos_registros
        
        resultados = []
        
        for registro in todos_registros:
            cumple = True
            
            # Filtrar por estado
            if 'estado' in criterios and criterios['estado']:
                if registro['estado'] != criterios['estado']:
                    cumple = False
            
            # Filtrar por cuadro de honor
            if 'cuadro_honor' in criterios and criterios['cuadro_honor']:
                if registro['cuadro_honor'] != criterios['cuadro_honor']:
                    cumple = False
            
            # Filtrar por rango de calificación
            if 'calificacion_min' in criterios:
                if registro['calificacion'] < float(criterios['calificacion_min']):
                    cumple = False
            
            if 'calificacion_max' in criterios:
                if registro['calificacion'] > float(criterios['calificacion_max']):
                    cumple = False
            
            # Filtrar por texto en nombre
            if 'nombre' in criterios and criterios['nombre']:
                nombre_completo = self.obtener_nombre_completo(registro).lower()
                if criterios['nombre'].lower() not in nombre_completo:
                    cumple = False
            
            if cumple:
                resultados.append(registro)
        
        return resultados
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de los registros
        
        Returns:
            dict: Diccionario con estadísticas
        """
        registros = self.db.listar_todos_registros()
        
        if not registros:
            return {
                'total': 0,
                'completos': 0,
                'pendientes': 0,
                'con_cuadro_honor': 0,
                'calificacion_promedio': 0
            }
        
        completos = sum(1 for r in registros if r['estado'] == 'COMPLETO')
        pendientes = sum(1 for r in registros if r['estado'] == 'PENDIENTE')
        con_cuadro = sum(1 for r in registros if r['cuadro_honor'] == 'SI')
        
        calificaciones = [r['calificacion'] for r in registros if r['calificacion'] > 0]
        promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0
        
        return {
            'total': len(registros),
            'completos': completos,
            'pendientes': pendientes,
            'con_cuadro_honor': con_cuadro,
            'calificacion_promedio': round(promedio, 2)
        }
    
    def _formatear_datos_registro(self, datos):
        """
        Formatea datos de registro antes de guardar
        
        Args:
            datos: Diccionario con datos crudos
            
        Returns:
            dict: Datos formateados
        """
        datos_formateados = {}
        
        # Copiar cédula sin cambios
        if 'cedula' in datos:
            datos_formateados['cedula'] = str(datos['cedula']).strip()
        
        # Formatear nombres a mayúsculas
        campos_nombre = ['primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno']
        for campo in campos_nombre:
            if campo in datos:
                valor = datos[campo]
                if valor:
                    datos_formateados[campo] = ' '.join(str(valor).upper().strip().split())
                else:
                    datos_formateados[campo] = ''
        
        # Formatear email a minúsculas
        if 'correo' in datos:
            datos_formateados['correo'] = str(datos['correo']).lower().strip()
        
        # Formatear celular
        if 'celular' in datos:
            datos_formateados['celular'] = str(datos['celular']).strip()
        
        # Convertir calificación a float
        if 'calificacion' in datos:
            try:
                datos_formateados['calificacion'] = float(datos['calificacion'])
            except:
                datos_formateados['calificacion'] = 0.0
        
        # Formatear cuadro de honor a mayúsculas
        if 'cuadro_honor' in datos:
            datos_formateados['cuadro_honor'] = str(datos['cuadro_honor']).upper().strip()
        
        # Formatear estado a mayúsculas
        if 'estado' in datos:
            datos_formateados['estado'] = str(datos['estado']).upper().strip()
        
        return datos_formateados
    
    def validar_edad(self, fecha_nacimiento):
        """
        Valida que el estudiante tenga edad mínima
        
        Args:
            fecha_nacimiento: Fecha de nacimiento (datetime o str)
            
        Returns:
            tuple: (bool valido, int edad)
        """
        if isinstance(fecha_nacimiento, str):
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            except:
                return False, 0
        
        hoy = datetime.now()
        edad = hoy.year - fecha_nacimiento.year
        
        # Ajustar si no ha cumplido años este año
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
        
        # Edad mínima: 17 años
        return edad >= 17, edad
