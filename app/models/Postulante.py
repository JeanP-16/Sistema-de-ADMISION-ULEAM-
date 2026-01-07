"""
Módulo: Postulante - CÓDIGO BUENO CON TODOS LOS PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Grabriel Cevallos
Fecha: Diciembre 2025
Descripción: Representa a un postulante en el sistema de admisión ULEAM

PRINCIPIOS SOLID APLICADOS:
✅ S (SRP): Responsabilidades separadas (Persona base, validaciones)
✅ O (OCP): Extensible mediante herencia y polimorfismo
✅ L (LSP): Sustituible por clase padre Persona
✅ I (ISP): Interfaces pequeñas y específicas
✅ D (DIP): Depende de abstracciones, usa inyección de dependencias
"""

from datetime import datetime
from typing import Optional, List
import re
from abc import ABC, abstractmethod


# ==================== PRINCIPIO D (DIP) ====================
# ABSTRACCIÓN: Repositorio para almacenamiento
class RepositorioPostulantesAbstracto(ABC):
    """Interfaz abstracta para repositorios de postulantes"""
    
    @abstractmethod
    def guardar(self, postulante: 'Postulante') -> None:
        pass
    
    @abstractmethod
    def buscar_por_id(self, id_postulante: int) -> Optional['Postulante']:
        pass
    
    @abstractmethod
    def contar_total(self) -> int:
        pass


# IMPLEMENTACIÓN CONCRETA
class RepositorioPostulantesEnMemoria(RepositorioPostulantesAbstracto):
    """Implementación concreta en memoria"""
    
    def __init__(self):
        self._postulantes = {}
    
    def guardar(self, postulante: 'Postulante') -> None:
        self._postulantes[postulante.id_postulante] = postulante
    
    def buscar_por_id(self, id_postulante: int) -> Optional['Postulante']:
        return self._postulantes.get(id_postulante)
    
    def contar_total(self) -> int:
        return len(self._postulantes)


# ==================== PRINCIPIO I (ISP) ====================
# INTERFAZ 1: Validación de identidad
class ValidadorIdentidad(ABC):
    """Interfaz específica para validación de identidad"""
    
    @abstractmethod
    def validarIdentidad(self) -> bool:
        pass


# INTERFAZ 2: Cálculo de edad
class CalculadorEdad(ABC):
    """Interfaz específica para cálculo de edad"""
    
    @abstractmethod
    def calcularEdad(self) -> int:
        pass


# ==================== PRINCIPIO S (SRP) ====================
# CLASE BASE: Solo datos personales básicos
class Persona(ValidadorIdentidad, CalculadorEdad):
    """
    Clase abstracta base para personas en el sistema
    APLICA SRP: Solo maneja datos básicos de identificación
    """
    
    def __init__(self, cedula: str, nombre_completo: str):
        self.cedula = cedula
        self.nombre_completo = nombre_completo
    
    @abstractmethod
    def validarIdentidad(self) -> bool:
        """Método abstracto que debe ser implementado"""
        pass
    
    @abstractmethod
    def calcularEdad(self) -> int:
        """Método abstracto para calcular edad"""
        pass


# ==================== PRINCIPIO O (OCP) + L (LSP) ====================
# CLASE PRINCIPAL: Extensible mediante herencia
class Postulante(Persona):
    """
    Representa a una persona que se postula al sistema de admisión.
    
    PRINCIPIOS SOLID APLICADOS:
    ✅ S (SRP): Hereda de Persona (responsabilidades separadas)
    ✅ O (OCP): Extensible - se pueden crear PostulanteMenor, PostulanteExtranjero, etc.
    ✅ L (LSP): Sustituye correctamente a Persona
    ✅ I (ISP): Implementa interfaces específicas (ValidadorIdentidad, CalculadorEdad)
    ✅ D (DIP): Usa RepositorioPostulantesAbstracto (inyección)
    """
    
    _contador_postulantes = 0
    _repositorio: RepositorioPostulantesAbstracto = RepositorioPostulantesEnMemoria()
    
    ESTADOS_VALIDOS = ['VERIFICADO', 'PENDIENTE', 'RECHAZADO']
    
    def __init__(self, cedula: str, nombre_completo: str, email: str, 
                 telefono: str, fecha_nacimiento: str):
        # Llamar al constructor de la clase padre (Persona)
        super().__init__(cedula, nombre_completo)
        
        Postulante._contador_postulantes += 1
        self.id_postulante = Postulante._contador_postulantes
        
        # Validar y asignar datos
        self.cedula = self._validar_cedula(cedula)
        self.email = self._validar_email(email)
        self.telefono = telefono.strip()
        self.fecha_nacimiento = fecha_nacimiento
        self.estado_registro = 'PENDIENTE'
        self.fecha_registro = datetime.now()
        
        # Relaciones con otras entidades
        self._inscripciones = []
        self._puntajes = []
        self._asignacion = None
        
        # ✅ PRINCIPIO D (DIP): Guardar usando repositorio abstracto
        Postulante._repositorio.guardar(self)
        
        print(f" ✓ Postulante creado: {self.nombre_completo} (ID: {self.id_postulante})")
    
    # ==================== VALIDACIONES (SRP) ====================
    
    def _validar_cedula(self, cedula: str) -> str:
        """Valida formato de cédula ecuatoriana"""
        cedula = cedula.strip()
        if not cedula.isdigit() or len(cedula) != 10:
            raise ValueError(f"Cédula inválida: debe tener 10 dígitos numéricos")
        
        # Verificar que los dos primeros dígitos sean válidos (01-24)
        provincia = int(cedula[:2])
        if provincia < 1 or provincia > 24:
            raise ValueError(f"Código de provincia inválido: {provincia}")
        
        return cedula
    
    def _validar_email(self, email: str) -> str:
        """Valida formato de email"""
        email = email.strip().lower()
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, email):
            raise ValueError(f"Email inválido: {email}")
        
        return email
    
    # ==================== POLIMORFISMO (LSP) ====================
    
    def validarIdentidad(self) -> bool:
        """
        PRINCIPIO L (LSP): Implementa el método abstracto de Persona
        Valida la identidad del postulante
        """
        es_valido = len(self.cedula) == 10 and self.cedula.isdigit()
        
        if es_valido:
            self.estado_registro = 'VERIFICADO'
            print(f" ✓ Identidad verificada: {self.nombre_completo}")
        else:
            self.estado_registro = 'RECHAZADO'
            print(f"Identidad rechazada: {self.nombre_completo}")
        
        return es_valido
    
    def calcularEdad(self) -> int:
        """
        PRINCIPIO L (LSP): Implementa el método abstracto de Persona
        Calcula la edad del postulante
        """
        fecha_nac = datetime.strptime(self.fecha_nacimiento, '%Y-%m-%d')
        hoy = datetime.now()
        edad = hoy.year - fecha_nac.year
        
        if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
            edad -= 1
        
        return edad
    
    # ==================== MÉTODOS DE GESTIÓN ====================
    
    def actualizarDatos(self, email: Optional[str] = None, 
                       telefono: Optional[str] = None) -> None:
        """Actualiza los datos de contacto del postulante"""
        if email:
            self.email = self._validar_email(email)
            print(f" ✓ Email actualizado: {self.email}")
        
        if telefono:
            self.telefono = telefono.strip()
            print(f" ✓ Teléfono actualizado: {self.telefono}")
    
    def obtenerInscripciones(self) -> List:
        """Obtiene todas las inscripciones del postulante"""
        return self._inscripciones.copy()
    
    def agregarInscripcion(self, inscripcion) -> None:
        """Agrega una inscripción al postulante"""
        self._inscripciones.append(inscripcion)
        print(f" ✓ Inscripción agregada para {self.nombre_completo}")
    
    def obtenerPuntajes(self) -> List:
        """Obtiene todos los puntajes del postulante"""
        return self._puntajes.copy()
    
    def tieneAsignacionActiva(self) -> bool:
        """Verifica si el postulante tiene una asignación activa"""
        return self._asignacion is not None
    
    # ==================== DECORADORES ====================
    
    @property
    def nombre_apellidos(self):
        """Property para obtener nombre completo"""
        return self.nombre_completo
    
    # ==================== MÉTODOS ESPECIALES ====================
    
    def __str__(self) -> str:
        return (f"Postulante(ID: {self.id_postulante}, "
                f"Nombre: {self.nombre_completo}, "
                f"Cedula: {self.cedula}, "
                f"Estado: {self.estado_registro})")
    
    def __repr__(self) -> str:
        return self.__str__()
    
    # ==================== MÉTODOS DE CLASE (Usan DIP) ====================
    
    @classmethod
    def obtener_total_postulantes(cls) -> int:
        """DIP: Usa repositorio abstracto"""
        return cls._repositorio.contar_total()
    
    @classmethod
    def cambiar_repositorio(cls, repositorio: RepositorioPostulantesAbstracto):
        """DIP: Permite cambiar el repositorio en runtime"""
        cls._repositorio = repositorio


# ==================== EJEMPLOS DE EXTENSIÓN (OCP) ====================

class PostulanteMenor(Postulante):
    """
    PRINCIPIO O (OCP): Extensión de Postulante sin modificar la clase base
    Maneja postulantes menores de edad con tutor legal
    """
    
    def __init__(self, cedula: str, nombre_completo: str, email: str,
                 telefono: str, fecha_nacimiento: str, tutor_nombre: str, tutor_cedula: str):
        super().__init__(cedula, nombre_completo, email, telefono, fecha_nacimiento)
        self.tutor_nombre = tutor_nombre
        self.tutor_cedula = tutor_cedula
        print(f" ✓ Tutor legal registrado: {tutor_nombre}")
    
    def validarIdentidad(self) -> bool:
        """Polimorfismo: Validación específica para menores"""
        # Primero valida identidad base
        if not super().validarIdentidad():
            return False
        
        # Luego valida tutor
        if not self.tutor_cedula or len(self.tutor_cedula) != 10:
            print(f"Tutor inválido para menor {self.nombre_completo}")
            self.estado_registro = 'RECHAZADO'
            return False
        
        print(f" ✓ Menor verificado con tutor: {self.tutor_nombre}")
        return True


class PostulanteExtranjero(Postulante):
    """
    PRINCIPIO O (OCP): Otra extensión sin modificar Postulante
    Maneja postulantes extranjeros con título homologado
    """
    
    def __init__(self, pasaporte: str, nombre_completo: str, email: str,
                 telefono: str, fecha_nacimiento: str, titulo_homologado: bool = False):
        super().__init__(pasaporte, nombre_completo, email, telefono, fecha_nacimiento)
        self.titulo_homologado = titulo_homologado
        print(f" ✓ Postulante extranjero registrado")
    
    def _validar_cedula(self, pasaporte: str) -> str:
        """Polimorfismo: Validación diferente para extranjeros"""
        pasaporte = pasaporte.strip()
        if len(pasaporte) < 5:
            raise ValueError(f"Pasaporte inválido")
        return pasaporte
    
    def validarIdentidad(self) -> bool:
        """Polimorfismo: Validación específica para extranjeros"""
        if not self.titulo_homologado:
            print(f"{self.nombre_completo} necesita título homologado")
            self.estado_registro = 'RECHAZADO'
            return False
        
        self.estado_registro = 'VERIFICADO'
        print(f" ✓ Extranjero verificado con título homologado")
        return True


# ==================== EJEMPLOS DE USO ====================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DEMOSTRACIÓN: TODOS LOS PRINCIPIOS SOLID - POSTULANTE")
    print("=" * 80)
    print("\n✅ S (SRP): Persona solo datos básicos, Postulante gestiona inscripciones")
    print("✅ O (OCP): Se pueden crear PostulanteMenor, PostulanteExtranjero sin modificar Postulante")
    print("✅ L (LSP): Todas las subclases sustituyen a Postulante correctamente")
    print("✅ I (ISP): Interfaces específicas (ValidadorIdentidad, CalculadorEdad)")
    print("✅ D (DIP): Usa RepositorioPostulantesAbstracto, no diccionario directo")
    print("=" * 80)
    
    # Ejemplo 1: Postulante regular
    print("\n\n EJEMPLO 1: Postulante Regular")
    print("-" * 80)
    try:
        postulante1 = Postulante(
            cedula="1316202082",
            nombre_completo="Jean Pierre Flores Piloso",
            email="florespilosojeanpierre@gmail.com",
            telefono="0979421538",
            fecha_nacimiento="2007-03-01"
        )
        
        postulante1.validarIdentidad()
        print(f"\n{postulante1}")
        print(f"Edad: {postulante1.calcularEdad()} años")
        print(f"Nombre (property): {postulante1.nombre_apellidos}")
        
    except ValueError as e:
        print(f"Error: {e}")
    
    # Ejemplo 2: Postulante menor (OCP en acción)
    print("\n\n EJEMPLO 2: Postulante Menor (Extensión OCP)")
    print("-" * 80)
    try:
        menor1 = PostulanteMenor(
            cedula="1350432058",
            nombre_completo="Braddy Londre Vera",
            email="braddy@uleam.edu.ec",
            telefono="0988888888",
            fecha_nacimiento="2008-03-20",
            tutor_nombre="Pedro Vera",
            tutor_cedula="1311111111"
        )
        
        menor1.validarIdentidad()
        print(f"\n{menor1}")
        
    except ValueError as e:
        print(f"Error: {e}")
    
    # Ejemplo 3: Postulante extranjero (OCP en acción)
    print("\n\n EJEMPLO 3: Postulante Extranjero (Extensión OCP)")
    print("-" * 80)
    try:
        extranjero1 = PostulanteExtranjero(
            pasaporte="PASS123456",
            nombre_completo="John Smith",
            email="john@mail.com",
            telefono="0998877665",
            fecha_nacimiento="1990-07-10",
            titulo_homologado=True
        )
        
        extranjero1.validarIdentidad()
        print(f"\n{extranjero1}")
        
    except ValueError as e:
        print(f"Error: {e}")
    
    # Demostrar DIP
    print("\n\n DEMOSTRACIÓN DIP:")
    print("-" * 80)
    print(f" Total postulantes: {Postulante.obtener_total_postulantes()}")
    print(" Se puede cambiar a RepositorioMySQL sin modificar la clase ✅")
    
    print("\n" + "=" * 80)