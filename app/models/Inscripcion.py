"""
Módulo: Inscripcion - CÓDIGO BUENO CON TODOS LOS PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Grabriel Cevallos
Fecha: Diciembre 2025
Descripción: Clase que representa la inscripción de un postulante a una carrera.
             Implementa herencia, abstracción y polimorfismo básico.

PRINCIPIOS SOLID APLICADOS:
S (SRP): Responsabilidades separadas (ProcesoBase define contrato)
O (OCP): Extensible mediante herencia de ProcesoBase
L (LSP): Sustituye correctamente a ProcesoBase
I (ISP): Interfaz específica con métodos necesarios
D (DIP): Depende de abstracciones, usa inyección de dependencias
"""

from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional


# ==================== PRINCIPIO D (DIP) ====================
# ABSTRACCIÓN: Repositorio para almacenamiento
class RepositorioInscripcionesAbstracto(ABC):
    """Interfaz abstracta para repositorios de inscripciones"""
    
    @abstractmethod
    def guardar(self, inscripcion: 'Inscripcion') -> None:
        pass
    
    @abstractmethod
    def buscar_por_id(self, id_inscripcion: int) -> Optional['Inscripcion']:
        pass
    
    @abstractmethod
    def contar_total(self) -> int:
        pass


# IMPLEMENTACIÓN CONCRETA
class RepositorioInscripcionesEnMemoria(RepositorioInscripcionesAbstracto):
    """Implementación concreta en memoria"""
    
    def __init__(self):
        self._inscripciones = {}
    
    def guardar(self, inscripcion: 'Inscripcion') -> None:
        self._inscripciones[inscripcion.id_inscripcion] = inscripcion
    
    def buscar_por_id(self, id_inscripcion: int) -> Optional['Inscripcion']:
        return self._inscripciones.get(id_inscripcion)
    
    def contar_total(self) -> int:
        return len(self._inscripciones)


# ABSTRACCIÓN: Servicio de notificaciones
class ServicioNotificacionesAbstracto(ABC):
    """Interfaz abstracta para servicios de notificación"""
    
    @abstractmethod
    def notificar_inscripcion(self, email: str, id_inscripcion: int, carrera: str) -> None:
        pass


# IMPLEMENTACIÓN CONCRETA
class ServicioNotificacionesEmail(ServicioNotificacionesAbstracto):
    """Implementación concreta con email"""
    
    def notificar_inscripcion(self, email: str, id_inscripcion: int, carrera: str) -> None:
        print(f"  [Email] Notificacion enviada a {email}")
        print(f"          Inscripcion {id_inscripcion} - Carrera: {carrera}")


# ==================== PRINCIPIO I (ISP) ====================
# INTERFAZ: Contrato para procesos administrativos
class ProcesoBase(ABC):
    """
    Clase base abstracta para procesos administrativos del sistema
    APLICA ISP: Interfaz específica con métodos esenciales
    """

    @abstractmethod
    def validarRequisitos(self) -> bool:
        """Valida los requisitos del proceso."""
        pass

    @abstractmethod
    def cancelar(self) -> None:
        """Cancela el proceso."""
        pass

    @abstractmethod
    def completar(self) -> None:
        """Completa el proceso."""
        pass

    @abstractmethod
    def mostrar_info_completa(self) -> None:
        """Muestra toda la información detallada del proceso."""
        pass


# ==================== CLASE PRINCIPAL ====================
# APLICA: SRP, OCP, LSP, ISP, DIP
class Inscripcion(ProcesoBase):
    """
    Representa la solicitud de inscripción de un postulante a una carrera.
    
    PRINCIPIOS SOLID APLICADOS:
    S (SRP): Hereda de ProcesoBase (responsabilidades separadas)
    O (OCP): Extensible mediante herencia
    L (LSP): Sustituye correctamente a ProcesoBase
    I (ISP): Implementa interfaz específica
    D (DIP): Usa RepositorioInscripcionesAbstracto y ServicioNotificacionesAbstracto
    """

    _contador_inscripciones = 0
    _repositorio: RepositorioInscripcionesAbstracto = RepositorioInscripcionesEnMemoria()
    _servicio_notificaciones: ServicioNotificacionesAbstracto = ServicioNotificacionesEmail()
    
    JORNADAS_VALIDAS = ['matutina', 'vespertina', 'nocturna']
    ESTADOS_VALIDOS = ['ACTIVA', 'CANCELADA', 'COMPLETADA']
    MAX_PREFERENCIAS = 3

    def __init__(self,
                 id_postulante: int,
                 carrera_id: int,
                 orden_preferencia: int,
                 sede_id: int,
                 jornada: str,
                 cedula_postulante: str,
                 email_postulante: str = None,
                 laboratorio_id: Optional[int] = None):
        """Inicializa una nueva inscripción y crea automáticamente su evaluación."""
        Inscripcion._contador_inscripciones += 1

        self.id_inscripcion = Inscripcion._contador_inscripciones
        self.id_postulante = id_postulante
        self.carrera_id = carrera_id
        self.orden_preferencia = self._validar_orden_preferencia(orden_preferencia)
        self.sede_id = sede_id
        self.jornada = self._validar_jornada(jornada)
        self.laboratorio_id = laboratorio_id
        self.cedula_postulante = cedula_postulante
        self.email_postulante = email_postulante
        self.fecha_inscripcion = datetime.now()
        self.comprobante_pdf_url = f"COMP-{self.id_inscripcion}-{self.cedula_postulante}.pdf"
        self.estado = 'ACTIVA'
        self._evaluacion = None

        # PRINCIPIO D (DIP): Guardar usando repositorio abstracto
        Inscripcion._repositorio.guardar(self)

        self._crear_evaluacion_automatica()
        
        # PRINCIPIO D (DIP): Notificar usando servicio abstracto
        if self.email_postulante:
            Inscripcion._servicio_notificaciones.notificar_inscripcion(
                self.email_postulante, 
                self.id_inscripcion,
                f"Carrera ID: {self.carrera_id}"
            )

    # ==================== VALIDACIONES (SRP) ====================

    def _validar_orden_preferencia(self, orden: int) -> int:
        """Valida el orden de preferencia."""
        if not isinstance(orden, int) or orden < 1 or orden > self.MAX_PREFERENCIAS:
            raise ValueError(f"Orden debe estar entre 1 y {self.MAX_PREFERENCIAS}.")
        return orden

    def _validar_jornada(self, jornada: str) -> str:
        """Valida la jornada ingresada."""
        jornada = jornada.lower().strip()
        if jornada not in self.JORNADAS_VALIDAS:
            raise ValueError(f"Jornada invalida. Debe ser: {', '.join(self.JORNADAS_VALIDAS)}.")
        return jornada

    # ==================== POLIMORFISMO (LSP) ====================

    def validarRequisitos(self) -> bool:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de ProcesoBase
        Valida que la inscripción cumpla con los requisitos
        """
        cumple = True

        if not self.comprobante_pdf_url:
            print("Advertencia: Falta comprobante de inscripcion.")
            cumple = False

        if self.estado == 'CANCELADA':
            print("No se puede validar una inscripcion cancelada.")
            return False

        if cumple:
            print(f"Requisitos validados correctamente para inscripcion {self.id_inscripcion}.")
        return cumple

    def cancelar(self) -> None:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de ProcesoBase
        Cancela la inscripción
        """
        self.estado = 'CANCELADA'
        if self._evaluacion:
            self._evaluacion.cancelar()
        print(f"Inscripcion {self.id_inscripcion} cancelada correctamente.")

    def completar(self) -> None:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de ProcesoBase
        Completa la inscripción
        """
        self.estado = 'COMPLETADA'
        print(f"Inscripcion {self.id_inscripcion} completada exitosamente.")

    def mostrar_info_completa(self) -> None:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de ProcesoBase
        Muestra toda la información de la inscripción, incluyendo evaluación
        """
        print("\n" + "=" * 60)
        print(f"INSCRIPCION ID: {self.id_inscripcion}")
        print("=" * 60)
        print(f"Cedula Postulante: {self.cedula_postulante}")
        print(f"Postulante ID: {self.id_postulante}")
        print(f"Carrera ID: {self.carrera_id}")
        print(f"Orden preferencia: {self.orden_preferencia}")
        print(f"Sede ID: {self.sede_id}")
        print(f"Jornada: {self.jornada}")
        print(f"Laboratorio ID: {self.laboratorio_id}")
        print(f"Fecha inscripcion: {self.fecha_inscripcion.strftime('%d/%m/%Y %H:%M')}")
        print(f"Comprobante: {self.comprobante_pdf_url}")
        print(f"Estado: {self.estado}")
        print("=" * 60)
        if self._evaluacion:
            print("\nEVALUACION ASOCIADA:")
            self._evaluacion.mostrar_info()

    # ==================== MÉTODOS INTERNOS ====================

    def _crear_evaluacion_automatica(self) -> None:
        """Crea automáticamente la evaluación para esta inscripción."""
        try:
            from models.Evaluacion import Evaluacion
            tipo_eval = self._determinar_tipo_evaluacion(self.carrera_id)

            self._evaluacion = Evaluacion(
                id_inscripcion=self.id_inscripcion,
                tipo=tipo_eval,
                sede_id=self.sede_id,
                jornada=self.jornada,
                laboratorio_id=self.laboratorio_id,
                auto_programar=True
            )

            print(f"\nEvaluacion creada automaticamente:")
            print(f"ID: {self._evaluacion.id_evaluacion}")
            print(f"Tipo: {self._evaluacion.tipo}")
            print(f"Fecha: {self._evaluacion.fecha_programada.strftime('%d/%m/%Y')}")
            print(f"Laboratorio: {self._evaluacion.laboratorio_id}")

        except ImportError:
            print("No se pudo importar el modulo Evaluacion. Verifique la estructura del proyecto.")

    def _determinar_tipo_evaluacion(self, carrera_id: int) -> str:
        """Determina el tipo de evaluación según la carrera."""
        if carrera_id in [101, 102]:
            return "practico"
        elif carrera_id in [103, 104]:
            return "escrito"
        else:
            return "escrito"

    def obtenerEvaluacion(self):
        """Devuelve la evaluación asociada."""
        return self._evaluacion

    # ==================== MÉTODOS ESPECIALES ====================

    def __str__(self) -> str:
        return f"Inscripcion(ID:{self.id_inscripcion}, Postulante:{self.id_postulante}, Estado:{self.estado})"

    # ==================== MÉTODOS DE CLASE (Usan DIP) ====================

    @classmethod
    def obtener_total_inscripciones(cls) -> int:
        """PRINCIPIO D (DIP): Usa repositorio abstracto"""
        return cls._repositorio.contar_total()

    @classmethod
    def cambiar_repositorio(cls, repositorio: RepositorioInscripcionesAbstracto):
        """PRINCIPIO D (DIP): Permite cambiar el repositorio en runtime"""
        cls._repositorio = repositorio

    @classmethod
    def cambiar_servicio_notificaciones(cls, servicio: ServicioNotificacionesAbstracto):
        """PRINCIPIO D (DIP): Permite cambiar el servicio de notificaciones"""
        cls._servicio_notificaciones = servicio


# ==================== EJEMPLOS DE EXTENSIÓN (OCP) ====================

class InscripcionPrioritaria(Inscripcion):
    """
    PRINCIPIO O (OCP): Extensión de Inscripcion sin modificar la clase base
    Maneja inscripciones prioritarias que requieren validación adicional
    """
    
    def __init__(self, id_postulante: int, carrera_id: int, orden_preferencia: int,
                 sede_id: int, jornada: str, cedula_postulante: str,
                 documento_prioritario: str, email_postulante: str = None,
                 laboratorio_id: Optional[int] = None):
        self.documento_prioritario = documento_prioritario
        super().__init__(id_postulante, carrera_id, orden_preferencia, sede_id,
                        jornada, cedula_postulante, email_postulante, laboratorio_id)
        print(f"  Inscripcion prioritaria con documento: {documento_prioritario}")
    
    def validarRequisitos(self) -> bool:
        """Polimorfismo: Validación adicional para inscripciones prioritarias"""
        # Primero valida requisitos base
        if not super().validarRequisitos():
            return False
        
        # Luego valida documento prioritario
        if not self.documento_prioritario:
            print(f"  Falta documento prioritario para inscripcion {self.id_inscripcion}")
            return False
        
        print(f"  Inscripcion prioritaria validada correctamente")
        return True


class InscripcionConBeca(Inscripcion):
    """
    PRINCIPIO O (OCP): Otra extensión sin modificar Inscripcion
    Maneja inscripciones con solicitud de beca
    """
    
    def __init__(self, id_postulante: int, carrera_id: int, orden_preferencia: int,
                 sede_id: int, jornada: str, cedula_postulante: str,
                 solicita_beca: bool = True, email_postulante: str = None,
                 laboratorio_id: Optional[int] = None):
        self.solicita_beca = solicita_beca
        self.beca_aprobada = False
        super().__init__(id_postulante, carrera_id, orden_preferencia, sede_id,
                        jornada, cedula_postulante, email_postulante, laboratorio_id)
        if self.solicita_beca:
            print(f"  Inscripcion con solicitud de beca")
    
    def aprobar_beca(self) -> None:
        """Método específico para aprobar beca"""
        if self.solicita_beca:
            self.beca_aprobada = True
            print(f"  Beca aprobada para inscripcion {self.id_inscripcion}")


# ==================== EJEMPLOS DE USO ====================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DEMOSTRACION: TODOS LOS PRINCIPIOS SOLID - INSCRIPCION")
    print("=" * 80)
    print("\nS (SRP): ProcesoBase define contrato, Inscripcion gestiona proceso")
    print("O (OCP): Se pueden crear InscripcionPrioritaria, InscripcionConBeca")
    print("L (LSP): Todas las subclases sustituyen a Inscripcion correctamente")
    print("I (ISP): Interfaz ProcesoBase con métodos específicos necesarios")
    print("D (DIP): Usa RepositorioInscripcionesAbstracto y ServicioNotificacionesAbstracto")
    print("=" * 80)
    
    # Ejemplo 1: Inscripción básica
    print("\n\nEJEMPLO 1: Inscripcion Basica")
    print("-" * 80)
    try:
        inscripcion1 = Inscripcion(
            id_postulante=1,
            carrera_id=101,
            orden_preferencia=1,
            sede_id=1,
            jornada="matutina",
            cedula_postulante="1316202082",
            email_postulante="jean@uleam.edu.ec",
            laboratorio_id=101
        )
        
        inscripcion1.validarRequisitos()
        inscripcion1.mostrar_info_completa()
        
    except ValueError as e:
        print(f"Error: {e}")
    
    # Ejemplo 2: Inscripción prioritaria (OCP en acción)
    print("\n\nEJEMPLO 2: Inscripcion Prioritaria (Extension OCP)")
    print("-" * 80)
    try:
        inscripcion_prioritaria = InscripcionPrioritaria(
            id_postulante=2,
            carrera_id=102,
            orden_preferencia=1,
            sede_id=1,
            jornada="vespertina",
            cedula_postulante="1350432058",
            documento_prioritario="CERT-MERITO-2024",
            email_postulante="braddy@uleam.edu.ec"
        )
        
        inscripcion_prioritaria.validarRequisitos()
        print(f"\n{inscripcion_prioritaria}")
        
    except ValueError as e:
        print(f"Error: {e}")
    
    # Ejemplo 3: Inscripción con beca (OCP en acción)
    print("\n\nEJEMPLO 3: Inscripcion Con Beca (Extension OCP)")
    print("-" * 80)
    try:
        inscripcion_beca = InscripcionConBeca(
            id_postulante=3,
            carrera_id=103,
            orden_preferencia=1,
            sede_id=2,
            jornada="nocturna",
            cedula_postulante="1360234567",
            solicita_beca=True,
            email_postulante="bismark@uleam.edu.ec"
        )
        
        inscripcion_beca.aprobar_beca()
        print(f"\n{inscripcion_beca}")
        
    except ValueError as e:
        print(f"Error: {e}")
    
    # Demostrar DIP
    print("\n\nDEMOSTRACION DIP:")
    print("-" * 80)
    print(f"Total inscripciones: {Inscripcion.obtener_total_inscripciones()}")
    print("Se puede cambiar a RepositorioMySQL sin modificar la clase")
    print("Se puede cambiar a ServicioSMS sin modificar la clase")
    
    print("\n" + "=" * 80)