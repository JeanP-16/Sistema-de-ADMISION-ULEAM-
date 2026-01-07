"""
Módulo: SedeCampus - CÓDIGO BUENO CON TODOS LOS PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Grabriel Cevallos
Fecha: Diciembre 2025
Descripción:
    Gestiona las sedes y campus de la Universidad Laica Eloy Alfaro de Manabí (ULEAM),
    aplicando herencia y polimorfismo básico para integrar la información con otros módulos.

PRINCIPIOS SOLID APLICADOS:
S (SRP): Responsabilidad única - gestionar información de sedes
O (OCP): Extensible mediante herencia de EntidadUniversitaria
L (LSP): Sustituible por EntidadUniversitaria
I (ISP): Interfaz pequeña con 2 métodos específicos
D (DIP): Depende de abstracción EntidadUniversitaria
"""

from abc import ABC, abstractmethod
from typing import Optional


# ==================== PRINCIPIO D (DIP) ====================
# ABSTRACCIÓN: Repositorio para almacenamiento
class RepositorioSedesAbstracto(ABC):
    """Interfaz abstracta para repositorios de sedes"""
    
    @abstractmethod
    def guardar(self, sede: 'SedeCampus') -> None:
        pass
    
    @abstractmethod
    def buscar_por_id(self, sede_id: int) -> Optional['SedeCampus']:
        pass
    
    @abstractmethod
    def contar_total(self) -> int:
        pass


# IMPLEMENTACIÓN CONCRETA
class RepositorioSedesEnMemoria(RepositorioSedesAbstracto):
    """Implementación concreta en memoria"""
    
    def __init__(self):
        self._sedes = {}
    
    def guardar(self, sede: 'SedeCampus') -> None:
        self._sedes[sede.sede_id] = sede
    
    def buscar_por_id(self, sede_id: int) -> Optional['SedeCampus']:
        return self._sedes.get(sede_id)
    
    def contar_total(self) -> int:
        return len(self._sedes)


# ==================== PRINCIPIO I (ISP) ====================
# INTERFAZ: Solo métodos esenciales para entidades universitarias
class EntidadUniversitaria(ABC):
    """
    Clase base abstracta para entidades de la universidad
    APLICA ISP: Interfaz pequeña con solo 2 métodos
    """

    @abstractmethod
    def obtener_info(self) -> dict:
        """Devuelve información estructurada de la entidad."""
        pass

    @abstractmethod
    def mostrar_info(self) -> None:
        """Muestra información de la entidad."""
        pass


# ==================== CLASE PRINCIPAL ====================
# APLICA: SRP, OCP, LSP, ISP, DIP
class SedeCampus(EntidadUniversitaria):
    """
    Representa una sede o campus de ULEAM.
    
    PRINCIPIOS SOLID APLICADOS:
    S (SRP): Solo gestiona información de sedes
    O (OCP): Extensible mediante herencia
    L (LSP): Sustituye correctamente a EntidadUniversitaria
    I (ISP): Implementa interfaz pequeña
    D (DIP): Usa RepositorioSedesAbstracto
    """

    _contador = 0
    _repositorio: RepositorioSedesAbstracto = RepositorioSedesEnMemoria()

    SEDES_ULEAM = {
        1: {'nombre': 'Matriz - Manta', 'canton': 'MANTA', 'provincia': 'MANABÍ'},
        2: {'nombre': 'Chone', 'canton': 'CHONE', 'provincia': 'MANABÍ'},
        3: {'nombre': 'El Carmen', 'canton': 'EL CARMEN', 'provincia': 'MANABÍ'},
        4: {'nombre': 'Pedernales', 'canton': 'PEDERNALES', 'provincia': 'MANABÍ'},
        5: {'nombre': 'Bahía de Caráquez', 'canton': 'SUCRE', 'provincia': 'MANABÍ'},
        6: {'nombre': 'Tosagua', 'canton': 'TOSAGUA', 'provincia': 'MANABÍ'},
        7: {'nombre': 'Santo Domingo', 'canton': 'SANTO DOMINGO', 'provincia': 'SANTO DOMINGO DE LOS TSÁCHILAS'},
        8: {'nombre': 'Flavio Alfaro', 'canton': 'FLAVIO ALFARO', 'provincia': 'MANABÍ'},
        9: {'nombre': 'Pichincha', 'canton': 'PICHINCHA', 'provincia': 'MANABÍ'}
    }

    def __init__(self, sede_id: int):
        """Inicializa una sede o campus según su ID oficial ULEAM."""
        if sede_id not in self.SEDES_ULEAM:
            raise ValueError(f"Sede ID {sede_id} no existe en ULEAM.")

        SedeCampus._contador += 1
        datos = self.SEDES_ULEAM[sede_id]

        self.sede_id = sede_id
        self.nombre_sede = datos['nombre']
        self.canton = datos['canton']
        self.provincia = datos['provincia']
        self.activa = True
        self.total_carreras = 0
        self.total_cupos = 0
        self.total_laboratorios = 0

        # PRINCIPIO D (DIP): Guardar usando repositorio abstracto
        SedeCampus._repositorio.guardar(self)

        print(f"Sede creada: {self.nombre_sede} ({self.canton}).")

    # ==================== POLIMORFISMO (LSP) ====================

    def obtener_info(self) -> dict:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de EntidadUniversitaria
        Devuelve información estructurada de la sede.
        """
        return {
            'sede_id': self.sede_id,
            'nombre': self.nombre_sede,
            'canton': self.canton,
            'provincia': self.provincia,
            'carreras': self.total_carreras,
            'cupos_totales': self.total_cupos,
            'laboratorios': self.total_laboratorios,
            'activa': self.activa
        }

    def mostrar_info(self) -> None:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de EntidadUniversitaria
        Muestra la información general de la sede.
        """
        print("\n" + "=" * 60)
        print(f"SEDE UNIVERSITARIA ULEAM")
        print("=" * 60)
        print(f"ID Sede: {self.sede_id}")
        print(f"Nombre: {self.nombre_sede}")
        print(f"Canton: {self.canton}")
        print(f"Provincia: {self.provincia}")
        print(f"Carreras registradas: {self.total_carreras}")
        print(f"Cupos totales: {self.total_cupos}")
        print(f"Laboratorios: {self.total_laboratorios}")
        print(f"Activa: {'Si' if self.activa else 'No'}")
        print("=" * 60)

    # ==================== MÉTODOS DE GESTIÓN ====================

    def agregar_carrera(self, nombre_carrera: str, cupos: int):
        """Registra una carrera en la sede."""
        self.total_carreras += 1
        self.total_cupos += cupos
        print(f"Carrera agregada: {nombre_carrera} ({cupos} cupos).")

    def agregar_laboratorio(self, nombre_laboratorio: str):
        """Registra un laboratorio en la sede."""
        self.total_laboratorios += 1
        print(f"Laboratorio agregado: {nombre_laboratorio}.")

    # ==================== MÉTODOS DE CLASE (Usan DIP) ====================

    @classmethod
    def listar_todas_sedes(cls):
        """Lista todas las sedes disponibles."""
        print("\n" + "=" * 60)
        print("LISTADO OFICIAL DE SEDES ULEAM 2025")
        print("=" * 60)
        for id_sede, datos in cls.SEDES_ULEAM.items():
            print(f"{id_sede}. {datos['nombre']:<30} | {datos['canton']:<16}")
        print("=" * 60)

    @classmethod
    def obtener_sede_por_canton(cls, canton: str) -> Optional[int]:
        """Busca sede por canton."""
        canton = canton.upper()
        for id_sede, datos in cls.SEDES_ULEAM.items():
            if datos['canton'] == canton:
                return id_sede
        return None

    @classmethod
    def obtener_total_sedes(cls) -> int:
        """Total de sedes creadas. PRINCIPIO D (DIP): Usa repositorio abstracto"""
        return cls._repositorio.contar_total()

    @classmethod
    def cambiar_repositorio(cls, repositorio: RepositorioSedesAbstracto):
        """PRINCIPIO D (DIP): Permite cambiar el repositorio en runtime"""
        cls._repositorio = repositorio

    # ==================== MÉTODOS ESPECIALES ====================

    def __str__(self) -> str:
        return f"SedeCampus(ID:{self.sede_id}, Nombre:{self.nombre_sede}, Canton:{self.canton})"

    def __repr__(self) -> str:
        return self.__str__()


# ==================== EJEMPLOS DE EXTENSIÓN (OCP) ====================

class SedePrincipal(SedeCampus):
    """
    PRINCIPIO O (OCP): Extension de SedeCampus sin modificar la clase base
    Representa sedes principales con funcionalidades adicionales
    """
    
    def __init__(self, sede_id: int):
        super().__init__(sede_id)
        self.es_principal = True
        self.tiene_rectorado = True
        print(f"Sede principal configurada: {self.nombre_sede}")
    
    def mostrar_info(self) -> None:
        """Polimorfismo: Información extendida para sede principal"""
        super().mostrar_info()
        print(f"Tipo: SEDE PRINCIPAL")
        print(f"Rectorado: {'Si' if self.tiene_rectorado else 'No'}")
        print("=" * 60)


class SedeExtension(SedeCampus):
    """
    PRINCIPIO O (OCP): Otra extension de SedeCampus
    Representa sedes de extension con funcionalidades limitadas
    """
    
    def __init__(self, sede_id: int, sede_principal_id: int):
        super().__init__(sede_id)
        self.es_extension = True
        self.sede_principal_id = sede_principal_id
        print(f"Sede extension configurada: {self.nombre_sede}")
    
    def mostrar_info(self) -> None:
        """Polimorfismo: Información extendida para sede extension"""
        super().mostrar_info()
        print(f"Tipo: SEDE EXTENSION")
        print(f"Depende de Sede ID: {self.sede_principal_id}")
        print("=" * 60)


# ==================== EJEMPLOS DE USO ====================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DEMOSTRACION: TODOS LOS PRINCIPIOS SOLID - SEDECAMPUS")
    print("=" * 80)
    print("\nS (SRP): Solo gestiona informacion de sedes")
    print("O (OCP): Se pueden crear SedePrincipal, SedeExtension sin modificar SedeCampus")
    print("L (LSP): Todas las subclases sustituyen a SedeCampus correctamente")
    print("I (ISP): Interfaz EntidadUniversitaria con solo 2 metodos")
    print("D (DIP): Usa RepositorioSedesAbstracto, no diccionario directo")
    print("=" * 80)
    
    # Ejemplo 1: Sede basica
    print("\n\nEJEMPLO 1: Sede Basica")
    print("-" * 80)
    sede1 = SedeCampus(1)  # Matriz - Manta
    sede1.agregar_carrera("Tecnologias de la Informacion", 40)
    sede1.agregar_carrera("Medicina", 70)
    sede1.agregar_laboratorio("Lab. Computo 1")
    sede1.mostrar_info()
    
    # Ejemplo 2: Sede Principal (OCP en accion)
    print("\n\nEJEMPLO 2: Sede Principal (Extension OCP)")
    print("-" * 80)
    sede_principal = SedePrincipal(1)  # Matriz - Manta
    sede_principal.agregar_carrera("Ingenieria Civil", 50)
    sede_principal.mostrar_info()
    
    # Ejemplo 3: Sede Extension (OCP en accion)
    print("\n\nEJEMPLO 3: Sede Extension (Extension OCP)")
    print("-" * 80)
    sede_extension = SedeExtension(2, sede_principal_id=1)  # Chone
    sede_extension.agregar_carrera("Administracion", 30)
    sede_extension.mostrar_info()
    
    # Listar todas las sedes disponibles
    print("\n\nLISTADO DE SEDES DISPONIBLES:")
    print("-" * 80)
    SedeCampus.listar_todas_sedes()
    
    # Demostrar DIP
    print("\n\nDEMOSTRACION DIP:")
    print("-" * 80)
    print(f"Total sedes creadas: {SedeCampus.obtener_total_sedes()}")
    print("Se puede cambiar a RepositorioMySQL sin modificar la clase")
    
    # Buscar sede por canton
    print("\n\nBUSCAR SEDE POR CANTON:")
    print("-" * 80)
    sede_id = SedeCampus.obtener_sede_por_canton("MANTA")
    print(f"Sede encontrada en MANTA: ID {sede_id}")
    
    print("\n" + "=" * 80)