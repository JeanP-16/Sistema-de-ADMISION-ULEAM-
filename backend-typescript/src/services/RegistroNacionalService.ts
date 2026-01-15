/**
 * Servicio: RegistroNacionalService
 * Gestiona la lógica de negocio para registros nacionales
 * Coordina: RegistroNacional, Builder, validaciones
 */

import { 
  RegistroNacional, 
  RegistroNacionalBuilder, 
  DirectorRegistro 
} from '../models/RegistroNacional';

export class RegistroNacionalService {
  private registros: Map<string, RegistroNacional> = new Map();

  /**
   * Crear registro básico (solo datos principales)
   */
  async crearRegistroBasico(datos: {
    identificacion: string;
    nombres: string;
    apellidos: string;
  }): Promise<{ exito: boolean; registro?: any; error?: string }> {
    
    try {
      // 1. Validar que no exista
      if (this.registros.has(datos.identificacion)) {
        return {
          exito: false,
          error: `Ya existe un registro con la identificación ${datos.identificacion}`
        };
      }

      // 2. Validar formato de identificación
      if (datos.identificacion.trim().length < 10) {
        return {
          exito: false,
          error: 'La identificación debe tener al menos 10 caracteres'
        };
      }

      // 3. Validar nombres y apellidos
      if (!datos.nombres.trim() || !datos.apellidos.trim()) {
        return {
          exito: false,
          error: 'Los nombres y apellidos son obligatorios'
        };
      }

      // 4. Crear registro
      const registro = new RegistroNacional(
        datos.identificacion,
        datos.nombres.toUpperCase(),
        datos.apellidos.toUpperCase()
      );

      // 5. Almacenar
      this.registros.set(datos.identificacion, registro);

      return {
        exito: true,
        registro: {
          identificacion: registro.identificacion,
          nombreCompleto: registro.obtenerNombreCompleto(),
          tipoDocumento: registro.tipoDocumento,
          nacionalidad: registro.nacionalidad,
          estado: registro.estado,
          estadoRegistroNacional: registro.estadoRegistroNacional,
          fechaRegistro: registro.fechaRegistroNacional
        }
      };

    } catch (error) {
      return {
        exito: false,
        error: error instanceof Error ? error.message : 'Error al crear registro básico'
      };
    }
  }

  /**
   * Crear registro completo usando Builder Pattern
   */
  async crearRegistroCompleto(datos: {
    identificacion: string;
    nombres: string;
    apellidos: string;
    datosPersonales: {
      fechaNac: string;
      sexo: string;
      autoidentificacion: string;
    };
    ubicacion: {
      provincia: string;
      canton: string;
      parroquia: string;
      barrio?: string;
      calle?: string;
    };
    contacto: {
      celular: string;
      correo: string;
    };
    academicos: {
      unidadEducativa: string;
      tipoUnidad: string;
      calificacion: number;
      cuadroHonor?: string;
    };
    discapacidad?: {
      carnet: string;
      tipo: string;
      porcentaje: number;
    };
  }): Promise<{ exito: boolean; registro?: any; error?: string }> {
    
    try {
      // 1. Validar que no exista
      if (this.registros.has(datos.identificacion)) {
        return {
          exito: false,
          error: `Ya existe un registro con la identificación ${datos.identificacion}`
        };
      }

      // 2. Validar datos de contacto
      if (!/^\d{10}$/.test(datos.contacto.celular)) {
        return {
          exito: false,
          error: 'El celular debe contener exactamente 10 dígitos'
        };
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(datos.contacto.correo)) {
        return {
          exito: false,
          error: 'El formato del correo es inválido'
        };
      }

      // 3. Validar calificación
      if (datos.academicos.calificacion < 0 || datos.academicos.calificacion > 10) {
        return {
          exito: false,
          error: 'La calificación debe estar entre 0 y 10'
        };
      }

      // 4. Crear usando Builder
      const builder = new RegistroNacionalBuilder(
        datos.identificacion,
        datos.nombres.toUpperCase(),
        datos.apellidos.toUpperCase()
      );

      // 5. Construir con Director
      let registro;
      
      if (datos.discapacidad) {
        // Con discapacidad
        registro = builder
          .conDatosPersonales(
            datos.datosPersonales.fechaNac,
            datos.datosPersonales.sexo,
            datos.datosPersonales.autoidentificacion
          )
          .conUbicacion(
            datos.ubicacion.provincia,
            datos.ubicacion.canton,
            datos.ubicacion.parroquia,
            datos.ubicacion.barrio,
            datos.ubicacion.calle
          )
          .conContacto(datos.contacto.celular, datos.contacto.correo)
          .conDatosAcademicos(
            datos.academicos.unidadEducativa,
            datos.academicos.tipoUnidad,
            datos.academicos.calificacion,
            datos.academicos.cuadroHonor
          )
          .conDiscapacidad(
            datos.discapacidad.carnet,
            datos.discapacidad.tipo,
            datos.discapacidad.porcentaje
          )
          .build();
      } else {
        // Sin discapacidad
        registro = DirectorRegistro.construirRegistroCompleto(
          builder,
          datos.datosPersonales,
          datos.ubicacion,
          datos.contacto,
          datos.academicos
        );
      }

      // 6. Almacenar
      this.registros.set(datos.identificacion, registro);

      return {
        exito: true,
        registro: {
          identificacion: registro.identificacion,
          nombreCompleto: registro.obtenerNombreCompleto(),
          tipoDocumento: registro.tipoDocumento,
          edad: registro.edad,
          correo: registro.correo,
          celular: registro.celular,
          provincia: registro.provinciaReside,
          unidadEducativa: registro.unidadEducativa,
          calificacion: registro.calificacion,
          cuadroHonor: registro.cuadroHonor,
          estado: registro.estado,
          estadoRegistroNacional: registro.estadoRegistroNacional,
          observacion: registro.observacionEstado,
          discapacidad: registro.carnetDiscapacidad ? {
            tipo: registro.tipoDiscapacidad,
            porcentaje: registro.porcentajeDiscapacidad
          } : null
        }
      };

    } catch (error) {
      return {
        exito: false,
        error: error instanceof Error ? error.message : 'Error al crear registro completo'
      };
    }
  }

  /**
   * Buscar registro por identificación
   */
  buscarPorIdentificacion(identificacion: string): any {
    const registro = this.registros.get(identificacion);
    
    if (!registro) {
      return null;
    }

    return {
      identificacion: registro.identificacion,
      nombreCompleto: registro.obtenerNombreCompleto(),
      tipoDocumento: registro.tipoDocumento,
      nacionalidad: registro.nacionalidad,
      fechaNacimiento: registro.fechaNacimiento,
      edad: registro.edad,
      sexo: registro.sexo,
      autoidentificacion: registro.autoidentificacion,
      correo: registro.correo,
      celular: registro.celular,
      provincia: registro.provinciaReside,
      canton: registro.cantonReside,
      parroquia: registro.parroquiaReside,
      unidadEducativa: registro.unidadEducativa,
      tipoUnidadEducativa: registro.tipoUnidadEducativa,
      calificacion: registro.calificacion,
      cuadroHonor: registro.cuadroHonor,
      estado: registro.estado,
      estadoRegistroNacional: registro.estadoRegistroNacional,
      observacion: registro.observacionEstado,
      discapacidad: registro.carnetDiscapacidad ? {
        carnet: registro.carnetDiscapacidad,
        tipo: registro.tipoDiscapacidad,
        porcentaje: registro.porcentajeDiscapacidad
      } : null,
      fechaRegistro: registro.fechaRegistroNacional
    };
  }

  /**
   * Listar registros habilitados (completos)
   */
  listarHabilitados(): any[] {
    return Array.from(this.registros.values())
      .filter(r => r.estadoRegistroNacional === 'HABILITADO')
      .map(r => ({
        identificacion: r.identificacion,
        nombreCompleto: r.obtenerNombreCompleto(),
        calificacion: r.calificacion,
        provincia: r.provinciaReside,
        estado: r.estado
      }));
  }

  /**
   * Listar registros incompletos
   */
  listarIncompletos(): any[] {
    return Array.from(this.registros.values())
      .filter(r => r.estado === 'INCOMPLETO')
      .map(r => ({
        identificacion: r.identificacion,
        nombreCompleto: r.obtenerNombreCompleto(),
        estado: r.estado,
        observacion: r.observacionEstado
      }));
  }

  /**
   * Listar todos los registros
   */
  listarTodos(): any[] {
    return Array.from(this.registros.values()).map(r => ({
      identificacion: r.identificacion,
      nombreCompleto: r.obtenerNombreCompleto(),
      tipoDocumento: r.tipoDocumento,
      correo: r.correo,
      celular: r.celular,
      estado: r.estado,
      estadoRegistroNacional: r.estadoRegistroNacional
    }));
  }

  /**
   * Verificar completitud de un registro
   */
  verificarCompletitud(identificacion: string): { completo: boolean; faltante?: string } {
    const registro = this.registros.get(identificacion);
    
    if (!registro) {
      return { completo: false, faltante: 'Registro no encontrado' };
    }

    const esCompleto = registro.validarCompletitud();
    
    return {
      completo: esCompleto,
      faltante: registro.observacionEstado || undefined
    };
  }

  /**
   * Obtener estadísticas
   */
  obtenerEstadisticas(): any {
    const todos = Array.from(this.registros.values());
    
    const porEstado: { [key: string]: number } = {};
    const porTipoDocumento: { [key: string]: number } = {};
    let conDiscapacidad = 0;
    let cuadroHonor = 0;

    for (const r of todos) {
      porEstado[r.estado] = (porEstado[r.estado] || 0) + 1;
      porTipoDocumento[r.tipoDocumento] = (porTipoDocumento[r.tipoDocumento] || 0) + 1;
      
      if (r.carnetDiscapacidad) conDiscapacidad++;
      if (r.cuadroHonor === 'SI') cuadroHonor++;
    }

    return {
      total: this.registros.size,
      porEstado,
      porTipoDocumento,
      habilitados: porEstado['COMPLETO'] || 0,
      incompletos: porEstado['INCOMPLETO'] || 0,
      conDiscapacidad,
      cuadroHonor
    };
  }

  /**
   * Verificar si existe un registro
   */
  existe(identificacion: string): boolean {
    return this.registros.has(identificacion);
  }
}