"""
Módulo: PuntajePostulacion aplicando PRINCIPIOS SOLID
Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
Fecha: Diciembre 2025

PRINCIPIOS SOLID APLICADOS (sin patrones de diseño específicos)
"""

from datetime import datetime
from typing import Optional, Dict


# ==================== INTERFACES (Interface Segregation Principle) ====================

class IValidableNotas:
    """Interfaz específica para validación de notas"""
    def validar_nota_grado(self, nota: float) -> None:
        pass
    
    def validar_puntaje(self, puntaje: float) -> None:
        pass


class ICalculablePuntajeTotal:
    """Interfaz específica para cálculo de puntaje total"""
    def calcular_puntaje_total(self) -> float:
        pass


# ==================== VALIDADOR DE NOTAS (Single Responsibility) ====================

class ValidadorNotasPuntaje:
    """
    SINGLE RESPONSIBILITY: Solo valida notas y puntajes
    OPEN/CLOSED: Se pueden agregar nuevas validaciones sin modificar existentes
    """
    
    NOTA_MINIMA = 0.0
    NOTA_MAXIMA = 10.0
    PUNTAJE_MINIMO = 0.0
    PUNTAJE_MAXIMO = 1000.0
    
    def validar_nota_grado(self, nota: float) -> None:
        """Valida que la nota de grado esté en rango válido"""
        if not (self.NOTA_MINIMA <= nota <= self.NOTA_MAXIMA):
            raise ValueError(f"La nota de grado debe estar entre {self.NOTA_MINIMA} y {self.NOTA_MAXIMA}")
    
    def validar_puntaje(self, puntaje: float, tipo: str) -> None:
        """Valida que el puntaje esté en rango válido"""
        if not (self.PUNTAJE_MINIMO <= puntaje <= self.PUNTAJE_MAXIMO):
            raise ValueError(f"El puntaje de {tipo} debe estar entre {self.PUNTAJE_MINIMO} y {self.PUNTAJE_MAXIMO}")


# ==================== CALCULADOR DE PUNTAJE (Single Responsibility) ====================

class CalculadorPuntajePostulacion:
    """
    SINGLE RESPONSIBILITY: Solo calcula el puntaje final
    OPEN/CLOSED: Se pueden agregar nuevos tipos de cálculo sin modificar existentes
    """
    
    PESO_NOTA_GRADO = 0.30
    PESO_EVALUACION = 0.50
    PESO_MERITO = 0.20
    PUNTAJE_MAXIMO = 1000
    FACTOR_NORMALIZACION_NOTA = 100
    
    def calcular_puntaje_total(self, 
                              nota_grado: float,
                              puntaje_evaluacion: float,
                              puntaje_meritos: float) -> float:
        """
        Calcula el puntaje total según normativa SENESCYT
        """
        # Normalizar nota de grado (0-10 → 0-1000)
        puntaje_grado_normalizado = nota_grado * self.FACTOR_NORMALIZACION_NOTA
        
        # Calcular componentes ponderados
        componente_grado = puntaje_grado_normalizado * self.PESO_NOTA_GRADO
        componente_evaluacion = puntaje_evaluacion * self.PESO_EVALUACION
        componente_meritos = puntaje_meritos * self.PESO_MERITO
        
        # Sumar y limitar al máximo
        puntaje_total = componente_grado + componente_evaluacion + componente_meritos
        puntaje_total = min(puntaje_total, self.PUNTAJE_MAXIMO)
        
        return round(puntaje_total, 2)
    
    def calcular_desglose(self,
                         nota_grado: float,
                         puntaje_evaluacion: float,
                         puntaje_meritos: float) -> Dict[str, float]:
        """
        Calcula el desglose detallado de componentes
        """
        puntaje_grado_norm = nota_grado * self.FACTOR_NORMALIZACION_NOTA
        
        return {
            'nota_grado_original': nota_grado,
            'nota_grado_normalizada': puntaje_grado_norm,
            'componente_grado': puntaje_grado_norm * self.PESO_NOTA_GRADO,
            'componente_evaluacion': puntaje_evaluacion * self.PESO_EVALUACION,
            'componente_meritos': puntaje_meritos * self.PESO_MERITO,
            'puntaje_final': self.calcular_puntaje_total(nota_grado, puntaje_evaluacion, puntaje_meritos)
        }


# ==================== FORMATEADOR DE SALIDA (Single Responsibility) ====================

class FormateadorSalidaPuntaje:
    """
    SINGLE RESPONSIBILITY: Solo formatea la salida de información
    OPEN/CLOSED: Se pueden agregar nuevos formatos sin modificar existentes
    """
    
    def mostrar_desglose(self, desglose: Dict[str, float], pesos: Dict[str, float]) -> None:
        """Muestra el desglose de puntaje formateado"""
        print("\n" + "=" * 60)
        print("DESGLOSE DE PUNTAJE")
        print("=" * 60)
        
        print(f"1. Nota de Grado ({int(pesos['grado']*100)}%):")
        print(f"   Nota: {desglose['nota_grado_original']}/10")
        print(f"   Normalizado: {desglose['nota_grado_normalizada']}/1000")
        print(f"   Ponderado: {desglose['componente_grado']:.2f} puntos")
        print()
        print(f"2. Evaluación de Aptitudes ({int(pesos['evaluacion']*100)}%):")
        print(f"   Puntaje: {desglose['componente_evaluacion']/pesos['evaluacion']:.2f}/1000")
        print(f"   Ponderado: {desglose['componente_evaluacion']:.2f} puntos")
        print()
        print(f"3. Méritos Adicionales ({int(pesos['merito']*100)}%):")
        print(f"   Puntaje: {desglose['componente_meritos']/pesos['merito']:.2f}/1000")
        print(f"   Ponderado: {desglose['componente_meritos']:.2f} puntos")
        print()
        print("=" * 60)
        print(f"PUNTAJE FINAL: {desglose['puntaje_final']}/1000 puntos")
        print("=" * 60)
    
    def mostrar_informacion(self, puntaje_obj) -> None:
        """Muestra la información completa del puntaje"""
        print("\n" + "=" * 60)
        print(f"PUNTAJE POSTULACIÓN ID: {puntaje_obj.id_puntaje}")
        print("=" * 60)
        print(f"Cédula Postulante: {puntaje_obj.cedula_postulante}")
        print(f"Postulante ID: {puntaje_obj.id_postulante}")
        print(f"Fecha cálculo: {puntaje_obj.fecha_calculo.strftime('%d/%m/%Y %H:%M')}")
        print(f"\nCOMPONENTES:")
        print(f"  Nota de Grado: {puntaje_obj.nota_grado}/10")
        print(f"  Evaluación: {puntaje_obj.puntaje_evaluacion}/1000")
        print(f"  Méritos: {puntaje_obj.puntaje_meritos}/1000")
        print(f"\nPUNTAJE FINAL: {puntaje_obj.puntaje_final}/1000")
        if puntaje_obj.observaciones:
            print(f"\nObservaciones: {puntaje_obj.observaciones}")
        print("=" * 60)


# ==================== CLASE PRINCIPAL (todos los principios SOLID) ====================

class PuntajePostulacion(IValidableNotas, ICalculablePuntajeTotal):
    """
    Puntaje de Postulación
    
    SOLID APLICADO:
    - S: Responsabilidad única - gestionar datos de puntaje
    - O: Abierto/Cerrado - se puede extender sin modificar
    - L: Liskov - puede sustituir a las interfaces que implementa
    - I: Interface Segregation - implementa interfaces específicas
    - D: Dependency Inversion - depende de abstracciones (ValidadorNotasPuntaje, CalculadorPuntajePostulacion)
    """
    
    _contador_puntajes = 0
    
    def __init__(self,
                 id_postulante: int,
                 nota_grado: float,
                 puntaje_evaluacion: float,
                 cedula_postulante: str,
                 validador: ValidadorNotasPuntaje,           # DEPENDENCY INJECTION
                 calculador: CalculadorPuntajePostulacion,   # DEPENDENCY INJECTION
                 formateador: FormateadorSalidaPuntaje,      # DEPENDENCY INJECTION
                 puntaje_meritos: float = 0.0):
        
        PuntajePostulacion._contador_puntajes += 1
        
        self.id_puntaje = PuntajePostulacion._contador_puntajes
        self.id_postulante = id_postulante
        self.cedula_postulante = cedula_postulante
        
        # DEPENDENCY INVERSION: Depende de abstracciones
        self._validador = validador
        self._calculador = calculador
        self._formateador = formateador
        
        # Validar y asignar notas
        self._validador.validar_nota_grado(nota_grado)
        self._validador.validar_puntaje(puntaje_evaluacion, "evaluación")
        self._validador.validar_puntaje(puntaje_meritos, "méritos")
        
        self._nota_grado = nota_grado
        self._puntaje_evaluacion = puntaje_evaluacion
        self._puntaje_meritos = puntaje_meritos
        
        self.fecha_calculo = datetime.now()
        self._puntaje_final = self._calculador.calcular_puntaje_total(
            self._nota_grado,
            self._puntaje_evaluacion,
            self._puntaje_meritos
        )
        self.observaciones = None
        
        print(f"✓ Puntaje calculado: {self._puntaje_final}/1000 pts")
    
    # PROPIEDADES (ENCAPSULAMIENTO)
    @property
    def nota_grado(self) -> float:
        """Getter para nota de grado"""
        return self._nota_grado
    
    @property
    def puntaje_evaluacion(self) -> float:
        """Getter para puntaje de evaluación"""
        return self._puntaje_evaluacion
    
    @property
    def puntaje_meritos(self) -> float:
        """Getter para puntaje de méritos"""
        return self._puntaje_meritos
    
    @property
    def puntaje_final(self) -> float:
        """Getter para puntaje final"""
        return self._puntaje_final
    
    @puntaje_meritos.setter
    def puntaje_meritos(self, valor: float) -> None:
        """
        Setter para actualizar méritos y recalcular
        DEPENDENCY INVERSION: Usa validador y calculador
        """
        self._validador.validar_puntaje(valor, "méritos")
        self._puntaje_meritos = valor
        self._puntaje_final = self._calculador.calcular_puntaje_total(
            self._nota_grado,
            self._puntaje_evaluacion,
            self._puntaje_meritos
        )
        print(f"  Méritos actualizados. Nuevo puntaje: {self._puntaje_final}/1000")
    
    def calcular_puntaje_total(self) -> float:
        """
        INTERFACE SEGREGATION: Implementa ICalculablePuntajeTotal
        DEPENDENCY INVERSION: Usa CalculadorPuntajePostulacion
        """
        return self._calculador.calcular_puntaje_total(
            self._nota_grado,
            self._puntaje_evaluacion,
            self._puntaje_meritos
        )
    
    def mostrar_desglose(self) -> None:
        """
        DEPENDENCY INVERSION: Usa CalculadorPuntajePostulacion y FormateadorSalidaPuntaje
        """
        desglose = self._calculador.calcular_desglose(
            self._nota_grado,
            self._puntaje_evaluacion,
            self._puntaje_meritos
        )
        
        pesos = {
            'grado': self._calculador.PESO_NOTA_GRADO,
            'evaluacion': self._calculador.PESO_EVALUACION,
            'merito': self._calculador.PESO_MERITO
        }
        
        self._formateador.mostrar_desglose(desglose, pesos)
    
    def agregar_observaciones(self, texto: str) -> None:
        """Agrega observaciones al puntaje"""
        self.observaciones = texto
    
    def mostrar_info(self) -> None:
        """
        DEPENDENCY INVERSION: Usa FormateadorSalidaPuntaje
        """
        self._formateador.mostrar_informacion(self)
    
    def __str__(self) -> str:
        return f"PuntajePostulacion(ID:{self.id_puntaje}, Postulante:{self.id_postulante}, Puntaje:{self.puntaje_final})"
    
    @classmethod
    def obtener_total(cls) -> int:
        """Total de puntajes creados"""
        return cls._contador_puntajes


# ==================== EJEMPLOS DE USO ====================

if __name__ == "__main__":
    print("=" * 80)
    print("PUNTAJE POSTULACIÓN - APLICANDO PRINCIPIOS SOLID")
    print("=" * 80)
    
    # Crear servicios (DEPENDENCY INJECTION)
    validador = ValidadorNotasPuntaje()
    calculador = CalculadorPuntajePostulacion()
    formateador = FormateadorSalidaPuntaje()
    
    # ===== EJEMPLO 1: Puntaje con mérito alto =====
    print("\n\n EJEMPLO 1: Estudiante con alto rendimiento")
    print("-" * 80)
    
    puntaje1 = PuntajePostulacion(
        id_postulante=1,
        nota_grado=9.5,
        puntaje_evaluacion=850,
        cedula_postulante="1316202082",
        validador=validador,
        calculador=calculador,
        formateador=formateador,
        puntaje_meritos=200
    )
    
    puntaje1.mostrar_info()
    puntaje1.mostrar_desglose()
    
    # ===== EJEMPLO 2: Puntaje sin méritos =====
    print("\n\n EJEMPLO 2: Estudiante sin méritos adicionales")
    print("-" * 80)
    
    puntaje2 = PuntajePostulacion(
        id_postulante=2,
        nota_grado=8.0,
        puntaje_evaluacion=700,
        cedula_postulante="1350123456",
        validador=validador,
        calculador=calculador,
        formateador=formateador
    )
    
    puntaje2.agregar_observaciones("Postulante sin méritos adicionales")
    puntaje2.mostrar_info()
    
    # ===== EJEMPLO 3: Actualización de méritos =====
    print("\n\n EJEMPLO 3: Actualización de méritos")
    print("-" * 80)
    
    puntaje3 = PuntajePostulacion(
        id_postulante=3,
        nota_grado=9.0,
        puntaje_evaluacion=800,
        cedula_postulante="1360234567",
        validador=validador,
        calculador=calculador,
        formateador=formateador,
        puntaje_meritos=100
    )
    
    print(f"\nPuntaje inicial: {puntaje3.puntaje_final}")
    
    # Actualizar méritos usando setter
    print("\nActualizando méritos de 100 a 250...")
    puntaje3.puntaje_meritos = 250
    
    print(f"Puntaje final: {puntaje3.puntaje_final}")
    puntaje3.mostrar_desglose()
    
    # ===== EJEMPLO 4: Validación de errores =====
    print("\n\n EJEMPLO 4: Validación de nota inválida")
    print("-" * 80)
    
    try:
        puntaje_error = PuntajePostulacion(
            id_postulante=4,
            nota_grado=11.5,  # Fuera de rango
            puntaje_evaluacion=800,
            cedula_postulante="1370345678",
            validador=validador,
            calculador=calculador,
            formateador=formateador
        )
    except ValueError as e:
        print(f"ERROR CAPTURADO: {e}")
    
    print(f"\n Total puntajes creados: {PuntajePostulacion.obtener_total()}")
    
    print("\n" + "=" * 80)
    print("PRINCIPIOS SOLID APLICADOS:")
    print("=" * 80)
    print(" S - Single Responsibility: Cada clase tiene UNA responsabilidad")
    print("   • PuntajePostulacion: gestión de puntaje")
    print("   • ValidadorNotasPuntaje: validación de notas")
    print("   • CalculadorPuntajePostulacion: cálculo de puntaje")
    print("   • FormateadorSalidaPuntaje: formateo de salida")
    print()
    print(" O - Open/Closed: Extensible sin modificar código existente")
    print("   • Nuevas validaciones en ValidadorNotasPuntaje")
    print("   • Nuevos cálculos en CalculadorPuntajePostulacion")
    print("   • Nuevos formatos en FormateadorSalidaPuntaje")
    print()
    print(" L - Liskov Substitution: PuntajePostulacion sustituye a sus interfaces")
    print()
    print(" I - Interface Segregation: Interfaces específicas y pequeñas")
    print("   • IValidableNotas, ICalculablePuntajeTotal")
    print()
    print(" D - Dependency Inversion: Depende de abstracciones")
    print("   • PuntajePostulacion recibe Validador, Calculador y Formateador")
    print("=" * 80) 
