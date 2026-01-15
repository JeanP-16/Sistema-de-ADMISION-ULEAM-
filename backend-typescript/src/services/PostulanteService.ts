/**
 * Servicio: PostulanteService
 * Gestiona la lógica de negocio para postulantes
 */

import { Postulante } from '../models/Postulante';

export class PostulanteService {
  private postulantes: Map<string, Postulante> = new Map();

  async registrarPostulante(datos: {
    cedula: string;
    nombreCompleto: string;
    email: string;
    telefono: string;
    fechaNacimiento: string;
  }): Promise<{ exito: boolean; postulante?: any; error?: string }> {
    
    try {
      if (this.postulantes.has(datos.cedula)) {
        return {
          exito: false,
          error: `Ya existe un postulante registrado con la cédula ${datos.cedula}`
        };
      }

      if (!/^\d{10}$/.test(datos.cedula)) {
        return {
          exito: false,
          error: 'La cédula debe contener exactamente 10 dígitos numéricos'
        };
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(datos.email)) {
        return {
          exito: false,
          error: 'El formato del email es inválido'
        };
      }

      const postulante = new Postulante(
        datos.cedula,
        datos.nombreCompleto,
        datos.email,
        datos.telefono,
        datos.fechaNacimiento
      );

      if (!postulante.validarIdentidad()) {
        return {
          exito: false,
          error: 'La identidad no pudo ser verificada. Verifica que la cédula sea correcta.'
        };
      }

      this.postulantes.set(datos.cedula, postulante);

      return {
        exito: true,
        postulante: {
          id: postulante.idPostulante,
          cedula: postulante.cedula,
          nombre: postulante.nombreCompleto,
          email: postulante.email,
          telefono: postulante.telefono,
          estado: postulante.estadoRegistro,
          edad: postulante.calcularEdad(),
          fechaRegistro: postulante.fechaRegistro
        }
      };

    } catch (error) {
      return {
        exito: false,
        error: error instanceof Error ? error.message : 'Error desconocido al registrar postulante'
      };
    }
  }

  buscarPorCedula(cedula: string): any {
    const postulante = this.postulantes.get(cedula);
    
    if (!postulante) {
      return null;
    }

    return {
      id: postulante.idPostulante,
      cedula: postulante.cedula,
      nombre: postulante.nombreCompleto,
      email: postulante.email,
      telefono: postulante.telefono,
      fechaNacimiento: postulante.fechaNacimiento,
      edad: postulante.calcularEdad(),
      estado: postulante.estadoRegistro,
      fechaRegistro: postulante.fechaRegistro
    };
  }

  buscarPorId(idPostulante: number): any {
    for (const postulante of this.postulantes.values()) {
      if (postulante.idPostulante === idPostulante) {
        return {
          id: postulante.idPostulante,
          cedula: postulante.cedula,
          nombre: postulante.nombreCompleto,
          email: postulante.email,
          telefono: postulante.telefono,
          estado: postulante.estadoRegistro,
          edad: postulante.calcularEdad()
        };
      }
    }
    return null;
  }

  actualizarDatos(cedula: string, datos: {
    email?: string;
    telefono?: string;
  }): { exito: boolean; mensaje: string } {
    
    const postulante = this.postulantes.get(cedula);
    
    if (!postulante) {
      return { 
        exito: false, 
        mensaje: `Postulante con cédula ${cedula} no encontrado` 
      };
    }

    try {
      if (datos.email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(datos.email)) {
          return {
            exito: false,
            mensaje: 'El formato del email es inválido'
          };
        }
      }

      postulante.actualizarDatos(datos.email || null, datos.telefono || null);
      
      return { 
        exito: true, 
        mensaje: 'Datos actualizados correctamente' 
      };

    } catch (error) {
      return {
        exito: false,
        mensaje: error instanceof Error ? error.message : 'Error al actualizar datos'
      };
    }
  }

  listarTodos(): any[] {
    return Array.from(this.postulantes.values()).map((p: any) => ({
      id: p.idPostulante,
      cedula: p.cedula,
      nombre: p.nombreCompleto,
      email: p.email,
      telefono: p.telefono,
      estado: p.estadoRegistro,
      edad: p.calcularEdad(),
      fechaRegistro: p.fechaRegistro
    }));
  }

  listarPorEstado(estado: string): any[] {
    const estadoUpper = estado.toUpperCase();
    
    return Array.from(this.postulantes.values())
      .filter((p: any) => p.estadoRegistro === estadoUpper)
      .map((p: any) => ({
        id: p.idPostulante,
        cedula: p.cedula,
        nombre: p.nombreCompleto,
        email: p.email,
        estado: p.estadoRegistro,
        fechaRegistro: p.fechaRegistro
      }));
  }

  existe(cedula: string): boolean {
    return this.postulantes.has(cedula);
  }

  obtenerTotal(): number {
    return this.postulantes.size;
  }

  obtenerEstadisticas(): any {
    const todos = Array.from(this.postulantes.values());
    
    const porEstado: { [key: string]: number } = {};
    for (const p of todos) {
      porEstado[p.estadoRegistro] = (porEstado[p.estadoRegistro] || 0) + 1;
    }

    const edades = todos.map((p: any) => p.calcularEdad()).filter((e: any) => e !== null) as number[];
    const edadPromedio = edades.length > 0 
      ? edades.reduce((sum: number, e: number) => sum + e, 0) / edades.length 
      : 0;

    return {
      total: this.postulantes.size,
      porEstado,
      edadPromedio: Math.round(edadPromedio),
      verificados: porEstado['VERIFICADO'] || 0,
      pendientes: porEstado['PENDIENTE'] || 0,
      rechazados: porEstado['RECHAZADO'] || 0
    };
  }
}