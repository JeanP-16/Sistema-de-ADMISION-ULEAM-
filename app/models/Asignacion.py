"""
Módulo: Asignacion aplicando PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
Fecha: Diciembre 2025

PRINCIPIOS SOLID APLICADOS (sin patrones de diseño específicos)
"""

from datetime import datetime
from typing import Optional, List, Dict
from abc import ABC, abstractmethod


# ==================== INTERFACES (Interface Segregation Principle) ====================

class IValidableRequisitos(ABC):
    """Interfaz específica para validación de requisitos"""
    @abstractmethod
    def validar_requisitos(self) -> bool:
        pass


class IProcesoCancelable(ABC):
    """Interfaz específica para procesos cancelables"""
    @abstractmethod
    def cancelar(self) -> None:
        pass


class IProcesoCompletable(ABC):
    """Interfaz específica para procesos completables"""
    @abstractmethod
    def completar(self) -> None:
        pass


# ==================== CLASE BASE (Liskov Substitution Principle) ====================

class ProcesoAcademico(IValidableRequisitos, IProcesoCancelable, IProcesoCompletable):
    """
    Clase base abstracta para procesos académicos
    
    SOLID:
    - Single Responsibility: Solo define la estructura de procesos académicos
    - Liskov Substitution: Las subclases pueden sustituir a esta clase
    """
    
    @abstractmethod
    def validar_requisitos(self) -> bool:
        pass
    
    @abstractmethod
    def cancelar(self) -> None:
        pass
    
    @abstractmethod
    def completar(self) -> None:
        pass


# ==================== SERVICIO DE GESTIÓN DE CUPOS (Single Responsibility) ====================

class ServicioCupos:
    """
    SINGLE RESPONSIBILITY: Solo gestiona cupos disponibles
    Separado de Asignacion para cumplir SRP
    """
    
    def __init__(self):
        self._cupos_por_carrera: Dict[int, int] = {}
    
    def configurar_cupos(self, carrera_id: int, cupos: int) -> None:
        """Configura cupos disponibles para una carrera"""
        self._cupos_por_carrera[carrera_id] = cupos
        print(f"[ServicioCupos] Cupos configurados para carrera {carrera_id}: {cupos}")
    
    def obtener_cupos_disponibles(self, carrera_id: int) -> int:
        """Obtiene cupos disponibles de una carrera"""
        return self._cupos_por_carrera.get(carrera_id, 0)
    
    def reducir_cupo(self, carrera_id: int) -> bool:
        """Reduce un cupo si hay disponibles"""
        if self._cupos_por_carrera.get(carrera_id, 0) > 0:
            self._cupos_por_carrera[carrera_id] -= 1
            return True
        return False
    
    def incrementar_cupo(self, carrera_id: int) -> None:
        """Incrementa un cupo (cuando se cancela asignación)"""
        cupos_actuales = self._cupos_por_carrera.get(carrera_id, 0)
        self._cupos_por_carrera[carrera_id] = cupos_actuales + 1


# ==================== VALIDADOR DE ASIGNACIONES (Single Responsibility) ====================

class ValidadorAsignacion:
    """
    SINGLE RESPONSIBILITY: Solo valida requisitos de asignación
    OPEN/CLOSED: Puede extenderse agregando más validaciones sin modificar código existente
    """
    
    PUNTAJE_MINIMO = 600
    
    def __init__(self, servicio_cupos: ServicioCupos):
        self._servicio_cupos = servicio_cupos
    
    def validar_cupos_disponibles(self, carrera_id: int) -> tuple[bool, Optional[str]]:
        """Valida si hay cupos disponibles"""
        cupos = self._servicio_cupos.obtener_cupos_disponibles(carrera_id)
        if cupos <= 0:
            return False, "Sin cupos disponibles"
        return True, None
    
    def validar_puntaje_minimo(self, puntaje: float) -> tuple[bool, Optional[str]]:
        """Valida si cumple puntaje mínimo"""
        if puntaje < self.PUNTAJE_MINIMO:
            return False, f"Puntaje insuficiente (mínimo {self.PUNTAJE_MINIMO})"
        return True, None
    
    def validar_todos_requisitos(self, carrera_id: int, puntaje: float) -> tuple[bool, Optional[str]]:
        """Valida todos los requisitos"""
        # Validar cupos
        valido_cupos, mensaje_cupos = self.validar_cupos_disponibles(carrera_id)
        if not valido_cupos:
            return False, mensaje_cupos
        
        # Validar puntaje
        valido_puntaje, mensaje_puntaje = self.validar_puntaje_minimo(puntaje)
        if not valido_puntaje:
            return False, mensaje_puntaje
        
        return True, None


# ==================== CLASE PRINCIPAL (todos los principios SOLID) ====================

class Asignacion(ProcesoAcademico):
    """
    Asignación de postulante a carrera
    
    SOLID APLICADO:
    - S: Responsabilidad única - gestionar datos de asignación
    - O: Abierto/Cerrado - se puede extender sin modificar
    - L: Liskov - puede sustituir a ProcesoAcademico
    - I: Interface Segregation - implementa interfaces específicas
    - D: Dependency Inversion - depende de abstracciones (ValidadorAsignacion, ServicioCupos)
    """
    
    ESTADOS_VALIDOS = ['ASIGNADO', 'PENDIENTE', 'RECHAZADO', 'CANCELADO']
    TIPOS_ASIGNACION = ['PRIMERA_OPCION', 'SEGUNDA_OPCION', 'TERCERA_OPCION', 'REASIGNACION']
    
    _contador_asignaciones = 0
    
    def __init__(self,
                 id_postulante: int,
                 carrera_id: int,
                 sede_id: int,
                 puntaje_total: float,
                 orden_merito: int,
                 validador: ValidadorAsignacion,  # DEPENDENCY INJECTION
                 servicio_cupos: ServicioCupos,   # DEPENDENCY INJECTION
                 tipo_asignacion: str = 'PRIMERA_OPCION'):
        
        Asignacion._contador_asignaciones += 1
        
        self.id_asignacion = Asignacion._contador_asignaciones
        self.id_postulante = id_postulante
        self.carrera_id = carrera_id
        self.sede_id = sede_id
        self.puntaje_total = puntaje_total
        self.orden_merito = orden_merito
        self.tipo_asignacion = tipo_asignacion.upper()
        
        # DEPENDENCY INVERSION: Depende de abstracciones
        self._validador = validador
        self._servicio_cupos = servicio_cupos
        
        self.fecha_asignacion = datetime.now()
        self.estado = 'PENDIENTE'
        self.observaciones = None
        self.fecha_aceptacion = None
        self.fecha_rechazo = None
        
        # Validaciones de entrada
        self._validar_tipo_asignacion()
        self._validar_rango_puntaje()
        
        print(f"Asignación creada: ID {self.id_asignacion} - Postulante {self.id_postulante}")
    
    def _validar_tipo_asignacion(self) -> None:
        """Valida que el tipo de asignación sea válido"""
        if self.tipo_asignacion not in self.TIPOS_ASIGNACION:
            raise ValueError(f"Tipo de asignación inválido: {self.tipo_asignacion}")
    
    def _validar_rango_puntaje(self) -> None:
        """Valida que el puntaje esté en rango válido"""
        if self.puntaje_total < 0 or self.puntaje_total > 1000:
            raise ValueError(f"Puntaje fuera de rango: {self.puntaje_total}")
    
    def validar_requisitos(self) -> bool:
        """
        DEPENDENCY INVERSION: Delega validación al ValidadorAsignacion
        """
        valido, mensaje = self._validador.validar_todos_requisitos(
            self.carrera_id,
            self.puntaje_total
        )
        
        if not valido:
            self.observaciones = mensaje
            print(f"[Validación] Asignación {self.id_asignacion}: {mensaje}")
            return False
        
        print(f"[Validación] Asignación {self.id_asignacion}: REQUISITOS CUMPLIDOS")
        return True
    
    def asignar(self) -> bool:
        """
        Confirma la asignación si cumple requisitos
        DEPENDENCY INVERSION: Usa ServicioCupos para gestionar cupos
        """
        if not self.validar_requisitos():
            self.estado = 'RECHAZADO'
            self.fecha_rechazo = datetime.now()
            return False
        
        # Reducir cupo usando el servicio
        if self._servicio_cupos.reducir_cupo(self.carrera_id):
            self.estado = 'ASIGNADO'
            self.fecha_aceptacion = datetime.now()
            self.observaciones = "Asignación exitosa"
            print(f"[Asignación] Postulante {self.id_postulante} asignado a carrera {self.carrera_id}")
            return True
        else:
            self.estado = 'RECHAZADO'
            self.observaciones = "No se pudo reducir cupo"
            return False
    
    def cancelar(self) -> None:
        """
        LISKOV SUBSTITUTION: Implementa correctamente el método de la clase base
        """
        if self.estado == 'ASIGNADO':
            # Devolver cupo usando el servicio
            self._servicio_cupos.incrementar_cupo(self.carrera_id)
        
        self.estado = 'CANCELADO'
        self.observaciones = "Asignación cancelada por el postulante"
        print(f"[Cancelación] Asignación {self.id_asignacion} cancelada")
    
    def completar(self) -> None:
        """
        LISKOV SUBSTITUTION: Implementa correctamente el método de la clase base
        """
        if self.estado == 'ASIGNADO':
            self.observaciones = "Proceso de asignación completado"
            print(f"[Completado] Asignación {self.id_asignacion} completada")
    
    def obtener_informacion(self) -> Dict:
        """Retorna información completa de la asignación"""
        return {
            'id_asignacion': self.id_asignacion,
            'id_postulante': self.id_postulante,
            'carrera_id': self.carrera_id,
            'sede_id': self.sede_id,
            'puntaje_total': self.puntaje_total,
            'orden_merito': self.orden_merito,
            'tipo_asignacion': self.tipo_asignacion,
            'estado': self.estado,
            'fecha_asignacion': self.fecha_asignacion.strftime('%Y-%m-%d %H:%M:%S'),
            'observaciones': self.observaciones
        }
    
    def __str__(self) -> str:
        return f"Asignacion(ID:{self.id_asignacion}, Postulante:{self.id_postulante}, Estado:{self.estado})"


# ==================== EJEMPLOS DE USO ====================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ASIGNACION - APLICANDO PRINCIPIOS SOLID (SIN PATRONES)")
    print("=" * 80)
    
    # Crear servicios (DEPENDENCY INJECTION)
    servicio_cupos = ServicioCupos()
    validador = ValidadorAsignacion(servicio_cupos)
    
    # Configurar cupos
    print("\n\nCONFIGURACIÓN INICIAL")
    print("-" * 80)
    servicio_cupos.configurar_cupos(101, 50)
    servicio_cupos.configurar_cupos(102, 30)
    
    # ===== EJEMPLO 1: Asignación exitosa =====
    print("\n\nEJEMPLO 1: Asignación Exitosa")
    print("-" * 80)
    
    asignacion1 = Asignacion(
        id_postulante=1,
        carrera_id=101,
        sede_id=1,
        puntaje_total=850,
        orden_merito=1,
        validador=validador,
        servicio_cupos=servicio_cupos,
        tipo_asignacion='PRIMERA_OPCION'
    )
    
    if asignacion1.asignar():
        print(f" {asignacion1}")
    
    print(f"Cupos restantes carrera 101: {servicio_cupos.obtener_cupos_disponibles(101)}")
    
    # ===== EJEMPLO 2: Asignación rechazada por puntaje =====
    print("\n\nEJEMPLO 2: Asignación Rechazada (puntaje bajo)")
    print("-" * 80)
    
    asignacion2 = Asignacion(
        id_postulante=2,
        carrera_id=101,
        sede_id=1,
        puntaje_total=550,
        orden_merito=50,
        validador=validador,
        servicio_cupos=servicio_cupos
    )
    
    if not asignacion2.asignar():
        print(f" {asignacion2}")
        print(f"   Motivo: {asignacion2.observaciones}")
    
    # ===== EJEMPLO 3: Asignación y cancelación =====
    print("\n\nEJEMPLO 3: Asignación y Cancelación")
    print("-" * 80)
    
    asignacion3 = Asignacion(
        id_postulante=3,
        carrera_id=102,
        sede_id=1,
        puntaje_total=750,
        orden_merito=5,
        validador=validador,
        servicio_cupos=servicio_cupos,
        tipo_asignacion='SEGUNDA_OPCION'
    )
    
    asignacion3.asignar()
    print(f"Cupos carrera 102 antes: {servicio_cupos.obtener_cupos_disponibles(102)}")
    
    asignacion3.cancelar()
    print(f"Cupos carrera 102 después: {servicio_cupos.obtener_cupos_disponibles(102)}")
    
    print("\n" + "=" * 80)
    print("PRINCIPIOS SOLID APLICADOS:")
    print("=" * 80)
    print(" S - Single Responsibility: Cada clase tiene UNA responsabilidad")
    print("   • Asignacion: gestión de asignación")
    print("   • ServicioCupos: gestión de cupos")
    print("   • ValidadorAsignacion: validación de requisitos")
    print()
    print(" O - Open/Closed: Extensible sin modificar código existente")
    print("   • Nuevas validaciones se agregan en ValidadorAsignacion")
    print()
    print(" L - Liskov Substitution: Asignacion sustituye a ProcesoAcademico")
    print()
    print(" I - Interface Segregation: Interfaces específicas y pequeñas")
    print("   • IValidableRequisitos, IProcesoCancelable, IProcesoCompletable")
    print()
    print(" D - Dependency Inversion: Depende de abstracciones")
    print("   • Asignacion recibe ValidadorAsignacion y ServicioCupos")
    print("=" * 80)
