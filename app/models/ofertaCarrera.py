"""
Módulo: OfertaCarrera - CÓDIGO BUENO CON TODOS LOS PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Grabriel Cevallos
Fecha: Diciembre 2025
Descripción:
    Gestiona las ofertas académicas de carreras con integración de herencia múltiple
    y polimorfismo aplicado a la administración de cupos y sedes ULEAM.

PRINCIPIOS SOLID APLICADOS:
S (SRP): Responsabilidades separadas (GestionCupos, InformacionSede)
O (OCP): Extensible mediante herencia múltiple
L (LSP): Sustituye correctamente a ambas clases padre
I (ISP): Dos interfaces específicas y pequeñas
D (DIP): Depende de abstracciones, usa inyección de dependencias
"""

from typing import Optional, Dict
from abc import ABC, abstractmethod


# ==================== PRINCIPIO D (DIP) ====================
# ABSTRACCIÓN: Repositorio para almacenamiento
class RepositorioOfertasAbstracto(ABC):
    """Interfaz abstracta para repositorios de ofertas"""
    
    @abstractmethod
    def guardar(self, oferta: 'OfertaCarrera') -> None:
        pass
    
    @abstractmethod
    def buscar_por_id(self, carrera_id: int) -> Optional['OfertaCarrera']:
        pass
    
    @abstractmethod
    def contar_total(self) -> int:
        pass


# IMPLEMENTACIÓN CONCRETA
class RepositorioOfertasEnMemoria(RepositorioOfertasAbstracto):
    """Implementación concreta en memoria"""
    
    def __init__(self):
        self._ofertas = {}
    
    def guardar(self, oferta: 'OfertaCarrera') -> None:
        self._ofertas[oferta.carrera_id] = oferta
    
    def buscar_por_id(self, carrera_id: int) -> Optional['OfertaCarrera']:
        return self._ofertas.get(carrera_id)
    
    def contar_total(self) -> int:
        return len(self._ofertas)


# ==================== PRINCIPIO I (ISP) ====================
# INTERFAZ 1: Gestión de cupos
class GestionCupos(ABC):
    """
    Clase abstracta que define métodos generales para gestión de cupos
    APLICA ISP: Interfaz específica solo para gestión de cupos
    """

    @abstractmethod
    def calcularCuposDisponibles(self, segmento: Optional[str] = None) -> int:
        pass

    @abstractmethod
    def reservarCupo(self, segmento: str) -> bool:
        pass

    @abstractmethod
    def liberarCupo(self, segmento: str) -> None:
        pass


# INTERFAZ 2: Información de sede
class InformacionSede(ABC):
    """
    Clase abstracta que modela datos básicos de una sede universitaria
    APLICA ISP: Interfaz específica solo para información de sede
    """

    @abstractmethod
    def mostrar_info_sede(self) -> None:
        pass


# ==================== CLASE PRINCIPAL ====================
# APLICA: SRP, OCP, LSP, ISP, DIP
class OfertaCarrera(GestionCupos, InformacionSede):
    """
    Representa la oferta de una carrera en una sede con sus cupos.
    
    PRINCIPIOS SOLID APLICADOS:
    S (SRP): Herencia múltiple separa responsabilidades
    O (OCP): Extensible mediante herencia
    L (LSP): Sustituye a GestionCupos e InformacionSede
    I (ISP): Implementa dos interfaces específicas
    D (DIP): Usa RepositorioOfertasAbstracto
    """

    _contador_ofertas = 0
    _repositorio: RepositorioOfertasAbstracto = RepositorioOfertasEnMemoria()
    
    PORCENTAJE_MINIMO_CUOTAS = 0.05
    PORCENTAJE_MAXIMO_CUOTAS = 0.10

    NIVELES = ['TERCER NIVEL', 'TERCER NIVEL TECNOLOGICO SUPERIOR']
    MODALIDADES = ['PRESENCIAL', 'HIBRIDA', 'SEMI-PRESENCIAL', 'DISTANCIA']
    JORNADAS = ['MATUTINA', 'VESPERTINA', 'NOCTURNA', 'NO APLICA JORNADA']

    def __init__(self, carrera_id: int, nombre_carrera: str, sede_id: int,
                 nombre_sede: str, cupos_total: int, nivel: str,
                 modalidad: str, jornada: str, ofa_id: int = None,
                 cus_id: int = None):
        """Inicializa una oferta de carrera (SENESCYT ULEAM 2025)."""
        OfertaCarrera._contador_ofertas += 1

        self.carrera_id = carrera_id
        self.ofa_id = ofa_id or (244900 + OfertaCarrera._contador_ofertas)
        self.cus_id = cus_id or (349000 + OfertaCarrera._contador_ofertas)
        self.nombre_carrera = nombre_carrera.upper()
        self.sede_id = sede_id
        self.nombre_sede = nombre_sede

        self.nivel = nivel.upper()
        self.modalidad = modalidad.upper()
        self.jornada = jornada.upper()

        self.cupos_total = cupos_total
        self.cupos_nivelacion = 0
        self.cupos_primer_semestre = 0
        self.cupos_pc = 0
        self.tipo_cupo = 'CUPOS_NIVELACION'
        self.focalizada = 'N'

        # Segmentación de cupos
        self._calcular_distribucion_cupos()

        # Registro de cupos asignados
        self.cupos_asignados = {
            'CUOTAS': 0,
            'VULNERABILIDAD': 0,
            'MERITO_ACADEMICO': 0,
            'RECONOCIMIENTOS': 0,
            'PUEBLOS_NACIONALIDADES': 0,
            'BACHILLERES': 0,
            'GENERAL': 0
        }
        
        # PRINCIPIO D (DIP): Guardar usando repositorio abstracto
        OfertaCarrera._repositorio.guardar(self)
        
        print(f"  Oferta creada: {nombre_carrera[:40]} ({nombre_sede})")
        print(f"   Cupos: {cupos_total} | {nivel} | {modalidad} | {jornada}")
    
    def _calcular_distribucion_cupos(self):
        """Calcula la distribución inicial de cupos."""
        self.cupos_pc = max(int(self.cupos_total * self.PORCENTAJE_MINIMO_CUOTAS), 1)
        self.cupos_nivelacion = self.cupos_total - self.cupos_pc
        
        # Distribuir por segmentos
        cupos_restantes = self.cupos_total - self.cupos_pc
        
        self.cupos_vulnerabilidad = int(cupos_restantes * 0.20)
        self.cupos_merito = int(cupos_restantes * 0.30)
        self.cupos_general = cupos_restantes - self.cupos_vulnerabilidad - self.cupos_merito
    
    # ==================== POLIMORFISMO (LSP) ====================
    
    def mostrar_info_sede(self) -> None:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de InformacionSede
        """
        print("\n--- Informacion de la Sede ---")
        print(f"Sede ID: {self.sede_id}")
        print(f"Nombre Sede: {self.nombre_sede}")
        print(f"Carrera: {self.nombre_carrera}")
        print(f"Nivel: {self.nivel}")
        print(f"Modalidad: {self.modalidad}")
        print(f"Jornada: {self.jornada}")
        print("-" * 40)

    def configurar_desde_pdf(self, cupos_nivelacion: int = 0,
                            cupos_primer_semestre: int = 0,
                            cupos_pc: int = 0,
                            tipo_cupo: str = 'CUPOS_NIVELACION',
                            focalizada: str = 'N'):
        """Configura los cupos según los datos extraídos del PDF oficial ULEAM."""
        self.cupos_nivelacion = cupos_nivelacion
        self.cupos_primer_semestre = cupos_primer_semestre
        self.cupos_pc = cupos_pc
        self.tipo_cupo = tipo_cupo
        self.focalizada = focalizada

        # Recalcular el total general
        self.cupos_total = cupos_nivelacion + cupos_primer_semestre + cupos_pc

        print("  Configuracion desde PDF aplicada")
        print(f"   Nivelacion: {cupos_nivelacion} | Primer Semestre: {cupos_primer_semestre} | PC: {cupos_pc}")

    @classmethod
    def crear_desde_pdf_uleam(cls, datos: dict):
        """Crea una oferta a partir de los datos del PDF ULEAM."""
        oferta = cls(
            carrera_id=datos.get('carrera_id', 0),
            nombre_carrera=datos.get('CAR_NOMBRE_CARRERA', 'SIN NOMBRE'),
            sede_id=datos.get('sede_id', 0),
            nombre_sede=datos.get('PRQ_NOMBRE', 'NO DEFINIDA'),
            cupos_total=datos.get('CUS_TOTAL_CUPOS', 0),
            nivel=datos.get('NIVEL', 'TERCER NIVEL'),
            modalidad=datos.get('MODALIDAD', 'PRESENCIAL'),
            jornada=datos.get('JORNADA', 'MATUTINA'),
            ofa_id=datos.get('OFA_ID'),
            cus_id=datos.get('CUS_ID')
        )

        oferta.configurar_desde_pdf(
            cupos_nivelacion=datos.get('CUS_CUPOS_NIVELACION', 0),
            cupos_primer_semestre=datos.get('CUS_CUPOS_PRIMER_SEMESTRE', 0),
            cupos_pc=datos.get('CUS_CUPOS_PC', 0),
            tipo_cupo=datos.get('DESCRIPCION_TIPO_CUPO', 'CUPOS_NIVELACION'),
            focalizada=datos.get('FOCALIZADA', 'N')
        )

        return oferta
    
    def calcularCuposDisponibles(self, segmento: Optional[str] = None) -> int:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de GestionCupos
        Polimorfismo: calcula disponibilidad general o segmentada
        """
        if segmento is None:
            total_asignados = sum(self.cupos_asignados.values())
            return self.cupos_total - total_asignados

        seg = segmento.upper()
        if seg not in self.cupos_asignados:
            return 0

        limites = {
            'CUOTAS': self.cupos_pc,
            'VULNERABILIDAD': self.cupos_vulnerabilidad,
            'MERITO_ACADEMICO': self.cupos_merito,
            'GENERAL': self.cupos_general
        }

        limite = limites.get(seg, self.cupos_general)
        return max(limite - self.cupos_asignados[seg], 0)

    def reservarCupo(self, segmento: str) -> bool:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de GestionCupos
        Reserva un cupo en el segmento especificado
        """
        segmento = segmento.upper()
        
        if segmento not in self.cupos_asignados:
            print(f" Segmento invalido: {segmento}")
            return False

        disponibles = self.calcularCuposDisponibles(segmento)
        if disponibles <= 0:
            print(f" No hay cupos disponibles en {segmento}")
            return False
        
        # Reservar cupo
        self.cupos_asignados[segmento] += 1
        
        print(f"  Cupo reservado en {segmento}")
        print(f"   Asignados: {self.cupos_asignados[segmento]} | Disponibles: {disponibles - 1}")
        
        return True

    def liberarCupo(self, segmento: str) -> None:
        """
        PRINCIPIO L (LSP): Implementa método abstracto de GestionCupos
        Libera un cupo previamente asignado
        """
        segmento = segmento.upper()
        
        if segmento not in self.cupos_asignados:
            print(f" Segmento invalido: {segmento}")
            return
        
        if self.cupos_asignados[segmento] > 0:
            self.cupos_asignados[segmento] -= 1
            disponibles = self.calcularCuposDisponibles(segmento)
            
            print(f" Cupo liberado en {segmento}")
            print(f"   Disponibles ahora: {disponibles}")
        else:
            print(f" No hay cupos asignados en {segmento} para liberar")
    
    # ==================== MÉTODOS ADICIONALES ====================
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas completas de la oferta."""
        total_asignados = sum(self.cupos_asignados.values())
        total_disponibles = self.cupos_total - total_asignados
        porcentaje_ocupacion = (total_asignados / self.cupos_total * 100) if self.cupos_total > 0 else 0

        return {
            'carrera': self.nombre_carrera,
            'sede': self.nombre_sede,
            'total_cupos': self.cupos_total,
            'asignados': total_asignados,
            'disponibles': total_disponibles,
            'ocupacion_%': round(porcentaje_ocupacion, 2),
            'segmentos': self.cupos_asignados.copy()
        }

    def mostrar_resumen(self) -> None:
        """Polimorfismo aplicado: muestra resumen según estado de ocupación."""
        info = self.obtener_estadisticas()
        print("\n" + "=" * 60)
        print(f"OFERTA: {info['carrera']} - {info['sede']}")
        print("=" * 60)
        print(f"Cupos Totales: {info['total_cupos']}")
        print(f"Cupos Asignados: {info['asignados']}")
        print(f"Cupos Disponibles: {info['disponibles']}")
        print(f"Ocupacion: {info['ocupacion_%']}%")
        print("-" * 60)
        for s, c in info['segmentos'].items():
            print(f"{s:<25}: {c}")
        print("=" * 60)

    def __str__(self) -> str:
        """Representación legible de la oferta."""
        return f"OfertaCarrera({self.nombre_carrera}, {self.nombre_sede}, Cupos={self.cupos_total})"

    # ==================== MÉTODOS DE CLASE (Usan DIP) ====================

    @classmethod
    def obtener_total_ofertas(cls) -> int:
        """PRINCIPIO D (DIP): Usa repositorio abstracto"""
        return cls._repositorio.contar_total()

    @classmethod
    def cambiar_repositorio(cls, repositorio: RepositorioOfertasAbstracto):
        """PRINCIPIO D (DIP): Permite cambiar el repositorio en runtime"""
        cls._repositorio = repositorio


# ==================== EJEMPLOS DE EXTENSIÓN (OCP) ====================

class OfertaCarreraConBeca(OfertaCarrera):
    """
    PRINCIPIO O (OCP): Extensión de OfertaCarrera sin modificar la clase base
    Maneja ofertas con becas disponibles
    """
    
    def __init__(self, carrera_id: int, nombre_carrera: str, sede_id: int,
                 nombre_sede: str, cupos_total: int, nivel: str,
                 modalidad: str, jornada: str, cupos_becas: int = 0,
                 ofa_id: int = None, cus_id: int = None):
        super().__init__(carrera_id, nombre_carrera, sede_id, nombre_sede,
                        cupos_total, nivel, modalidad, jornada, ofa_id, cus_id)
        self.cupos_becas = cupos_becas
        self.becas_asignadas = 0
        print(f"  Oferta con {cupos_becas} becas disponibles")
    
    def asignar_beca(self, postulante: str) -> bool:
        """Método específico para asignar becas"""
        if self.becas_asignadas < self.cupos_becas:
            self.becas_asignadas += 1
            print(f"  Beca asignada a {postulante}")
            return True
        print(f"  No hay becas disponibles")
        return False


# ==================== EJEMPLOS DE USO ====================
if __name__ == "__main__":
    print("=" * 70)
    print("DEMOSTRACION: TODOS LOS PRINCIPIOS SOLID - OFERTACARRERA")
    print("=" * 70)
    print("\nS (SRP): GestionCupos y InformacionSede separadas")
    print("O (OCP): Se puede crear OfertaCarreraConBeca sin modificar OfertaCarrera")
    print("L (LSP): OfertaCarrera sustituye a ambas clases padre")
    print("I (ISP): Dos interfaces específicas (GestionCupos, InformacionSede)")
    print("D (DIP): Usa RepositorioOfertasAbstracto")
    print("=" * 70)
    
    # Ejemplo 1: Oferta básica
    print("\n\nEJEMPLO 1: Oferta Basica")
    print("-" * 70)
    
    datos_ti = {
        'carrera_id': 101,
        'CAR_NOMBRE_CARRERA': 'TECNOLOGIAS DE LA INFORMACION',
        'PRQ_NOMBRE': 'MANTA',
        'sede_id': 1,
        'NIVEL': 'TERCER NIVEL',
        'MODALIDAD': 'PRESENCIAL',
        'JORNADA': 'MATUTINA',
        'CUS_TOTAL_CUPOS': 40,
        'CUS_CUPOS_NIVELACION': 38,
        'CUS_CUPOS_PRIMER_SEMESTRE': 0,
        'CUS_CUPOS_PC': 2,
        'OFA_ID': 245912,
        'CUS_ID': 350708,
        'FOCALIZADA': 'N',
        'DESCRIPCION_TIPO_CUPO': 'CUPOS_NIVELACION'
    }
    
    oferta_ti = OfertaCarrera.crear_desde_pdf_uleam(datos_ti)
    oferta_ti.mostrar_resumen()
    
    # Simular asignaciones
    print("\nSimulando asignaciones...")
    oferta_ti.reservarCupo("MERITO_ACADEMICO")
    oferta_ti.reservarCupo("VULNERABILIDAD")
    oferta_ti.reservarCupo("GENERAL")
    
    oferta_ti.mostrar_resumen()
    
    # Ejemplo 2: Oferta con becas (OCP en acción)
    print("\n\nEJEMPLO 2: Oferta con Becas (Extension OCP)")
    print("-" * 70)
    
    oferta_medicina = OfertaCarreraConBeca(
        carrera_id=102,
        nombre_carrera="Medicina",
        sede_id=1,
        nombre_sede="MANTA",
        cupos_total=70,
        nivel="TERCER NIVEL",
        modalidad="PRESENCIAL",
        jornada="MATUTINA",
        cupos_becas=10
    )
    
    oferta_medicina.asignar_beca("Juan Perez")
    oferta_medicina.asignar_beca("Maria Lopez")
    print(f"\n{oferta_medicina}")
    
    # Demostrar DIP
    print("\n\nDEMOSTRACION DIP:")
    print("-" * 70)
    print(f"Total ofertas creadas: {OfertaCarrera.obtener_total_ofertas()}")
    print("Se puede cambiar a RepositorioMySQL sin modificar la clase")
    
    print("\n" + "=" * 70)