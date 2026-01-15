/**
 * Módulo: Inscripcion con PATRÓN ADAPTER
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: ADAPTER (Estructural)
 * ¿Por qué? Necesitamos adaptar sistemas externos a nuestra interfaz
 */

// ==================== CLASE BASE ====================

abstract class ProcesoBase {
    abstract validarRequisitos(): boolean;
    abstract cancelar(): void;
    abstract completar(): void;
    abstract mostrarInfoCompleta(): void;
}

// ==================== CLASE PRINCIPAL ====================

class Inscripcion extends ProcesoBase {
    private static _contadorInscripciones: number = 0;

    static readonly JORNADAS_VALIDAS = ['matutina', 'vespertina', 'nocturna'];
    static readonly ESTADOS_VALIDOS = ['ACTIVA', 'CANCELADA', 'COMPLETADA'];
    static readonly MAX_PREFERENCIAS = 3;

    idInscripcion: number;
    idPostulante: number;
    carreraId: number;
    ordenPreferencia: number;
    sedeId: number;
    jornada: string;
    laboratorioId: number | null;
    cedulaPostulante: string;
    emailPostulante: string | null;
    fechaInscripcion: Date;
    comprobantePdfUrl: string;
    estado: string = 'ACTIVA';

    constructor(
        idPostulante: number,
        carreraId: number,
        ordenPreferencia: number,
        sedeId: number,
        jornada: string,
        cedulaPostulante: string,
        emailPostulante: string | null = null,
        laboratorioId: number | null = null
    ) {
        super();

        Inscripcion._contadorInscripciones++;

        this.idInscripcion = Inscripcion._contadorInscripciones;
        this.idPostulante = idPostulante;
        this.carreraId = carreraId;
        this.ordenPreferencia = ordenPreferencia;
        this.sedeId = sedeId;
        this.jornada = jornada.toLowerCase();
        this.laboratorioId = laboratorioId;
        this.cedulaPostulante = cedulaPostulante;
        this.emailPostulante = emailPostulante;
        this.fechaInscripcion = new Date();
        this.comprobantePdfUrl = `COMP-${this.idInscripcion}-${this.cedulaPostulante}.pdf`;
    }

    validarRequisitos(): boolean {
        if (!this.comprobantePdfUrl) {
            return false;
        }

        if (this.estado === 'CANCELADA') {
            return false;
        }

        return true;
    }

    cancelar(): void {
        this.estado = 'CANCELADA';
    }

    completar(): void {
        this.estado = 'COMPLETADA';
    }

    mostrarInfoCompleta(): void {
        console.log(`\nINSCRIPCION ID: ${this.idInscripcion}`);
        console.log(`Postulante ID: ${this.idPostulante}`);
        console.log(`Carrera ID: ${this.carreraId}`);
        console.log(`Estado: ${this.estado}`);
    }

    toString(): string {
        return `Inscripcion(ID:${this.idInscripcion}, Estado:${this.estado})`;
    }
}

export { Inscripcion, ProcesoBase };