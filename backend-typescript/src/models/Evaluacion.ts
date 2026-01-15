/**
 * Módulo: Evaluacion con PATRÓN STRATEGY
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: STRATEGY (Comportamiento)
 * ¿Por qué? Diferentes estrategias de cálculo de puntaje según el tipo de evaluación
 */

interface IEstrategiaPuntaje {
    calcularPuntaje(notaExamen: number, notaEntrevista: number, 
                   calificacionColegio: number, extras: any): number;
    obtenerNombre(): string;
}

class EstrategiaPuntajeStandar implements IEstrategiaPuntaje {
    calcularPuntaje(notaExamen: number, notaEntrevista: number,
                   calificacionColegio: number, extras: any): number {
        const puntaje = (
            notaExamen * 0.60 +
            calificacionColegio * 10 * 0.25 +
            notaEntrevista * 0.15
        );
        
        return Math.round(puntaje * 100) / 100;
    }
    
    obtenerNombre(): string {
        return "ESTANDAR";
    }
}

class EstrategiaPuntajeMerito implements IEstrategiaPuntaje {
    calcularPuntaje(notaExamen: number, notaEntrevista: number,
                   calificacionColegio: number, extras: any): number {
        const puntajeBase = (
            notaExamen * 0.40 +
            calificacionColegio * 10 * 0.50 +
            notaEntrevista * 0.10
        );
        
        const bonoCuadroHonor = extras.cuadroHonor ? 50 : 0;
        const bonoExcelencia = calificacionColegio >= 9.5 ? 30 : 0;
        
        const puntajeTotal = puntajeBase + bonoCuadroHonor + bonoExcelencia;
        
        return Math.round(puntajeTotal * 100) / 100;
    }
    
    obtenerNombre(): string {
        return "MERITO_ACADEMICO";
    }
}

class EstrategiaPuntajeInclusion implements IEstrategiaPuntaje {
    calcularPuntaje(notaExamen: number, notaEntrevista: number,
                   calificacionColegio: number, extras: any): number {
        const puntajeBase = (
            notaExamen * 0.50 +
            calificacionColegio * 10 * 0.20 +
            notaEntrevista * 0.10
        );
        
        const bonoDiscapacidad = (extras.porcentajeDiscapacidad || 0) * 2;
        const bonoEtnico = extras.puebloOriginario ? 100 : 0;
        const bonoZonaRural = extras.zonaRural ? 50 : 0;
        
        const bonosTotales = bonoDiscapacidad + bonoEtnico + bonoZonaRural;
        const puntajeTotal = puntajeBase + bonosTotales;
        
        return Math.round(puntajeTotal * 100) / 100;
    }
    
    obtenerNombre(): string {
        return "INCLUSION_SOCIAL";
    }
}

class EstrategiaPuntajeDeportivo implements IEstrategiaPuntaje {
    calcularPuntaje(notaExamen: number, notaEntrevista: number,
                   calificacionColegio: number, extras: any): number {
        const puntajeBase = (
            notaExamen * 0.30 +
            calificacionColegio * 10 * 0.20
        );
        
        const nivelDeportivo = extras.nivelDeportivo || 'NINGUNO';
        const bonosDeportivos: { [key: string]: number } = {
            'INTERNACIONAL': 500,
            'NACIONAL': 350,
            'PROVINCIAL': 200,
            'LOCAL': 100,
            'NINGUNO': 0
        };
        
        const bonoDeporte = bonosDeportivos[nivelDeportivo] || 0;
        const puntajeTotal = puntajeBase + bonoDeporte;
        
        return Math.round(puntajeTotal * 100) / 100;
    }
    
    obtenerNombre(): string {
        return "DEPORTIVO";
    }
}

class Evaluacion {
    private static _contadorEvaluaciones: number = 0;
    static readonly ESTADOS_VALIDOS = ['PROGRAMADA', 'EN_CURSO', 'COMPLETADA', 'CANCELADA'];
    static readonly TIPOS_EVALUACION = ['EXAMEN', 'ENTREVISTA', 'INTEGRAL'];
    
    idEvaluacion: number;
    idInscripcion: number;
    tipoEvaluacion: string;
    private _estrategiaPuntaje: IEstrategiaPuntaje;
    
    fechaProgramada: Date;
    fechaRealizacion: Date | null = null;
    estado: string = 'PROGRAMADA';
    
    notaExamen: number | null = null;
    notaEntrevista: number | null = null;
    calificacionColegio: number | null = null;
    puntajeTotal: number | null = null;
    
    extras: any = {};
    
    constructor(
        idInscripcion: number,
        tipoEvaluacion: string,
        estrategiaPuntaje: IEstrategiaPuntaje,
        fechaProgramada?: string
    ) {
        Evaluacion._contadorEvaluaciones++;
        
        this.idEvaluacion = Evaluacion._contadorEvaluaciones;
        this.idInscripcion = idInscripcion;
        this.tipoEvaluacion = tipoEvaluacion.toUpperCase();
        this._estrategiaPuntaje = estrategiaPuntaje;
        
        if (fechaProgramada) {
            this.fechaProgramada = new Date(fechaProgramada);
        } else {
            this.fechaProgramada = new Date();
        }
        
        if (!Evaluacion.TIPOS_EVALUACION.includes(this.tipoEvaluacion)) {
            throw new Error(`Tipo de evaluación inválido: ${tipoEvaluacion}`);
        }
    }
    
    cambiarEstrategia(nuevaEstrategia: IEstrategiaPuntaje): void {
        this._estrategiaPuntaje = nuevaEstrategia;
    }
    
    registrarNotas(
        notaExamen: number,
        notaEntrevista: number,
        calificacionColegio: number,
        extras: any = {}
    ): void {
        if (notaExamen < 0 || notaExamen > 1000) {
            throw new Error(`Nota de examen fuera de rango: ${notaExamen}`);
        }
        
        if (notaEntrevista < 0 || notaEntrevista > 100) {
            throw new Error(`Nota de entrevista fuera de rango: ${notaEntrevista}`);
        }
        
        if (calificacionColegio < 0 || calificacionColegio > 10) {
            throw new Error(`Calificación de colegio fuera de rango: ${calificacionColegio}`);
        }
        
        this.notaExamen = notaExamen;
        this.notaEntrevista = notaEntrevista;
        this.calificacionColegio = calificacionColegio;
        this.extras = extras;
    }
    
    calcularPuntajeTotal(): number {
        if (this.notaExamen === null) {
            throw new Error("Debe registrar notas antes de calcular puntaje");
        }
        
        this.puntajeTotal = this._estrategiaPuntaje.calcularPuntaje(
            this.notaExamen,
            this.notaEntrevista!,
            this.calificacionColegio!,
            this.extras
        );
        
        this.estado = 'COMPLETADA';
        this.fechaRealizacion = new Date();
        
        return this.puntajeTotal;
    }
    
    obtenerResultado(): any {
        return {
            idEvaluacion: this.idEvaluacion,
            idInscripcion: this.idInscripcion,
            tipoEvaluacion: this.tipoEvaluacion,
            estrategia: this._estrategiaPuntaje.obtenerNombre(),
            notaExamen: this.notaExamen,
            notaEntrevista: this.notaEntrevista,
            calificacionColegio: this.calificacionColegio,
            puntajeTotal: this.puntajeTotal,
            estado: this.estado,
            fechaRealizacion: this.fechaRealizacion?.toISOString()
        };
    }
    
    toString(): string {
        return `Evaluacion(ID:${this.idEvaluacion}, Estrategia:${this._estrategiaPuntaje.obtenerNombre()}, Puntaje:${this.puntajeTotal})`;
    }
}

export { Evaluacion, IEstrategiaPuntaje, EstrategiaPuntajeStandar, EstrategiaPuntajeMerito, EstrategiaPuntajeInclusion, EstrategiaPuntajeDeportivo };