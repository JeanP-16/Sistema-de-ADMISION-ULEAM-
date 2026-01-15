/**
 * Módulo: RegistroNacional con PATRÓN BUILDER
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: BUILDER (Creacional)
 * ¿Por qué? RegistroNacional tiene muchos atributos opcionales que se configuran paso a paso
 */

// ==================== INTERFACES ====================

interface IValidable {
    validarCompletitud(): boolean;
}

interface IDatosPersonales {
    identificacion: string;
    nombres: string;
    apellidos: string;
    obtenerNombreCompleto(): string;
}

// ==================== CLASE BASE ====================

class DatosPersonales implements IDatosPersonales {
    identificacion: string;
    nombres: string;
    apellidos: string;

    constructor(identificacion: string, nombres: string, apellidos: string) {
        this.identificacion = identificacion;
        this.nombres = nombres;
        this.apellidos = apellidos;
    }

    obtenerNombreCompleto(): string {
        return `${this.nombres} ${this.apellidos}`;
    }
}

// ==================== CLASE PRINCIPAL ====================

class RegistroNacional extends DatosPersonales implements IValidable {
    private static _contador: number = 0;

    tipoDocumento: string;
    nacionalidad: string;

    fechaNacimiento: string | null = null;
    sexo: string | null = null;
    genero: string | null = null;
    autoidentificacion: string | null = null;
    edad: number | null = null;

    carnetDiscapacidad: string | null = null;
    tipoDiscapacidad: string | null = null;
    porcentajeDiscapacidad: number = 0;

    provinciaReside: string | null = null;
    cantonReside: string | null = null;
    parroquiaReside: string | null = null;
    barrioSector: string | null = null;
    callePrincipal: string | null = null;

    celular: string | null = null;
    correo: string | null = null;

    unidadEducativa: string | null = null;
    tipoUnidadEducativa: string | null = null;
    calificacion: number | null = null;
    cuadroHonor: string = 'NO';

    fechaRegistroNacional: Date;
    estado: string = 'INCOMPLETO';
    estadoRegistroNacional: string = 'NO HABILITADO';
    observacionEstado: string | null = null;

    constructor(identificacion: string, nombres: string, apellidos: string) {
        super(identificacion, nombres, apellidos);

        RegistroNacional._contador++;
        this.tipoDocumento = /^\d+$/.test(identificacion) ? 'CEDULA' : 'PASAPORTE';
        this.nacionalidad = 'ECUATORIANA';
        this.fechaRegistroNacional = new Date();
    }

    calcularEdad(): number | null {
        if (this.fechaNacimiento) {
            const fechaNac = new Date(this.fechaNacimiento);
            const hoy = new Date();
            let edad = hoy.getFullYear() - fechaNac.getFullYear();
            const mes = hoy.getMonth() - fechaNac.getMonth();

            if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
                edad--;
            }

            this.edad = edad;
            return edad;
        }
        return null;
    }

    validarCompletitud(): boolean {
        if (!this.nombres || !this.apellidos || !this.identificacion) {
            this.estado = 'INCOMPLETO';
            this.observacionEstado = 'Faltan datos básicos';
            return false;
        }

        if (!this.celular || !this.correo) {
            this.estado = 'INCOMPLETO';
            this.observacionEstado = 'Faltan datos de contacto';
            return false;
        }

        if (!this.provinciaReside) {
            this.estado = 'INCOMPLETO';
            this.observacionEstado = 'Falta ubicación';
            return false;
        }

        if (!this.unidadEducativa) {
            this.estado = 'INCOMPLETO';
            this.observacionEstado = 'Faltan datos académicos';
            return false;
        }

        this.estado = 'COMPLETO';
        this.estadoRegistroNacional = 'HABILITADO';
        this.observacionEstado = null;
        return true;
    }

    toString(): string {
        return `RegistroNacional(${this.obtenerNombreCompleto()}, CI: ${this.identificacion})`;
    }
}

// ==================== PATRÓN BUILDER ====================

class RegistroNacionalBuilder {
    private _registro: RegistroNacional;

    constructor(identificacion: string, nombres: string, apellidos: string) {
        this._registro = new RegistroNacional(identificacion, nombres, apellidos);
    }

    conDatosPersonales(fechaNac: string, sexo: string, autoidentificacion: string): RegistroNacionalBuilder {
        this._registro.fechaNacimiento = fechaNac;
        this._registro.sexo = sexo.toUpperCase();
        this._registro.genero = sexo.toUpperCase() === 'HOMBRE' ? 'MASCULINO' : 'FEMENINO';
        this._registro.autoidentificacion = autoidentificacion.toUpperCase();
        this._registro.calcularEdad();
        return this;
    }

    conUbicacion(provincia: string, canton: string, parroquia: string, 
                 barrio: string | null = null, calle: string | null = null): RegistroNacionalBuilder {
        this._registro.provinciaReside = provincia;
        this._registro.cantonReside = canton;
        this._registro.parroquiaReside = parroquia;
        this._registro.barrioSector = barrio;
        this._registro.callePrincipal = calle;
        return this;
    }

    conContacto(celular: string, correo: string): RegistroNacionalBuilder {
        this._registro.celular = celular;
        this._registro.correo = correo.toLowerCase();
        return this;
    }

    conDatosAcademicos(unidadEducativa: string, tipoUnidad: string, 
                       calificacion: number, cuadroHonor: string = 'NO'): RegistroNacionalBuilder {
        this._registro.unidadEducativa = unidadEducativa;
        this._registro.tipoUnidadEducativa = tipoUnidad.toUpperCase();
        this._registro.calificacion = calificacion;
        this._registro.cuadroHonor = cuadroHonor.toUpperCase();
        return this;
    }

    conDiscapacidad(carnet: string, tipo: string, porcentaje: number): RegistroNacionalBuilder {
        this._registro.carnetDiscapacidad = carnet;
        this._registro.tipoDiscapacidad = tipo.toUpperCase();
        this._registro.porcentajeDiscapacidad = porcentaje;
        return this;
    }

    build(): RegistroNacional {
        this._registro.validarCompletitud();
        return this._registro;
    }
}

// ==================== DIRECTOR ====================

class DirectorRegistro {
    static construirRegistroCompleto(
        builder: RegistroNacionalBuilder,
        datosPersonales: { fechaNac: string; sexo: string; autoidentificacion: string },
        ubicacion: { provincia: string; canton: string; parroquia: string },
        contacto: { celular: string; correo: string },
        academicos: { unidadEducativa: string; tipoUnidad: string; calificacion: number; cuadroHonor?: string }
    ): RegistroNacional {
        return builder
            .conDatosPersonales(datosPersonales.fechaNac, datosPersonales.sexo, datosPersonales.autoidentificacion)
            .conUbicacion(ubicacion.provincia, ubicacion.canton, ubicacion.parroquia)
            .conContacto(contacto.celular, contacto.correo)
            .conDatosAcademicos(academicos.unidadEducativa, academicos.tipoUnidad, academicos.calificacion, academicos.cuadroHonor)
            .build();
    }
}

export { RegistroNacional, RegistroNacionalBuilder, DirectorRegistro, DatosPersonales, IValidable, IDatosPersonales };