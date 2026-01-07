"""
Módulo: PoliticaAccionAfirmativa aplicando PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
Fecha: Diciembre 2025

PRINCIPIOS SOLID APLICADOS (sin patrones de diseño específicos)
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict


# ==================== INTERFACES (Interface Segregation Principle) ====================

class IAplicableCondicionSocial(ABC):
    """Interfaz específica para aplicar condiciones sociales"""
    @abstractmethod
    def aplicar_condicion_socioeconomica(self, quintil: int) -> None:
        pass


class IAplicableRuralidad(ABC):
    """Interfaz específica para aplicar ruralidad"""
    @abstractmethod
    def aplicar_ruralidad(self, tipo_institucion: str, zona: str) -> None:
        pass


class IAplicableDiscapacidad(ABC):
    """Interfaz específica para aplicar discapacidad"""
    @abstractmethod
    def aplicar_discapacidad(self, porcentaje: int, tiene_carnet: bool) -> None:
        pass


class ICalculableSegmento(ABC):
    """Interfaz específica para calcular segmento"""
    @abstractmethod
    def calcular_segmento(self) -> str:
        pass


# ==================== EVALUADOR DE CONDICIONES (Single Responsibility) ====================

class EvaluadorCondicionesSociales:
    """
    SINGLE RESPONSIBILITY: Solo evalúa condiciones sociales
    OPEN/CLOSED: Se pueden agregar nuevas evaluaciones sin modificar existentes
    """
    
    def evaluar_condicion_socioeconomica(self, quintil: int) -> tuple[bool, bool]:
        """
        Evalúa condición socioeconómica
        Retorna: (tiene_condicion, es_vulnerable)
        """
        tiene_condicion = quintil <= 2
        es_vulnerable = quintil == 1
        return tiene_condicion, es_vulnerable
    
    def evaluar_ruralidad(self, tipo_institucion: str, zona: str) -> bool:
        """Evalúa si aplica ruralidad"""
        return tipo_institucion.upper() == 'FISCAL' and zona.upper() == 'RURAL'
    
    def evaluar_discapacidad(self, porcentaje: int, tiene_carnet: bool) -> bool:
        """Evalúa si aplica discapacidad"""
        return tiene_carnet and porcentaje >= 30
    
    def evaluar_pueblos_nacionalidades(self, autoidentificacion: str) -> bool:
        """Evalúa si pertenece a pueblos o nacionalidades"""
        grupos = ['INDIGENA', 'AFROECUATORIANO', 'MONTUBIO']
        return autoidentificacion.upper() in grupos
    
    def evaluar_merito_academico(self, cuadro_honor: str, distincion: Optional[str]) -> bool:
        """Evalúa si aplica mérito académico"""
        if cuadro_honor != 'SI':
            return False
        
        distinciones_merito = [
            'ABANDERADO PABELLON NACIONAL',
            'PORTA ESTANDARTE PLANTEL',
            '1er. ESCOLTA PABELLON NACIONAL'
        ]
        
        return distincion and distincion in distinciones_merito


# ==================== CALCULADOR DE SEGMENTOS (Single Responsibility) ====================

class CalculadorSegmento:
    """
    SINGLE RESPONSIBILITY: Solo calcula el segmento de asignación
    OPEN/CLOSED: Se pueden agregar nuevos segmentos sin modificar lógica existente
    """
    
    ORDEN_SEGMENTOS = [
        'CUOTAS',
        'VULNERABILIDAD',
        'MERITO_ACADEMICO',
        'RECONOCIMIENTOS',
        'PUEBLOS_NACIONALIDADES',
        'BACHILLERES',
        'GENERAL'
    ]
    
    def calcular(self, marcadores: Dict[str, str]) -> tuple[str, int]:
        """
        Calcula segmento y prioridad según marcadores
        Retorna: (segmento, prioridad)
        """
        # 1. CUOTAS (Prioridad 1)
        if self._tiene_cuotas(marcadores):
            return 'CUOTAS', 1
        
        # 2. VULNERABILIDAD (Prioridad 2)
        if marcadores.get('vulnerabilidad_socioeconomica') == 'SI':
            return 'VULNERABILIDAD', 2
        
        # 3. MÉRITO ACADÉMICO (Prioridad 3)
        if marcadores.get('merito_academico') == 'SI':
            return 'MERITO_ACADEMICO', 3
        
        # 5. PUEBLOS Y NACIONALIDADES (Prioridad 5)
        if marcadores.get('bachiller_pueblos_nacionalidad') == 'SI':
            return 'PUEBLOS_NACIONALIDADES', 5
        
        # 6. BACHILLERES (Prioridad 6)
        if marcadores.get('bachiller_periodo_academico') == 'SI':
            return 'BACHILLERES', 6
        
        # 7. POBLACIÓN GENERAL (Prioridad 7)
        return 'GENERAL', 7
    
    def _tiene_cuotas(self, marcadores: Dict[str, str]) -> bool:
        """Verifica si aplica para cuotas"""
        condiciones_cuotas = [
            marcadores.get('condicion_socioeconomica') == 'SI',
            marcadores.get('ruralidad') == 'SI',
            marcadores.get('discapacidad') == 'SI',
            marcadores.get('pueblos_nacionalidades') == 'SI',
            marcadores.get('victima_violencia') == 'SI',
            marcadores.get('migrantes_retornados') == 'SI'
        ]
        return any(condiciones_cuotas)


# ==================== CLASE PRINCIPAL (todos los principios SOLID) ====================

class PoliticaAccionAfirmativa(IAplicableCondicionSocial, IAplicableRuralidad, 
                               IAplicableDiscapacidad, ICalculableSegmento):
    """
    Política de Acción Afirmativa (PAA)
    
    SOLID APLICADO:
    - S: Responsabilidad única - gestionar datos de PAA
    - O: Abierto/Cerrado - se puede extender sin modificar
    - L: Liskov - puede sustituir a las interfaces que implementa
    - I: Interface Segregation - implementa interfaces específicas
    - D: Dependency Inversion - depende de abstracciones (EvaluadorCondicionesSociales, CalculadorSegmento)
    """
    
    _contador = 0
    
    def __init__(self, 
                 id_postulante: int, 
                 identificacion: str,
                 evaluador: EvaluadorCondicionesSociales,  # DEPENDENCY INJECTION
                 calculador: CalculadorSegmento):            # DEPENDENCY INJECTION
        
        PoliticaAccionAfirmativa._contador += 1
        
        self.id_postulante = id_postulante
        self.identificacion = identificacion
        
        # DEPENDENCY INVERSION: Depende de abstracciones
        self._evaluador = evaluador
        self._calculador = calculador
        
        # Marcaciones iniciales
        self.cupo_aceptado_historico_pc = 'NO'
        self.cupo_historico_activo = 'NO'
        self.numero_cupos_activos = 0
        
        # Condiciones sociales
        self._marcadores = {
            'condicion_socioeconomica': 'NO',
            'ruralidad': 'NO',
            'discapacidad': 'NO',
            'pueblos_nacionalidades': 'NO',
            'victima_violencia': 'NO',
            'migrantes_retornados': 'NO',
            'merito_academico': 'NO',
            'vulnerabilidad_socioeconomica': 'NO',
            'bachiller_pueblos_nacionalidad': 'NO',
            'bachiller_periodo_academico': 'NO',
            'poblacion_general': 'SI'
        }
        
        # Segmento asignado
        self.segmento_asignado = None
        self.prioridad_segmento = 99
        
        print(f"✓ PAA creada para postulante ID: {id_postulante}")
    
    def marcar_cupo_historico(self, tiene_cupo: bool, activo: bool = False) -> None:
        """Marca si tiene cupo aceptado histórico"""
        self.cupo_aceptado_historico_pc = 'SI' if tiene_cupo else 'NO'
        self.cupo_historico_activo = 'SI' if activo else 'NO'
        if activo:
            self.numero_cupos_activos += 1
        print(f"  Cupo histórico: {self.cupo_aceptado_historico_pc}")
    
    def aplicar_condicion_socioeconomica(self, quintil: int) -> None:
        """
        INTERFACE SEGREGATION: Implementa IAplicableCondicionSocial
        DEPENDENCY INVERSION: Usa EvaluadorCondicionesSociales
        """
        tiene_condicion, es_vulnerable = self._evaluador.evaluar_condicion_socioeconomica(quintil)
        
        if tiene_condicion:
            self._marcadores['condicion_socioeconomica'] = 'SI'
            if es_vulnerable:
                self._marcadores['vulnerabilidad_socioeconomica'] = 'SI'
                print(f"  Vulnerabilidad socioeconómica detectada (Quintil {quintil})")
        
        print(f"  Condición socioeconómica: Quintil {quintil}")
    
    def aplicar_ruralidad(self, tipo_institucion: str, zona: str) -> None:
        """
        INTERFACE SEGREGATION: Implementa IAplicableRuralidad
        DEPENDENCY INVERSION: Usa EvaluadorCondicionesSociales
        """
        if self._evaluador.evaluar_ruralidad(tipo_institucion, zona):
            self._marcadores['ruralidad'] = 'SI'
            print(f"  Ruralidad aplicada")
    
    def aplicar_discapacidad(self, porcentaje: int, tiene_carnet: bool) -> None:
        """
        INTERFACE SEGREGATION: Implementa IAplicableDiscapacidad
        DEPENDENCY INVERSION: Usa EvaluadorCondicionesSociales
        """
        if self._evaluador.evaluar_discapacidad(porcentaje, tiene_carnet):
            self._marcadores['discapacidad'] = 'SI'
            print(f"  Discapacidad aplicada: {porcentaje}%")
    
    def aplicar_pueblos_nacionalidades(self, autoidentificacion: str) -> None:
        """Aplica si pertenece a pueblos o nacionalidades"""
        if self._evaluador.evaluar_pueblos_nacionalidades(autoidentificacion):
            self._marcadores['pueblos_nacionalidades'] = 'SI'
            print(f"  Pueblos y nacionalidades: {autoidentificacion}")
    
    def aplicar_merito_academico(self, cuadro_honor: str, distincion: Optional[str] = None) -> None:
        """Aplica mérito académico"""
        if self._evaluador.evaluar_merito_academico(cuadro_honor, distincion):
            self._marcadores['merito_academico'] = 'SI'
            print(f"  Mérito académico: {distincion}")
    
    def aplicar_bachiller_ultimo_anio(self, es_bachiller: bool, 
                                     pertenece_pueblos: bool = False) -> None:
        """Aplica si está cursando último año de bachillerato"""
        if es_bachiller:
            self._marcadores['bachiller_periodo_academico'] = 'SI'
            if pertenece_pueblos:
                self._marcadores['bachiller_pueblos_nacionalidad'] = 'SI'
                print(f"  Bachiller de pueblos y nacionalidades")
            else:
                print(f"  Bachiller último año")
    
    def calcular_segmento(self) -> str:
        """
        INTERFACE SEGREGATION: Implementa ICalculableSegmento
        DEPENDENCY INVERSION: Usa CalculadorSegmento
        OPEN/CLOSED: Extensible sin modificar esta clase
        """
        self.segmento_asignado, self.prioridad_segmento = self._calculador.calcular(self._marcadores)
        
        print(f"  Segmento: {self.segmento_asignado} (Prioridad {self.prioridad_segmento})")
        return self.segmento_asignado
    
    def obtener_resumen(self) -> Dict:
        """Obtiene resumen de PAA y segmento"""
        return {
            'id_postulante': self.id_postulante,
            'segmento': self.segmento_asignado,
            'prioridad': self.prioridad_segmento,
            'vulnerabilidad': self._marcadores['vulnerabilidad_socioeconomica'],
            'merito': self._marcadores['merito_academico'],
            'pueblos': self._marcadores['pueblos_nacionalidades'],
            'discapacidad': self._marcadores['discapacidad'],
            'ruralidad': self._marcadores['ruralidad']
        }
    
    def __str__(self) -> str:
        return f"PAA(Postulante:{self.id_postulante}, Segmento:{self.segmento_asignado}, Prioridad:{self.prioridad_segmento})"
    
    @classmethod
    def obtener_total(cls) -> int:
        """Total de PAA creadas"""
        return cls._contador


# ==================== EJEMPLOS DE USO ====================

if __name__ == "__main__":
    print("=" * 80)
    print("POLÍTICA DE ACCIÓN AFIRMATIVA - APLICANDO PRINCIPIOS SOLID")
    print("=" * 80)
    
    # Crear servicios (DEPENDENCY INJECTION)
    evaluador = EvaluadorCondicionesSociales()
    calculador = CalculadorSegmento()
    
    # ===== CASO 1: Estudiante con mérito académico =====
    print("\n\n🎓 CASO 1: Estudiante con mérito académico")
    print("-" * 80)
    
    paa1 = PoliticaAccionAfirmativa(
        id_postulante=1,
        identificacion="1316202082",
        evaluador=evaluador,
        calculador=calculador
    )
    
    paa1.aplicar_merito_academico(
        cuadro_honor='SI',
        distincion='ABANDERADO PABELLON NACIONAL'
    )
    
    paa1.calcular_segmento()
    print(f"\nResumen: {paa1.obtener_resumen()}")
    
    # ===== CASO 2: Estudiante con vulnerabilidad =====
    print("\n\n🏘️ CASO 2: Estudiante con vulnerabilidad socioeconómica")
    print("-" * 80)
    
    paa2 = PoliticaAccionAfirmativa(
        id_postulante=2,
        identificacion="1350123456",
        evaluador=evaluador,
        calculador=calculador
    )
    
    paa2.aplicar_condicion_socioeconomica(quintil=1)  # Pobreza extrema
    paa2.aplicar_ruralidad(tipo_institucion='FISCAL', zona='RURAL')
    paa2.aplicar_pueblos_nacionalidades('MONTUBIO')
    
    paa2.calcular_segmento()
    print(f"\nResumen: {paa2.obtener_resumen()}")
    
    # ===== CASO 3: Población general =====
    print("\n\n👥 CASO 3: Población general")
    print("-" * 80)
    
    paa3 = PoliticaAccionAfirmativa(
        id_postulante=3,
        identificacion="1360234567",
        evaluador=evaluador,
        calculador=calculador
    )
    
    paa3.calcular_segmento()
    print(f"\nResumen: {paa3.obtener_resumen()}")
    
    # ===== CASO 4: Bachiller de pueblos y nacionalidades =====
    print("\n\n🌾 CASO 4: Bachiller de pueblos y nacionalidades")
    print("-" * 80)
    
    paa4 = PoliticaAccionAfirmativa(
        id_postulante=4,
        identificacion="1370345678",
        evaluador=evaluador,
        calculador=calculador
    )
    
    paa4.aplicar_pueblos_nacionalidades('INDIGENA')
    paa4.aplicar_bachiller_ultimo_anio(es_bachiller=True, pertenece_pueblos=True)
    
    paa4.calcular_segmento()
    print(f"\nResumen: {paa4.obtener_resumen()}")
    
    print(f"\n📊 Total PAA creadas: {PoliticaAccionAfirmativa.obtener_total()}")
    
    print("\n" + "=" * 80)
    print("PRINCIPIOS SOLID APLICADOS:")
    print("=" * 80)
    print("✅ S - Single Responsibility: Cada clase tiene UNA responsabilidad")
    print("   • PoliticaAccionAfirmativa: gestión de PAA")
    print("   • EvaluadorCondicionesSociales: evaluación de condiciones")
    print("   • CalculadorSegmento: cálculo de segmento")
    print()
    print("✅ O - Open/Closed: Extensible sin modificar código existente")
    print("   • Nuevas evaluaciones en EvaluadorCondicionesSociales")
    print("   • Nuevos segmentos en CalculadorSegmento")
    print()
    print("✅ L - Liskov Substitution: PAA sustituye a sus interfaces")
    print()
    print("✅ I - Interface Segregation: Interfaces específicas y pequeñas")
    print("   • IAplicableCondicionSocial, IAplicableRuralidad, etc.")
    print()
    print("✅ D - Dependency Inversion: Depende de abstracciones")
    print("   • PAA recibe EvaluadorCondicionesSociales y CalculadorSegmento")
    print("=" * 80)