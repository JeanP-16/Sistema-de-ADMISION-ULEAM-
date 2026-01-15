/**
 * Módulo: Asignacion con PATRÓN SINGLETON
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: SINGLETON (Creacional)
 * ¿Por qué? Solo debe existir UNA instancia del gestor de asignaciones en todo el sistema
 */

// ==================== PATRÓN SINGLETON ====================

class AsignacionManager {
    private static _instancia: AsignacionManager | null = null;
    private static _inicializado: boolean = false;
    
    private _asignaciones: Map<number, Asignacion> = new Map();
    private _contador: number = 0;
    private _cuposDisponibles: Map<number, number> = new Map();
    
    private constructor() {
        if (!AsignacionManager._inicializado) {
            AsignacionManager._inicializado = true;
        }
    }
    
    static obtenerInstancia(): AsignacionManager {
        if (AsignacionManager._instancia === null) {
            AsignacionManager._instancia = new AsignacionManager();
        }
        return AsignacionManager._instancia;
    }
    
    registrarAsignacion(asignacion: Asignacion): void {
        this._contador++;
        this._asignaciones.set(asignacion.idAsignacion, asignacion);
    }
    
    obtenerAsignacion(idAsignacion: number): Asignacion | null {
        return this._asignaciones.get(idAsignacion) || null;
    }
    
    obtenerTodasAsignaciones(): Asignacion[] {
        return Array.from(this._asignaciones.values());
    }
    
    configurarCupos(carreraId: number, cupos: number): void {
        this._cuposDisponibles.set(carreraId, cupos);
    }
    
    obtenerCuposDisponibles(carreraId: number): number {
        return this._cuposDisponibles.get(carreraId) || 0;
    }
    
    reducirCupo(carreraId: number): boolean {
        const cupos = this.obtenerCuposDisponibles(carreraId);
        if (cupos > 0) {
            this._cuposDisponibles.set(carreraId, cupos - 1);
            return true;
        }
        return false;
    }
    
    obtenerEstadisticas(): any {
        const estados: { [key: string]: number } = {};
        
        for (const asig of this._asignaciones.values()) {
            estados[asig.estado] = (estados[asig.estado] || 0) + 1;
        }
        
        let cuposRestantes = 0;
        for (const cupos of this._cuposDisponibles.values()) {
            cuposRestantes += cupos;
        }
        
        return {
            totalAsignaciones: this._contador,
            porEstado: estados,
            cuposRestantes: cuposRestantes
        };
    }
}

// ==================== CLASES BASE ====================

abstract class ProcesoAcademico {
    abstract validarRequisitos(): boolean;
    abstract cancelar(): void;
    abstract completar(): void;
}

// ==================== CLASE PRINCIPAL ====================

class Asignacion extends ProcesoAcademico {
    private static _contadorAsignaciones: number = 0;
    static readonly ESTADOS_VALIDOS = ['ASIGNADO', 'PENDIENTE', 'RECHAZADO', 'CANCELADO'];
    static readonly TIPOS_ASIGNACION = ['PRIMERA_OPCION', 'SEGUNDA_OPCION', 'TERCERA_OPCION', 'REASIGNACION'];
    
    idAsignacion: number;
    idPostulante: number;
    carreraId: number;
    sedeId: number;
    puntajeTotal: number;
    ordenMerito: number;
    tipoAsignacion: string;
    
    fechaAsignacion: Date;
    estado: string = 'PENDIENTE';
    observaciones: string | null = null;
    fechaAceptacion: Date | null = null;
    fechaRechazo: Date | null = null;
    
    constructor(
        idPostulante: number,
        carreraId: number,
        sedeId: number,
        puntajeTotal: number,
        ordenMerito: number,
        tipoAsignacion: string = 'PRIMERA_OPCION'
    ) {
        super();
        
        Asignacion._contadorAsignaciones++;
        
        this.idAsignacion = Asignacion._contadorAsignaciones;
        this.idPostulante = idPostulante;
        this.carreraId = carreraId;
        this.sedeId = sedeId;
        this.puntajeTotal = puntajeTotal;
        this.ordenMerito = ordenMerito;
        this.tipoAsignacion = tipoAsignacion.toUpperCase();
        
        this.fechaAsignacion = new Date();
        
        if (!Asignacion.TIPOS_ASIGNACION.includes(this.tipoAsignacion)) {
            throw new Error(`Tipo de asignación inválido: ${tipoAsignacion}`);
        }
        
        if (this.puntajeTotal < 0 || this.puntajeTotal > 1000) {
            throw new Error(`Puntaje fuera de rango: ${puntajeTotal}`);
        }
        
        const manager = AsignacionManager.obtenerInstancia();
        manager.registrarAsignacion(this);
    }
    
    validarRequisitos(): boolean {
        const manager = AsignacionManager.obtenerInstancia();
        
        const cupos = manager.obtenerCuposDisponibles(this.carreraId);
        if (cupos <= 0) {
            this.observaciones = "Sin cupos disponibles";
            return false;
        }
        
        if (this.puntajeTotal < 600) {
            this.observaciones = "Puntaje insuficiente (mínimo 600)";
            return false;
        }
        
        return true;
    }
    
    asignar(): boolean {
        if (!this.validarRequisitos()) {
            this.estado = 'RECHAZADO';
            this.fechaRechazo = new Date();
            return false;
        }
        
        const manager = AsignacionManager.obtenerInstancia();
        
        if (manager.reducirCupo(this.carreraId)) {
            this.estado = 'ASIGNADO';
            this.fechaAceptacion = new Date();
            this.observaciones = "Asignación exitosa";
            return true;
        } else {
            this.estado = 'RECHAZADO';
            this.observaciones = "No se pudo reducir cupo";
            return false;
        }
    }
    
    cancelar(): void {
        if (this.estado === 'ASIGNADO') {
            const manager = AsignacionManager.obtenerInstancia();
            const cuposActuales = manager.obtenerCuposDisponibles(this.carreraId);
            manager.configurarCupos(this.carreraId, cuposActuales + 1);
        }
        
        this.estado = 'CANCELADO';
        this.observaciones = "Asignación cancelada por el postulante";
    }
    
    completar(): void {
        if (this.estado === 'ASIGNADO') {
            this.observaciones = "Proceso de asignación completado";
        }
    }
    
    obtenerInformacion(): any {
        return {
            idAsignacion: this.idAsignacion,
            idPostulante: this.idPostulante,
            carreraId: this.carreraId,
            sedeId: this.sedeId,
            puntajeTotal: this.puntajeTotal,
            ordenMerito: this.ordenMerito,
            tipoAsignacion: this.tipoAsignacion,
            estado: this.estado,
            fechaAsignacion: this.fechaAsignacion.toISOString(),
            observaciones: this.observaciones
        };
    }
    
    toString(): string {
        return `Asignacion(ID:${this.idAsignacion}, Postulante:${this.idPostulante}, Estado:${this.estado})`;
    }
}

export { AsignacionManager, Asignacion, ProcesoAcademico };