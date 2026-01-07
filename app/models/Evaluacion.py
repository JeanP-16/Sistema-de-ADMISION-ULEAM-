"""
Módulo: Evaluacion aplicando PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
Fecha: Diciembre 2025

PRINCIPIOS SOLID APLICADOS (sin patrones de diseño específicos)
"""

from datetime import datetime
from typing import Optional, Dict
from abc import ABC, abstractmethod


# ==================== INTERFACES (Interface Segregation Principle) ====================

class IRegistrableNotas(ABC):
    """Interfaz específica para registro de notas"""
    @abstractmethod
    def registrar_notas(self, nota_examen: float, nota_entrevista: float, 
                       calificacion_colegio: float, **extras) -> None:
        pass


class ICalculablePuntaje(ABC):
    """Interfaz específica para cálculo de puntaje"""
    @abstractmethod
    def calcular_puntaje_total(self) -> float:
        pass


# ==================== CALCULADORA DE PUNTAJE (Single Responsibility) ====================

class CalculadoraPuntaje:
    """
    SINGLE RESPONSIBILITY: Solo calcula puntajes
    OPEN/CLOSED: Puede extenderse con nuevos métodos de cálculo sin modificar existentes
    """
    
    def calcular_puntaje_estandar(self, nota_examen: float, nota_entrevista: float,
                                  calificacion_colegio: float) -> float:
        """
        Cálculo estándar: 60% examen + 25% colegio + 15% entrevista
        """
        puntaje = (
            nota_examen * 0.60 +
            calificacion_colegio * 10 * 0.25 +
            nota_entrevista * 0.15
        )
        return round(puntaje, 2)
    
    def calcular_puntaje_con_merito(self, nota_examen: float, nota_entrevista: float,
                                    calificacion_colegio: float, cuadro_honor: bool = False) -> float:
        """
        Cálculo con mérito: 40% examen + 50% colegio + 10% entrevista + bonos
        """
        puntaje_base = (
            nota_examen * 0.40 +
            calificacion_colegio * 10 * 0.50 +
            nota_entrevista * 0.10
        )
        
        bono_cuadro_honor = 50 if cuadro_honor else 0
        bono_excelencia = 30 if calificacion_colegio >= 9.5 else 0
        
        return round(puntaje_base + bono_cuadro_honor + bono_excelencia, 2)
    
    def calcular_puntaje_inclusion(self, nota_examen: float, nota_entrevista: float,
                                   calificacion_colegio: float, 
                                   porcentaje_discapacidad: int = 0,
                                   pueblo_originario: bool = False,
                                   zona_rural: bool = False) -> float:
        """
        Cálculo inclusión: 50% examen + 20% colegio + 10% entrevista + factores sociales
        """
        puntaje_base = (
            nota_examen * 0.50 +
            calificacion_colegio * 10 * 0.20 +
            nota_entrevista * 0.10
        )
        
        bono_discapacidad = porcentaje_discapacidad * 2
        bono_etnico = 100 if pueblo_originario else 0
        bono_zona_rural = 50 if zona_rural else 0
        
        return round(puntaje_base + bono_discapacidad + bono_etnico + bono_zona_rural, 2)


# ==================== VALIDADOR DE NOTAS (Single Responsibility) ====================

class ValidadorNotas:
    """
    SINGLE RESPONSIBILITY: Solo valida notas ingresadas
    OPEN/CLOSED: Se pueden agregar nuevas validaciones sin modificar las existentes
    """
    
    def validar_nota_examen(self, nota: float) -> None:
        """Valida que la nota del examen esté en rango válido"""
        if not (0 <= nota <= 1000):
            raise ValueError(f"Nota de examen fuera de rango: {nota}")
    
    def validar_nota_entrevista(self, nota: float) -> None:
        """Valida que la nota de entrevista esté en rango válido"""
        if not (0 <= nota <= 100):
            raise ValueError(f"Nota de entrevista fuera de rango: {nota}")
    
    def validar_calificacion_colegio(self, calificacion: float) -> None:
        """Valida que la calificación del colegio esté en rango válido"""
        if not (0 <= calificacion <= 10):
            raise ValueError(f"Calificación de colegio fuera de rango: {calificacion}")
    
    def validar_todas_notas(self, nota_examen: float, nota_entrevista: float,
                           calificacion_colegio: float) -> None:
        """Valida todas las notas"""
        self.validar_nota_examen(nota_examen)
        self.validar_nota_entrevista(nota_entrevista)
        self.validar_calificacion_colegio(calificacion_colegio)


# ==================== CLASE PRINCIPAL (todos los principios SOLID) ====================

class Evaluacion(IRegistrableNotas, ICalculablePuntaje):
    """
    Evaluación de postulantes
    
    SOLID APLICADO:
    - S: Responsabilidad única - gestionar datos de evaluación
    - O: Abierto/Cerrado - se puede extender con nuevos tipos de cálculo
    - L: Liskov - puede sustituir a las interfaces que implementa
    - I: Interface Segregation - implementa interfaces específicas
    - D: Dependency Inversion - depende de abstracciones (CalculadoraPuntaje, ValidadorNotas)
    """
    
    ESTADOS_VALIDOS = ['PROGRAMADA', 'EN_CURSO', 'COMPLETADA', 'CANCELADA']
    TIPOS_EVALUACION = ['EXAMEN', 'ENTREVISTA', 'INTEGRAL']
    TIPOS_CALCULO = ['ESTANDAR', 'MERITO', 'INCLUSION']
    
    _contador_evaluaciones = 0
    
    def __init__(self,
                 id_inscripcion: int,
                 tipo_evaluacion: str,
                 tipo_calculo: str,
                 calculadora: CalculadoraPuntaje,  # DEPENDENCY INJECTION
                 validador: ValidadorNotas,         # DEPENDENCY INJECTION
                 fecha_programada: Optional[str] = None):
        
        Evaluacion._contador_evaluaciones += 1
        
        self.id_evaluacion = Evaluacion._contador_evaluaciones
        self.id_inscripcion = id_inscripcion
        self.tipo_evaluacion = tipo_evaluacion.upper()
        self.tipo_calculo = tipo_calculo.upper()
        
        # DEPENDENCY INVERSION: Depende de abstracciones
        self._calculadora = calculadora
        self._validador = validador
        
        if fecha_programada:
            self.fecha_programada = datetime.strptime(fecha_programada, '%Y-%m-%d')
        else:
            self.fecha_programada = datetime.now()
        
        self.fecha_realizacion = None
        self.estado = 'PROGRAMADA'
        
        # Notas
        self.nota_examen: Optional[float] = None
        self.nota_entrevista: Optional[float] = None
        self.calificacion_colegio: Optional[float] = None
        self.puntaje_total: Optional[float] = None
        
        # Extras
        self.extras: Dict = {}
        
        # Validaciones
        self._validar_tipo_evaluacion()
        self._validar_tipo_calculo()
        
        print(f"Evaluación creada: ID {self.id_evaluacion} - Tipo cálculo: {self.tipo_calculo}")
    
    def _validar_tipo_evaluacion(self) -> None:
        """Valida que el tipo de evaluación sea válido"""
        if self.tipo_evaluacion not in self.TIPOS_EVALUACION:
            raise ValueError(f"Tipo de evaluación inválido: {self.tipo_evaluacion}")
    
    def _validar_tipo_calculo(self) -> None:
        """Valida que el tipo de cálculo sea válido"""
        if self.tipo_calculo not in self.TIPOS_CALCULO:
            raise ValueError(f"Tipo de cálculo inválido: {self.tipo_calculo}")
    
    def registrar_notas(self, 
                       nota_examen: float,
                       nota_entrevista: float,
                       calificacion_colegio: float,
                       **extras) -> None:
        """
        INTERFACE SEGREGATION: Implementa IRegistrableNotas
        DEPENDENCY INVERSION: Usa ValidadorNotas para validar
        """
        # Validar usando el validador inyectado
        self._validador.validar_todas_notas(nota_examen, nota_entrevista, calificacion_colegio)
        
        self.nota_examen = nota_examen
        self.nota_entrevista = nota_entrevista
        self.calificacion_colegio = calificacion_colegio
        self.extras = extras
        
        print(f"\n[Notas Registradas] Evaluación {self.id_evaluacion}:")
        print(f"  Examen: {nota_examen}/1000")
        print(f"  Entrevista: {nota_entrevista}/100")
        print(f"  Colegio: {calificacion_colegio}/10")
        if extras:
            print(f"  Extras: {extras}")
    
    def calcular_puntaje_total(self) -> float:
        """
        INTERFACE SEGREGATION: Implementa ICalculablePuntaje
        DEPENDENCY INVERSION: Usa CalculadoraPuntaje para calcular
        OPEN/CLOSED: Extensible agregando nuevos tipos de cálculo
        """
        if self.nota_examen is None:
            raise ValueError("Debe registrar notas antes de calcular puntaje")
        
        print(f"\n[Calculando Puntaje] Tipo: {self.tipo_calculo}")
        
        # Delegar cálculo a la calculadora según el tipo
        if self.tipo_calculo == 'ESTANDAR':
            self.puntaje_total = self._calculadora.calcular_puntaje_estandar(
                self.nota_examen,
                self.nota_entrevista,
                self.calificacion_colegio
            )
        
        elif self.tipo_calculo == 'MERITO':
            self.puntaje_total = self._calculadora.calcular_puntaje_con_merito(
                self.nota_examen,
                self.nota_entrevista,
                self.calificacion_colegio,
                self.extras.get('cuadro_honor', False)
            )
        
        elif self.tipo_calculo == 'INCLUSION':
            self.puntaje_total = self._calculadora.calcular_puntaje_inclusion(
                self.nota_examen,
                self.nota_entrevista,
                self.calificacion_colegio,
                self.extras.get('porcentaje_discapacidad', 0),
                self.extras.get('pueblo_originario', False),
                self.extras.get('zona_rural', False)
            )
        
        self.estado = 'COMPLETADA'
        self.fecha_realizacion = datetime.now()
        
        print(f"  PUNTAJE FINAL: {self.puntaje_total}")
        return self.puntaje_total
    
    def obtener_resultado(self) -> Dict:
        """Retorna el resultado completo de la evaluación"""
        return {
            'id_evaluacion': self.id_evaluacion,
            'id_inscripcion': self.id_inscripcion,
            'tipo_evaluacion': self.tipo_evaluacion,
            'tipo_calculo': self.tipo_calculo,
            'nota_examen': self.nota_examen,
            'nota_entrevista': self.nota_entrevista,
            'calificacion_colegio': self.calificacion_colegio,
            'puntaje_total': self.puntaje_total,
            'estado': self.estado,
            'fecha_realizacion': self.fecha_realizacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_realizacion else None
        }
    
    def __str__(self) -> str:
        return f"Evaluacion(ID:{self.id_evaluacion}, Tipo:{self.tipo_calculo}, Puntaje:{self.puntaje_total})"


# ==================== EJEMPLOS DE USO ====================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("EVALUACION - APLICANDO PRINCIPIOS SOLID (SIN PATRONES)")
    print("=" * 80)
    
    # Crear servicios (DEPENDENCY INJECTION)
    calculadora = CalculadoraPuntaje()
    validador = ValidadorNotas()
    
    # ===== EJEMPLO 1: Evaluación ESTÁNDAR =====
    print("\n\nEJEMPLO 1: Evaluación con Cálculo ESTÁNDAR")
    print("-" * 80)
    
    eval1 = Evaluacion(
        id_inscripcion=1,
        tipo_evaluacion='INTEGRAL',
        tipo_calculo='ESTANDAR',
        calculadora=calculadora,
        validador=validador
    )
    
    eval1.registrar_notas(
        nota_examen=800,
        nota_entrevista=85,
        calificacion_colegio=9.0
    )
    
    puntaje1 = eval1.calcular_puntaje_total()
    print(f" {eval1}")
    
    # ===== EJEMPLO 2: Evaluación MÉRITO =====
    print("\n\nEJEMPLO 2: Evaluación con Cálculo MÉRITO ACADÉMICO")
    print("-" * 80)
    
    eval2 = Evaluacion(
        id_inscripcion=2,
        tipo_evaluacion='INTEGRAL',
        tipo_calculo='MERITO',
        calculadora=calculadora,
        validador=validador
    )
    
    eval2.registrar_notas(
        nota_examen=750,
        nota_entrevista=80,
        calificacion_colegio=9.8,
        cuadro_honor=True
    )
    
    puntaje2 = eval2.calcular_puntaje_total()
    print(f" {eval2}")
    
    # ===== EJEMPLO 3: Evaluación INCLUSIÓN =====
    print("\n\nEJEMPLO 3: Evaluación con Cálculo INCLUSIÓN SOCIAL")
    print("-" * 80)
    
    eval3 = Evaluacion(
        id_inscripcion=3,
        tipo_evaluacion='INTEGRAL',
        tipo_calculo='INCLUSION',
        calculadora=calculadora,
        validador=validador
    )
    
    eval3.registrar_notas(
        nota_examen=650,
        nota_entrevista=75,
        calificacion_colegio=8.5,
        porcentaje_discapacidad=40,
        pueblo_originario=True,
        zona_rural=True
    )
    
    puntaje3 = eval3.calcular_puntaje_total()
    print(f" {eval3}")
    
    # ===== EJEMPLO 4: Comparación de tipos de cálculo =====
    print("\n\nEJEMPLO 4: Comparación - Mismas notas, diferentes tipos de cálculo")
    print("-" * 80)
    
    notas_base = {
        'nota_examen': 750,
        'nota_entrevista': 85,
        'calificacion_colegio': 9.0
    }
    
    # Crear 3 evaluaciones con el mismo postulante
    eval_est = Evaluacion(4, 'INTEGRAL', 'ESTANDAR', calculadora, validador)
    eval_est.registrar_notas(**notas_base)
    p_est = eval_est.calcular_puntaje_total()
    
    eval_mer = Evaluacion(4, 'INTEGRAL', 'MERITO', calculadora, validador)
    eval_mer.registrar_notas(**notas_base, cuadro_honor=True)
    p_mer = eval_mer.calcular_puntaje_total()
    
    eval_inc = Evaluacion(4, 'INTEGRAL', 'INCLUSION', calculadora, validador)
    eval_inc.registrar_notas(**notas_base, porcentaje_discapacidad=30)
    p_inc = eval_inc.calcular_puntaje_total()
    
    print("\nRESULTADOS:")
    print(f"  ESTANDAR:  {p_est} puntos")
    print(f"  MERITO:    {p_mer} puntos")
    print(f"  INCLUSION: {p_inc} puntos")
    
    # ===== EJEMPLO 5: Validación de errores =====
    print("\n\nEJEMPLO 5: Validación de notas incorrectas")
    print("-" * 80)
    
    try:
        eval_error = Evaluacion(5, 'INTEGRAL', 'ESTANDAR', calculadora, validador)
        eval_error.registrar_notas(
            nota_examen=1200,  # Fuera de rango
            nota_entrevista=85,
            calificacion_colegio=9.0
        )
    except ValueError as e:
        print(f" ERROR CAPTURADO: {e}")
    
    print("\n" + "=" * 80)
    print("PRINCIPIOS SOLID APLICADOS:")
    print("=" * 80)
    print(" S - Single Responsibility: Cada clase tiene UNA responsabilidad")
    print("   • Evaluacion: gestión de evaluación")
    print("   • CalculadoraPuntaje: cálculo de puntajes")
    print("   • ValidadorNotas: validación de notas")
    print()
    print(" O - Open/Closed: Extensible sin modificar código existente")
    print("   • Nuevos tipos de cálculo se agregan en CalculadoraPuntaje")
    print("   • Nuevas validaciones se agregan en ValidadorNotas")
    print()
    print(" L - Liskov Substitution: Evaluacion sustituye a sus interfaces")
    print()
    print(" I - Interface Segregation: Interfaces específicas y pequeñas")
    print("   • IRegistrableNotas, ICalculablePuntaje")
    print()
    print(" D - Dependency Inversion: Depende de abstracciones")
    print("   • Evaluacion recibe CalculadoraPuntaje y ValidadorNotas")
    print("=" * 80)
