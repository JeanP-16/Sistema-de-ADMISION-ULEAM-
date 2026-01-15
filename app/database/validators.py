"""
Validadores de Datos - Sistema de Admisión ULEAM
Valida cédulas, emails, calificaciones y otros datos
"""

import re


class Validator:
    """Clase base para validadores"""
    
    def validar(self, valor):
        """
        Valida un valor
        
        Args:
            valor: Valor a validar
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        raise NotImplementedError("Subclases deben implementar validar()")


class CedulaValidator(Validator):
    """Validador de cédulas ecuatorianas"""
    
    def validar(self, cedula):
        """
        Valida formato de cédula ecuatoriana
        
        Args:
            cedula: Número de cédula
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not cedula:
            return False, "Cédula es requerida"
        
        cedula_str = str(cedula).strip()
        
        # Validar longitud
        if len(cedula_str) != 10:
            return False, "Cédula debe tener exactamente 10 dígitos"
        
        # Validar que solo contenga números
        if not cedula_str.isdigit():
            return False, "Cédula debe contener solo números"
        
        # Validar que los dos primeros dígitos sean válidos (01-24)
        provincia = int(cedula_str[:2])
        if provincia < 1 or provincia > 24:
            return False, "Código de provincia inválido"
        
        return True, "Cédula válida"
    
    def validar_completo(self, cedula):
        """
        Validación completa con algoritmo de dígito verificador
        (Implementación opcional más robusta)
        """
        # Validación básica primero
        es_valida, mensaje = self.validar(cedula)
        if not es_valida:
            return False, mensaje
        
        cedula_str = str(cedula).strip()
        
        # Algoritmo de verificación del dígito verificador
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        
        for i in range(9):
            valor = int(cedula_str[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        
        residuo = suma % 10
        digito_verificador = 0 if residuo == 0 else 10 - residuo
        
        if digito_verificador != int(cedula_str[9]):
            return False, "Dígito verificador inválido"
        
        return True, "Cédula válida"


class EmailValidator(Validator):
    """Validador de emails"""
    
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validar(self, email):
        """
        Valida formato de email
        
        Args:
            email: Dirección de email
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not email:
            return False, "Email es requerido"
        
        email_str = str(email).strip()
        
        if not re.match(self.EMAIL_REGEX, email_str):
            return False, "Formato de email inválido"
        
        # Validar longitud
        if len(email_str) > 100:
            return False, "Email demasiado largo (máximo 100 caracteres)"
        
        # Validar dominios comunes educativos
        dominios_educativos = ['uleam.edu.ec', 'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com']
        dominio = email_str.split('@')[1].lower()
        
        # Solo advertencia, no error
        if dominio not in dominios_educativos:
            # Aceptar pero podría ser sospechoso
            pass
        
        return True, "Email válido"


class CalificacionValidator(Validator):
    """Validador de calificaciones (0-10)"""
    
    def validar(self, calificacion):
        """
        Valida calificación en rango 0-10
        
        Args:
            calificacion: Valor de calificación
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if calificacion is None:
            return False, "Calificación es requerida"
        
        try:
            calif_float = float(calificacion)
        except (ValueError, TypeError):
            return False, "Calificación debe ser un número"
        
        if calif_float < 0:
            return False, "Calificación no puede ser negativa"
        
        if calif_float > 10:
            return False, "Calificación no puede ser mayor a 10"
        
        return True, "Calificación válida"


class CelularValidator(Validator):
    """Validador de números de celular ecuatorianos"""
    
    def validar(self, celular):
        """
        Valida formato de celular ecuatoriano
        
        Args:
            celular: Número de celular
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not celular:
            return False, "Número de celular es requerido"
        
        celular_str = str(celular).strip()
        
        # Eliminar espacios y guiones
        celular_limpio = celular_str.replace(' ', '').replace('-', '')
        
        # Validar longitud (10 dígitos)
        if len(celular_limpio) != 10:
            return False, "Celular debe tener 10 dígitos"
        
        # Validar que solo contenga números
        if not celular_limpio.isdigit():
            return False, "Celular debe contener solo números"
        
        # Validar que empiece con 09
        if not celular_limpio.startswith('09'):
            return False, "Celular debe empezar con 09"
        
        return True, "Celular válido"


class EstadoValidator(Validator):
    """Validador de estados predefinidos"""
    
    ESTADOS_VALIDOS = {
        'registro': ['COMPLETO', 'PENDIENTE', 'INCOMPLETO'],
        'inscripcion': ['CONFIRMADA', 'PENDIENTE', 'CANCELADA'],
        'evaluacion': ['EVALUADO', 'PENDIENTE', 'NO_PRESENTADO'],
        'asignacion': ['ASIGNADO', 'PENDIENTE', 'RECHAZADO'],
        'puntaje': ['APROBADO', 'NO_APROBADO', 'PENDIENTE']
    }
    
    def __init__(self, tipo_estado='registro'):
        """
        Inicializa validador de estado
        
        Args:
            tipo_estado: Tipo de estado a validar
        """
        self.tipo_estado = tipo_estado
        self.estados_permitidos = self.ESTADOS_VALIDOS.get(tipo_estado, [])
    
    def validar(self, estado):
        """
        Valida que el estado sea uno de los permitidos
        
        Args:
            estado: Estado a validar
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not estado:
            return False, "Estado es requerido"
        
        estado_str = str(estado).upper().strip()
        
        if estado_str not in self.estados_permitidos:
            estados_texto = ', '.join(self.estados_permitidos)
            return False, f"Estado inválido. Debe ser uno de: {estados_texto}"
        
        return True, "Estado válido"


class CuadroHonorValidator(Validator):
    """Validador de cuadro de honor (SI/NO)"""
    
    VALORES_VALIDOS = ['SI', 'NO']
    
    def validar(self, valor):
        """
        Valida valor de cuadro de honor
        
        Args:
            valor: Valor a validar
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not valor:
            return True, "Valor por defecto: NO"  # Permitir vacío, usar default
        
        valor_str = str(valor).upper().strip()
        
        if valor_str not in self.VALORES_VALIDOS:
            return False, "Cuadro de honor debe ser 'SI' o 'NO'"
        
        return True, "Valor válido"


class CarreraValidator(Validator):
    """Validador de IDs de carreras"""
    
    CARRERAS_VALIDAS = {
        101: 'Tecnologías de Información',
        102: 'Medicina',
        103: 'Ingeniería Civil',
        104: 'Administración',
        105: 'Derecho'
    }
    
    def validar(self, carrera_id):
        """
        Valida ID de carrera
        
        Args:
            carrera_id: ID de la carrera
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not carrera_id:
            return False, "ID de carrera es requerido"
        
        try:
            carrera_int = int(carrera_id)
        except (ValueError, TypeError):
            return False, "ID de carrera debe ser un número"
        
        if carrera_int not in self.CARRERAS_VALIDAS:
            carreras_texto = ', '.join([f"{k}: {v}" for k, v in self.CARRERAS_VALIDAS.items()])
            return False, f"Carrera inválida. Carreras disponibles: {carreras_texto}"
        
        return True, f"Carrera válida: {self.CARRERAS_VALIDAS[carrera_int]}"
    
    def obtener_nombre(self, carrera_id):
        """Obtiene el nombre de una carrera por ID"""
        return self.CARRERAS_VALIDAS.get(int(carrera_id), "Carrera desconocida")


class JornadaValidator(Validator):
    """Validador de jornadas"""
    
    JORNADAS_VALIDAS = ['MATUTINA', 'VESPERTINA', 'NOCTURNA']
    
    def validar(self, jornada):
        """
        Valida jornada
        
        Args:
            jornada: Jornada a validar
            
        Returns:
            tuple: (bool es_valido, str mensaje)
        """
        if not jornada:
            return False, "Jornada es requerida"
        
        jornada_str = str(jornada).upper().strip()
        
        if jornada_str not in self.JORNADAS_VALIDAS:
            jornadas_texto = ', '.join(self.JORNADAS_VALIDAS)
            return False, f"Jornada inválida. Debe ser: {jornadas_texto}"
        
        return True, "Jornada válida"


class ValidadorCompleto:
    """
    Validador completo que agrupa todos los validadores
    Facilita la validación de formularios completos
    """
    
    def __init__(self):
        self.cedula = CedulaValidator()
        self.email = EmailValidator()
        self.calificacion = CalificacionValidator()
        self.celular = CelularValidator()
        self.cuadro_honor = CuadroHonorValidator()
        self.carrera = CarreraValidator()
        self.jornada = JornadaValidator()
        self.estado_registro = EstadoValidator('registro')
        self.estado_inscripcion = EstadoValidator('inscripcion')
        self.estado_evaluacion = EstadoValidator('evaluacion')
    
    def validar_registro_completo(self, datos):
        """
        Valida todos los campos de un registro
        
        Args:
            datos: Diccionario con datos del registro
            
        Returns:
            tuple: (bool es_valido, list errores)
        """
        errores = []
        
        # Validar cédula
        es_valida, msg = self.cedula.validar(datos.get('cedula'))
        if not es_valida:
            errores.append(f"Cédula: {msg}")
        
        # Validar email
        es_valido, msg = self.email.validar(datos.get('correo'))
        if not es_valido:
            errores.append(f"Email: {msg}")
        
        # Validar calificación
        es_valida, msg = self.calificacion.validar(datos.get('calificacion'))
        if not es_valida:
            errores.append(f"Calificación: {msg}")
        
        # Validar celular
        es_valido, msg = self.celular.validar(datos.get('celular'))
        if not es_valido:
            errores.append(f"Celular: {msg}")
        
        # Validar cuadro de honor
        es_valido, msg = self.cuadro_honor.validar(datos.get('cuadro_honor'))
        if not es_valido:
            errores.append(f"Cuadro de honor: {msg}")
        
        # Validar estado
        es_valido, msg = self.estado_registro.validar(datos.get('estado'))
        if not es_valido:
            errores.append(f"Estado: {msg}")
        
        # Validar campos de texto requeridos
        if not datos.get('primer_nombre'):
            errores.append("Primer nombre es requerido")
        
        if not datos.get('apellido_paterno'):
            errores.append("Apellido paterno es requerido")
        
        if not datos.get('apellido_materno'):
            errores.append("Apellido materno es requerido")
        
        return len(errores) == 0, errores


# Instancia global para uso fácil
validador = ValidadorCompleto()
