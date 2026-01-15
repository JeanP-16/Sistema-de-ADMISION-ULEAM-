/**
 * Módulo: PuntajePostulacion con PATRÓN TEMPLATE METHOD
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: TEMPLATE METHOD (Comportamiento)
 * ¿Por qué? El cálculo de puntaje sigue pasos fijos, pero algunos pasos pueden variar
 */

// Encapsulación para evitar conflictos de nombres globales
(function() {

// ==================== PATRÓN TEMPLATE METHOD ====================

abstract class CalculadorPuntajeBase {
    /**
     * PATRÓN TEMPLATE METHOD
     * Define el esqueleto del algoritmo, los pasos específicos se implementan en subclases
     */
    
    protected readonly PUNTAJE_MAXIMO = 1000;
    
    // TEMPLATE METHOD: Define la estructura del algoritmo
    calcularPuntajeFinal(notaGrado: number, puntajeEvaluacion: number, puntajeMeritos: number): number {
        // Paso 1: Validar (puede variar según tipo)
        this.validarEntradas(notaGrado, puntajeEvaluacion, puntajeMeritos);
        
        // Paso 2: Normalizar nota de grado (puede variar)
        const notaNormalizada = this.normalizarNotaGrado(notaGrado);
        
        // Paso 3: Aplicar ponderaciones (varía según tipo)
        const componentes = this.aplicarPonderaciones(notaNormalizada, puntajeEvaluacion, puntajeMeritos);
        
        // Paso 4: Calcular bonificaciones (varía según tipo)
        const bonificacion = this.calcularBonificaciones(puntajeMeritos);
        
        // Paso 5: Sumar y limitar (fijo)
        const total = componentes.grado + componentes.evaluacion + componentes.meritos + bonificacion;
        const puntajeFinal = Math.min(total, this.PUNTAJE_MAXIMO);
        
        // Paso 6: Redondear (fijo)
        return Math.round(puntajeFinal * 100) / 100;
    }
    
    // Métodos abstractos (deben implementarse en subclases)
    protected abstract validarEntradas(notaGrado: number, puntajeEval: number, puntajeMer: number): void;
    protected abstract normalizarNotaGrado(nota: number): number;
    protected abstract aplicarPonderaciones(notaNorm: number, puntajeEval: number, puntajeMer: number): {
        grado: number;
        evaluacion: number;
        meritos: number;
    };
    protected abstract calcularBonificaciones(puntajeMeritos: number): number;
    
    // Hook (método opcional que las subclases pueden sobrescribir)
    protected logCalculation(mensaje: string): void {
        // Por defecto no hace nada, pero puede sobrescribirse
    }
}

// ==================== IMPLEMENTACIONES CONCRETAS ====================

class CalculadorPuntajeEstandar extends CalculadorPuntajeBase {
    /**
     * IMPLEMENTACIÓN ESTÁNDAR: 30% grado + 50% evaluación + 20% méritos
     */
    
    private readonly PESO_GRADO = 0.30;
    private readonly PESO_EVALUACION = 0.50;
    private readonly PESO_MERITOS = 0.20;
    private readonly FACTOR_NORMALIZACION = 100;
    
    protected validarEntradas(notaGrado: number, puntajeEval: number, puntajeMer: number): void {
        if (notaGrado < 0 || notaGrado > 10) {
            throw new Error(`Nota de grado debe estar entre 0 y 10`);
        }
        if (puntajeEval < 0 || puntajeEval > this.PUNTAJE_MAXIMO) {
            throw new Error(`Puntaje de evaluación debe estar entre 0 y ${this.PUNTAJE_MAXIMO}`);
        }
        if (puntajeMer < 0 || puntajeMer > this.PUNTAJE_MAXIMO) {
            throw new Error(`Puntaje de méritos debe estar entre 0 y ${this.PUNTAJE_MAXIMO}`);
        }
    }
    
    protected normalizarNotaGrado(nota: number): number {
        return nota * this.FACTOR_NORMALIZACION;
    }
    
    protected aplicarPonderaciones(notaNorm: number, puntajeEval: number, puntajeMer: number) {
        return {
            grado: notaNorm * this.PESO_GRADO,
            evaluacion: puntajeEval * this.PESO_EVALUACION,
            meritos: puntajeMer * this.PESO_MERITOS
        };
    }
    
    protected calcularBonificaciones(puntajeMeritos: number): number {
        // Estándar no tiene bonificaciones adicionales
        return 0;
    }
    
    protected logCalculation(mensaje: string): void {
        console.log(`  [Estándar] ${mensaje}`);
    }
    
    obtenerNombre(): string {
        return "ESTANDAR";
    }
}

class CalculadorPuntajeConMerito extends CalculadorPuntajeBase {
    /**
     * CON MÉRITO: 25% grado + 45% evaluación + 30% méritos + bonificaciones
     */
    
    private readonly PESO_GRADO = 0.25;
    private readonly PESO_EVALUACION = 0.45;
    private readonly PESO_MERITOS = 0.30;
    private readonly FACTOR_NORMALIZACION = 100;
    private readonly BONIFICACION_ALTO_MERITO = 50;  // Bono si méritos > 700
    
    protected validarEntradas(notaGrado: number, puntajeEval: number, puntajeMer: number): void {
        if (notaGrado < 0 || notaGrado > 10) {
            throw new Error(`Nota de grado debe estar entre 0 y 10`);
        }
        if (puntajeEval < 0 || puntajeEval > this.PUNTAJE_MAXIMO) {
            throw new Error(`Puntaje de evaluación debe estar entre 0 y ${this.PUNTAJE_MAXIMO}`);
        }
        if (puntajeMer < 0 || puntajeMer > this.PUNTAJE_MAXIMO) {
            throw new Error(`Puntaje de méritos debe estar entre 0 y ${this.PUNTAJE_MAXIMO}`);
        }
    }
    
    protected normalizarNotaGrado(nota: number): number {
        return nota * this.FACTOR_NORMALIZACION;
    }
    
    protected aplicarPonderaciones(notaNorm: number, puntajeEval: number, puntajeMer: number) {
        return {
            grado: notaNorm * this.PESO_GRADO,
            evaluacion: puntajeEval * this.PESO_EVALUACION,
            meritos: puntajeMer * this.PESO_MERITOS
        };
    }
    
    protected calcularBonificaciones(puntajeMeritos: number): number {
        // Bonificación si tiene alto mérito
        if (puntajeMeritos > 700) {
            this.logCalculation(`Bonificación por alto mérito: +${this.BONIFICACION_ALTO_MERITO}`);
            return this.BONIFICACION_ALTO_MERITO;
        }
        return 0;
    }
    
    protected logCalculation(mensaje: string): void {
        console.log(`  [Con Mérito] ${mensaje}`);
    }
    
    obtenerNombre(): string {
        return "CON_MERITO";
    }
}

class CalculadorPuntajeInclusion extends CalculadorPuntajeBase {
    /**
     * INCLUSIÓN: 20% grado + 40% evaluación + 40% méritos/factores sociales
     */
    
    private readonly PESO_GRADO = 0.20;
    private readonly PESO_EVALUACION = 0.40;
    private readonly PESO_MERITOS = 0.40;
    private readonly FACTOR_NORMALIZACION = 100;
    private readonly BONIFICACION_INCLUSION = 100;  // Bono inclusión
    
    protected validarEntradas(notaGrado: number, puntajeEval: number, puntajeMer: number): void {
        if (notaGrado < 0 || notaGrado > 10) {
            throw new Error(`Nota de grado debe estar entre 0 y 10`);
        }
        if (puntajeEval < 0 || puntajeEval > this.PUNTAJE_MAXIMO) {
            throw new Error(`Puntaje de evaluación debe estar entre 0 y ${this.PUNTAJE_MAXIMO}`);
        }
        if (puntajeMer < 0 || puntajeMer > this.PUNTAJE_MAXIMO) {
            throw new Error(`Puntaje de méritos debe estar entre 0 y ${this.PUNTAJE_MAXIMO}`);
        }
    }
    
    protected normalizarNotaGrado(nota: number): number {
        return nota * this.FACTOR_NORMALIZACION;
    }
    
    protected aplicarPonderaciones(notaNorm: number, puntajeEval: number, puntajeMer: number) {
        return {
            grado: notaNorm * this.PESO_GRADO,
            evaluacion: puntajeEval * this.PESO_EVALUACION,
            meritos: puntajeMer * this.PESO_MERITOS
        };
    }
    
    protected calcularBonificaciones(puntajeMeritos: number): number {
        // Siempre aplica bonificación de inclusión
        this.logCalculation(`Bonificación por inclusión: +${this.BONIFICACION_INCLUSION}`);
        return this.BONIFICACION_INCLUSION;
    }
    
    protected logCalculation(mensaje: string): void {
        console.log(`  [Inclusión] ${mensaje}`);
    }
    
    obtenerNombre(): string {
        return "INCLUSION";
    }
}

// ==================== CLASE PRINCIPAL ====================

class PuntajePostulacion {
    private static _contadorPuntajes: number = 0;
    
    idPuntaje: number;
    idPostulante: number;
    cedulaPostulante: string;
    
    private _notaGrado: number;
    private _puntajeEvaluacion: number;
    private _puntajeMeritos: number;
    private _puntajeFinal: number;
    
    fechaCalculo: Date;
    observaciones: string | null = null;
    
    // TEMPLATE METHOD: Calculador inyectado
    private _calculador: CalculadorPuntajeBase;
    
    constructor(
        idPostulante: number,
        notaGrado: number,
        puntajeEvaluacion: number,
        cedulaPostulante: string,
        calculador: CalculadorPuntajeBase,  // DEPENDENCY INJECTION del calculador
        puntajeMeritos: number = 0.0
    ) {
        PuntajePostulacion._contadorPuntajes++;
        
        this.idPuntaje = PuntajePostulacion._contadorPuntajes;
        this.idPostulante = idPostulante;
        this.cedulaPostulante = cedulaPostulante;
        this._calculador = calculador;
        
        this._notaGrado = notaGrado;
        this._puntajeEvaluacion = puntajeEvaluacion;
        this._puntajeMeritos = puntajeMeritos;
        
        this.fechaCalculo = new Date();
        
        // Usar TEMPLATE METHOD para calcular
        this._puntajeFinal = this._calculador.calcularPuntajeFinal(
            this._notaGrado,
            this._puntajeEvaluacion,
            this._puntajeMeritos
        );
        
        console.log(`Puntaje calculado: ${this._puntajeFinal}/1000 pts`);
    }
    
    // Getters
    get notaGrado(): number { return this._notaGrado; }
    get puntajeEvaluacion(): number { return this._puntajeEvaluacion; }
    get puntajeMeritos(): number { return this._puntajeMeritos; }
    get puntajeFinal(): number { return this._puntajeFinal; }
    
    // Setter con recálculo
    set puntajeMeritos(valor: number) {
        this._puntajeMeritos = valor;
        this._puntajeFinal = this._calculador.calcularPuntajeFinal(
            this._notaGrado,
            this._puntajeEvaluacion,
            this._puntajeMeritos
        );
        console.log(`  Méritos actualizados. Nuevo puntaje: ${this._puntajeFinal}/1000`);
    }
    
    agregarObservaciones(texto: string): void {
        this.observaciones = texto;
    }
    
    mostrarInfo(): void {
        console.log("\n" + "=".repeat(60));
        console.log(`PUNTAJE POSTULACIÓN ID: ${this.idPuntaje}`);
        console.log("=".repeat(60));
        console.log(`Cédula Postulante: ${this.cedulaPostulante}`);
        console.log(`Postulante ID: ${this.idPostulante}`);
        console.log(`Fecha cálculo: ${this.fechaCalculo.toLocaleDateString()}`);
        console.log(`\nCOMPONENTES:`);
        console.log(`  Nota de Grado: ${this._notaGrado}/10`);
        console.log(`  Evaluación: ${this._puntajeEvaluacion}/1000`);
        console.log(`  Méritos: ${this._puntajeMeritos}/1000`);
        console.log(`\nPUNTAJE FINAL: ${this._puntajeFinal}/1000`);
        if (this.observaciones) {
            console.log(`\nObservaciones: ${this.observaciones}`);
        }
        console.log("=".repeat(60));
    }
    
    toString(): string {
        return `PuntajePostulacion(ID:${this.idPuntaje}, Postulante:${this.idPostulante}, Puntaje:${this.puntajeFinal})`;
    }
    
    static obtenerTotal(): number {
        return PuntajePostulacion._contadorPuntajes;
    }
}

// ==================== EJEMPLOS DE USO ====================

console.log("\n" + "=".repeat(80));
console.log("PATRÓN TEMPLATE METHOD - PUNTAJE POSTULACIÓN");
console.log("=".repeat(80));

// ===== EJEMPLO 1: Calculador ESTÁNDAR =====
console.log("\n\nEJEMPLO 1: Puntaje con calculador ESTANDAR");
console.log("-".repeat(80));

const calcEstandar = new CalculadorPuntajeEstandar();

const puntaje1 = new PuntajePostulacion(
    1,
    9.5,
    850,
    "1316202082",
    calcEstandar,
    200
);

puntaje1.mostrarInfo();

// ===== EJEMPLO 2: Calculador CON MÉRITO =====
console.log("\n\nEJEMPLO 2: Puntaje con calculador CON MERITO");
console.log("-".repeat(80));

const calcMerito = new CalculadorPuntajeConMerito();

const puntaje2 = new PuntajePostulacion(
    2,
    9.0,
    800,
    "1350123456",
    calcMerito,
    750  // Alto mérito → bonificación
);

puntaje2.mostrarInfo();

// ===== EJEMPLO 3: Calculador INCLUSIÓN =====
console.log("\n\nEJEMPLO 3: Puntaje con calculador INCLUSION");
console.log("-".repeat(80));

const calcInclusion = new CalculadorPuntajeInclusion();

const puntaje3 = new PuntajePostulacion(
    3,
    8.0,
    700,
    "1360234567",
    calcInclusion,
    500
);

puntaje3.mostrarInfo();

// ===== EJEMPLO 4: Comparación de calculadores =====
console.log("\n\nEJEMPLO 4: Comparacion - Mismas notas, diferentes calculadores");
console.log("-".repeat(80));

const notasBase = {
    idPostulante: 4,
    notaGrado: 9.0,
    puntajeEval: 800,
    cedula: "1370345678",
    meritos: 600
};

const p_estandar = new PuntajePostulacion(
    notasBase.idPostulante,
    notasBase.notaGrado,
    notasBase.puntajeEval,
    notasBase.cedula,
    new CalculadorPuntajeEstandar(),
    notasBase.meritos
);

const p_merito = new PuntajePostulacion(
    notasBase.idPostulante,
    notasBase.notaGrado,
    notasBase.puntajeEval,
    notasBase.cedula,
    new CalculadorPuntajeConMerito(),
    notasBase.meritos
);

const p_inclusion = new PuntajePostulacion(
    notasBase.idPostulante,
    notasBase.notaGrado,
    notasBase.puntajeEval,
    notasBase.cedula,
    new CalculadorPuntajeInclusion(),
    notasBase.meritos
);

console.log("\nRESULTADOS:");
console.log("  ESTANDAR:  " + p_estandar.puntajeFinal + " puntos");
console.log("  MERITO:    " + p_merito.puntajeFinal + " puntos");
console.log("  INCLUSION: " + p_inclusion.puntajeFinal + " puntos");

console.log("\nTotal puntajes creados: " + PuntajePostulacion.obtenerTotal());

console.log("\n" + "=".repeat(80));
console.log("VENTAJAS DEL PATRÓN TEMPLATE METHOD:");
console.log("=".repeat(80));
console.log("1. Define estructura fija del algoritmo");
console.log("2. Permite personalizar pasos específicos");
console.log("3. Evita duplicación de código");
console.log("4. Fácil agregar nuevos tipos de cálculo");
console.log("5. Cumple Open/Closed Principle");
console.log("=".repeat(80));

})(); // Fin de encapsulación