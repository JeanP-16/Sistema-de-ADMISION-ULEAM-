"""
Servicio de Autenticación y Autorización - Sistema de Admisión ULEAM
Maneja login, logout y permisos de usuarios
"""

from functools import wraps
from flask import session, redirect, url_for, flash


class AuthService:
    """
    Servicio de autenticación y control de acceso
    """
    
    ROLES = {
        'ADMIN': {
            'nombre': 'Administrador',
            'permisos': ['crear', 'leer', 'actualizar', 'eliminar', 'gestionar_todo']
        },
        'ESTUDIANTE': {
            'nombre': 'Estudiante',
            'permisos': ['leer', 'inscribirse', 'consultar']
        }
    }
    
    def __init__(self, db_manager):
        """
        Inicializa el servicio
        
        Args:
            db_manager: Instancia de ExcelManager
        """
        self.db = db_manager
    
    def autenticar_usuario(self, cedula):
        """
        Autentica un usuario por su cédula
        
        Args:
            cedula: Número de cédula del usuario
            
        Returns:
            tuple: (bool autenticado, str rol, dict info_usuario)
        """
        if not cedula:
            return False, None, None
        
        # Verificar si es administrador
        if self.db.es_administrador(cedula):
            info_admin = self.db.obtener_info_administrador(cedula)
            if info_admin:
                return True, 'ADMIN', {
                    'cedula': cedula,
                    'nombre': info_admin['nombre_completo'],
                    'email': info_admin['email'],
                    'rol': 'ADMIN'
                }
        
        # Verificar si es estudiante
        if self.db.existe_registro(cedula):
            registro = self.db.obtener_registro_por_cedula(cedula)
            if registro:
                nombre_completo = self._obtener_nombre_completo(registro)
                return True, 'ESTUDIANTE', {
                    'cedula': cedula,
                    'nombre': nombre_completo,
                    'email': registro['correo'],
                    'rol': 'ESTUDIANTE'
                }
        
        return False, None, None
    
    def iniciar_sesion(self, cedula):
        """
        Inicia sesión de un usuario
        
        Args:
            cedula: Cédula del usuario
            
        Returns:
            tuple: (bool exito, str mensaje)
        """
        autenticado, rol, info = self.autenticar_usuario(cedula)
        
        if not autenticado:
            return False, "Cédula no encontrada en el sistema"
        
        # Guardar en sesión
        session['cedula'] = info['cedula']
        session['nombre'] = info['nombre']
        session['email'] = info['email']
        session['rol'] = info['rol']
        session['autenticado'] = True
        
        mensaje = f"Bienvenido/a {info['nombre']}"
        
        return True, mensaje
    
    def cerrar_sesion(self):
        """
        Cierra la sesión del usuario actual
        
        Returns:
            tuple: (bool exito, str mensaje)
        """
        if 'autenticado' in session:
            nombre = session.get('nombre', 'Usuario')
            session.clear()
            return True, f"Sesión cerrada exitosamente. Hasta pronto, {nombre}"
        else:
            return False, "No hay sesión activa"
    
    def obtener_usuario_actual(self):
        """
        Obtiene información del usuario en sesión
        
        Returns:
            dict: Información del usuario o None
        """
        if not session.get('autenticado'):
            return None
        
        return {
            'cedula': session.get('cedula'),
            'nombre': session.get('nombre'),
            'email': session.get('email'),
            'rol': session.get('rol')
        }
    
    def es_administrador(self):
        """
        Verifica si el usuario actual es administrador
        
        Returns:
            bool: True si es admin
        """
        return session.get('rol') == 'ADMIN'
    
    def es_estudiante(self):
        """
        Verifica si el usuario actual es estudiante
        
        Returns:
            bool: True si es estudiante
        """
        return session.get('rol') == 'ESTUDIANTE'
    
    def tiene_permiso(self, permiso):
        """
        Verifica si el usuario tiene un permiso específico
        
        Args:
            permiso: Nombre del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso
        """
        rol = session.get('rol')
        
        if not rol:
            return False
        
        permisos = self.ROLES.get(rol, {}).get('permisos', [])
        
        return permiso in permisos
    
    def puede_modificar_registro(self, cedula_registro):
        """
        Verifica si el usuario puede modificar un registro
        
        Args:
            cedula_registro: Cédula del registro a modificar
            
        Returns:
            bool: True si puede modificar
        """
        # Admin puede modificar todo
        if self.es_administrador():
            return True
        
        # Estudiante puede modificar solo su registro (si implementamos esto)
        cedula_usuario = session.get('cedula')
        if self.es_estudiante() and cedula_usuario == cedula_registro:
            return True  # Por ahora False, pero se puede habilitar
        
        return False
    
    def requiere_autenticacion(self, f):
        """
        Decorador para rutas que requieren autenticación
        
        Args:
            f: Función de la ruta
            
        Returns:
            function: Función decorada
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('autenticado'):
                flash('Debe iniciar sesión para acceder', 'warning')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    def requiere_rol(self, rol_requerido):
        """
        Decorador para rutas que requieren un rol específico
        
        Args:
            rol_requerido: Rol necesario para acceder
            
        Returns:
            function: Decorador
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not session.get('autenticado'):
                    flash('Debe iniciar sesión', 'warning')
                    return redirect(url_for('index'))
                
                if session.get('rol') != rol_requerido:
                    flash('No tiene permisos para acceder a esta sección', 'error')
                    return redirect(url_for('dashboard'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def requiere_admin(self, f):
        """
        Decorador para rutas que requieren rol de administrador
        
        Args:
            f: Función de la ruta
            
        Returns:
            function: Función decorada
        """
        return self.requiere_rol('ADMIN')(f)
    
    def _obtener_nombre_completo(self, registro):
        """
        Formatea el nombre completo de un registro
        
        Args:
            registro: Diccionario con datos del registro
            
        Returns:
            str: Nombre completo
        """
        partes = [
            registro.get('primer_nombre', ''),
            registro.get('segundo_nombre', ''),
            registro.get('apellido_paterno', ''),
            registro.get('apellido_materno', '')
        ]
        
        return ' '.join([p for p in partes if p]).strip()
    
    def registrar_actividad(self, accion, detalles=None):
        """
        Registra actividad del usuario (para auditoría futura)
        
        Args:
            accion: Descripción de la acción
            detalles: Detalles adicionales
            
        Returns:
            bool: True si se registró
        """
        # Por ahora solo imprime, pero se puede guardar en log
        usuario = self.obtener_usuario_actual()
        
        if usuario:
            log_entry = f"[{usuario['rol']}] {usuario['nombre']} ({usuario['cedula']}): {accion}"
            if detalles:
                log_entry += f" - {detalles}"
            
            print(f"LOG: {log_entry}")
            return True
        
        return False
    
    def validar_sesion(self):
        """
        Valida que la sesión actual sea válida
        
        Returns:
            bool: True si la sesión es válida
        """
        if not session.get('autenticado'):
            return False
        
        # Verificar que el usuario aún existe
        cedula = session.get('cedula')
        rol = session.get('rol')
        
        if rol == 'ADMIN':
            return self.db.es_administrador(cedula)
        elif rol == 'ESTUDIANTE':
            return self.db.existe_registro(cedula)
        
        return False
