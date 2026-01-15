/**
 * Servicio: InscripcionService
 * Gestiona la lógica de negocio para inscripciones
 * Coordina: Inscripcion, validaciones, adaptadores
 */

import { Inscripcion } from '../models/Inscripcion';

export class InscripcionService {
  private inscripciones: Map<number, Inscripcion> = new Map();
  private static readonly JORNADAS_VALIDAS = ['matutina', 'vespertina', 'nocturna'];
  private static readonly MAX_PREFERENCIAS = 3;

  /**
   * Procesar inscripción completa
   */
  async procesarInscripcion(datos: {
    idPostulante: number;
    carreraId: number;
    ordenPreferencia: number;
    sedeId: number;
    jornada: string;
    cedulaPostulante: string;
    emailPostulante: string;
    laboratorioId?: number;
  }): Promise<{ exito: boolean; mensaje: string; inscripcion?: any }> {
    
    try {
      // 1. Validar orden de preferencia
      if (datos.ordenPreferencia < 1 || datos.ordenPreferencia > InscripcionService.MAX_PREFERENCIAS) {
        return {
          exito: false,
          mensaje: `El orden de preferencia debe estar entre 1 y ${InscripcionService.MAX_PREFERENCIAS}`
        };
      }

      // 2. Validar jornada
      const jornada = datos.jornada.toLowerCase();
      if (!InscripcionService.JORNADAS_VALIDAS.includes(jornada)) {
        return {
          exito: false,
          mensaje: `Jornada inválida. Use: ${InscripcionService.JORNADAS_VALIDAS.join(', ')}`
        };
      }

      // 3. Validar que no tenga inscripción duplicada
      const yaInscrito = this.verificarInscripcionDuplicada(
        datos.idPostulante, 
        datos.carreraId
      );

      if (yaInscrito) {
        return {
          exito: false,
          mensaje: 'El postulante ya tiene una inscripción activa en esta carrera'
        };
      }

      // 4. Validar límite de inscripciones
      const totalInscripciones = this.contarInscripcionesPorPostulante(datos.idPostulante);
      if (totalInscripciones >= InscripcionService.MAX_PREFERENCIAS) {
        return {
          exito: false,
          mensaje: `El postulante ya alcanzó el límite de ${InscripcionService.MAX_PREFERENCIAS} inscripciones`
        };
      }

      // 5. Crear inscripción
      const inscripcion = new Inscripcion(
        datos.idPostulante,
        datos.carreraId,
        datos.ordenPreferencia,
        datos.sedeId,
        jornada,
        datos.cedulaPostulante,
        datos.emailPostulante,
        datos.laboratorioId || null
      );

      // 6. Validar requisitos
      if (!inscripcion.validarRequisitos()) {
        return {
          exito: false,
          mensaje: 'No cumple los requisitos para inscribirse. Verifica tu documentación.'
        };
      }

      // 7. Completar inscripción
      inscripcion.completar();

      // 8. Almacenar
      this.inscripciones.set(inscripcion.idInscripcion, inscripcion);

      return {
        exito: true,
        mensaje: 'Inscripción procesada exitosamente',
        inscripcion: {
          id: inscripcion.idInscripcion,
          idPostulante: inscripcion.idPostulante,
          carreraId: inscripcion.carreraId,
          ordenPreferencia: inscripcion.ordenPreferencia,
          estado: inscripcion.estado,
          jornada: inscripcion.jornada,
          comprobante: inscripcion.comprobantePdfUrl,
          fechaInscripcion: inscripcion.fechaInscripcion
        }
      };

    } catch (error) {
      return {
        exito: false,
        mensaje: error instanceof Error ? error.message : 'Error desconocido en inscripción'
      };
    }
  }

  /**
   * Cancelar inscripción
   */
  cancelarInscripcion(idInscripcion: number): { exito: boolean; mensaje: string } {
    const inscripcion = this.inscripciones.get(idInscripcion);
    
    if (!inscripcion) {
      return { 
        exito: false, 
        mensaje: `Inscripción con ID ${idInscripcion} no encontrada` 
      };
    }

    if (inscripcion.estado === 'CANCELADA') {
      return {
        exito: false,
        mensaje: 'La inscripción ya estaba cancelada'
      };
    }

    inscripcion.cancelar();
    
    return { 
      exito: true, 
      mensaje: 'Inscripción cancelada exitosamente' 
    };
  }

  /**
   * Obtener inscripción por ID
   */
  obtenerPorId(idInscripcion: number): any {
    const inscripcion = this.inscripciones.get(idInscripcion);
    
    if (!inscripcion) {
      return null;
    }

    return {
      id: inscripcion.idInscripcion,
      idPostulante: inscripcion.idPostulante,
      carreraId: inscripcion.carreraId,
      ordenPreferencia: inscripcion.ordenPreferencia,
      sedeId: inscripcion.sedeId,
      jornada: inscripcion.jornada,
      laboratorioId: inscripcion.laboratorioId,
      cedulaPostulante: inscripcion.cedulaPostulante,
      emailPostulante: inscripcion.emailPostulante,
      estado: inscripcion.estado,
      comprobante: inscripcion.comprobantePdfUrl,
      fechaInscripcion: inscripcion.fechaInscripcion
    };
  }

  /**
   * Listar inscripciones de un postulante
   */
  listarPorPostulante(idPostulante: number): any[] {
    return Array.from(this.inscripciones.values())
      .filter(i => i.idPostulante === idPostulante)
      .map(i => ({
        id: i.idInscripcion,
        carreraId: i.carreraId,
        ordenPreferencia: i.ordenPreferencia,
        jornada: i.jornada,
        estado: i.estado,
        fechaInscripcion: i.fechaInscripcion
      }));
  }

  /**
   * Listar inscripciones por carrera
   */
  listarPorCarrera(carreraId: number): any[] {
    return Array.from(this.inscripciones.values())
      .filter(i => i.carreraId === carreraId)
      .map(i => ({
        id: i.idInscripcion,
        idPostulante: i.idPostulante,
        ordenPreferencia: i.ordenPreferencia,
        jornada: i.jornada,
        estado: i.estado
      }));
  }

  /**
   * Listar inscripciones por estado
   */
  listarPorEstado(estado: string): any[] {
    const estadoUpper = estado.toUpperCase();
    
    return Array.from(this.inscripciones.values())
      .filter(i => i.estado === estadoUpper)
      .map(i => ({
        id: i.idInscripcion,
        idPostulante: i.idPostulante,
        carreraId: i.carreraId,
        jornada: i.jornada,
        estado: i.estado
      }));
  }

  /**
   * Listar todas las inscripciones
   */
  listarTodas(): any[] {
    return Array.from(this.inscripciones.values()).map(i => ({
      id: i.idInscripcion,
      idPostulante: i.idPostulante,
      carreraId: i.carreraId,
      ordenPreferencia: i.ordenPreferencia,
      estado: i.estado,
      jornada: i.jornada,
      fechaInscripcion: i.fechaInscripcion
    }));
  }

  /**
   * Verificar si existe inscripción duplicada
   */
  private verificarInscripcionDuplicada(idPostulante: number, carreraId: number): boolean {
    for (const inscripcion of this.inscripciones.values()) {
      if (inscripcion.idPostulante === idPostulante && 
          inscripcion.carreraId === carreraId &&
          inscripcion.estado === 'ACTIVA') {
        return true;
      }
    }
    return false;
  }

  /**
   * Contar inscripciones activas de un postulante
   */
  private contarInscripcionesPorPostulante(idPostulante: number): number {
    let count = 0;
    for (const inscripcion of this.inscripciones.values()) {
      if (inscripcion.idPostulante === idPostulante && 
          inscripcion.estado === 'ACTIVA') {
        count++;
      }
    }
    return count;
  }

  /**
   * Obtener estadísticas de inscripciones
   */
  obtenerEstadisticas(): any {
    const todas = Array.from(this.inscripciones.values());
    
    const porEstado: { [key: string]: number } = {};
    const porJornada: { [key: string]: number } = {};
    const porCarrera: { [key: number]: number } = {};

    for (const i of todas) {
      porEstado[i.estado] = (porEstado[i.estado] || 0) + 1;
      porJornada[i.jornada] = (porJornada[i.jornada] || 0) + 1;
      porCarrera[i.carreraId] = (porCarrera[i.carreraId] || 0) + 1;
    }

    return {
      total: this.inscripciones.size,
      porEstado,
      porJornada,
      porCarrera,
      activas: porEstado['ACTIVA'] || 0,
      completadas: porEstado['COMPLETADA'] || 0,
      canceladas: porEstado['CANCELADA'] || 0
    };
  }
}