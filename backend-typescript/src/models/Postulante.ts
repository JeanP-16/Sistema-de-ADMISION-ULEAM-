/**
 * Módulo: Postulante con PATRÓN OBSERVER
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: OBSERVER (Comportamiento)
 * ¿Por qué? Cuando un postulante cambia de estado, varios componentes necesitan ser notificados
 */

// ==================== PATRÓN OBSERVER ====================

interface IObservadorPostulante {
    actualizar(postulante: Postulante, evento: string, datos: any): void;
}

// ==================== CLASES BASE ====================

interface IValidadorIdentidad {
    validarIdentidad(): boolean;
}

interface ICalculadorEdad {
    calcularEdad(): number;
}

abstract class Persona implements IValidadorIdentidad, ICalculadorEdad {
    cedula: string;
    nombreCompleto: string;

    constructor(cedula: string, nombreCompleto: string) {
        this.cedula = cedula;
        this.nombreCompleto = nombreCompleto;
    }

    abstract validarIdentidad(): boolean;
    abstract calcularEdad(): number;
}

// ==================== CLASE PRINCIPAL ====================

class Postulante extends Persona {
    private static _contadorPostulantes: number = 0;
    static readonly ESTADOS_VALIDOS = ['VERIFICADO', 'PENDIENTE', 'RECHAZADO'];

    idPostulante: number;
    email: string;
    telefono: string;
    fechaNacimiento: string;
    estadoRegistro: string = 'PENDIENTE';
    fechaRegistro: Date;

    private _inscripciones: any[] = [];
    private _puntajes: any[] = [];
    private _asignacion: any = null;

    private _observadores: IObservadorPostulante[] = [];

    constructor(cedula: string, nombreCompleto: string, email: string, telefono: string, fechaNacimiento: string) {
        super(cedula, nombreCompleto);

        Postulante._contadorPostulantes++;
        this.idPostulante = Postulante._contadorPostulantes;

        this.cedula = this._validarCedula(cedula);
        this.email = this._validarEmail(email);
        this.telefono = telefono.trim();
        this.fechaNacimiento = fechaNacimiento;
        this.fechaRegistro = new Date();
    }

    private _validarCedula(cedula: string): string {
        cedula = cedula.trim();

        if (!/^\d{10}$/.test(cedula)) {
            throw new Error('Cedula invalida: debe tener 10 digitos numericos');
        }

        const provincia = parseInt(cedula.substring(0, 2));
        if (provincia < 1 || provincia > 24) {
            throw new Error(`Codigo de provincia invalido: ${provincia}`);
        }

        return cedula;
    }

    private _validarEmail(email: string): string {
        email = email.trim().toLowerCase();
        const patron = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        if (!patron.test(email)) {
            throw new Error(`Email invalido: ${email}`);
        }

        return email;
    }

    agregarObservador(observador: IObservadorPostulante): void {
        if (!this._observadores.includes(observador)) {
            this._observadores.push(observador);
        }
    }

    removerObservador(observador: IObservadorPostulante): void {
        const index = this._observadores.indexOf(observador);
        if (index > -1) {
            this._observadores.splice(index, 1);
        }
    }

    private notificarObservadores(evento: string, datos: any = {}): void {
        for (const obs of this._observadores) {
            obs.actualizar(this, evento, datos);
        }
    }

    validarIdentidad(): boolean {
        const esValido = this.cedula.length === 10 && /^\d+$/.test(this.cedula);

        if (esValido) {
            this.estadoRegistro = 'VERIFICADO';
            this.notificarObservadores('identidad_verificada', {
                cedula: this.cedula,
                estado: 'VERIFICADO'
            });
        } else {
            this.estadoRegistro = 'RECHAZADO';
            this.notificarObservadores('identidad_rechazada', {
                cedula: this.cedula,
                estado: 'RECHAZADO'
            });
        }

        return esValido;
    }

    calcularEdad(): number {
        const fechaNac = new Date(this.fechaNacimiento);
        const hoy = new Date();
        let edad = hoy.getFullYear() - fechaNac.getFullYear();
        const mes = hoy.getMonth() - fechaNac.getMonth();

        if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
            edad--;
        }

        return edad;
    }

    actualizarDatos(email: string | null = null, telefono: string | null = null): void {
        const datosActualizados: any = {};

        if (email) {
            this.email = this._validarEmail(email);
            datosActualizados.email = this.email;
        }

        if (telefono) {
            this.telefono = telefono.trim();
            datosActualizados.telefono = this.telefono;
        }

        if (Object.keys(datosActualizados).length > 0) {
            this.notificarObservadores('datos_actualizados', datosActualizados);
        }
    }

    agregarInscripcion(inscripcion: any): void {
        this._inscripciones.push(inscripcion);
        this.notificarObservadores('inscripcion_agregada', {
            totalInscripciones: this._inscripciones.length
        });
    }

    toString(): string {
        return `Postulante(ID: ${this.idPostulante}, Nombre: ${this.nombreCompleto})`;
    }
}

export { Postulante, Persona, IValidadorIdentidad, ICalculadorEdad, IObservadorPostulante };