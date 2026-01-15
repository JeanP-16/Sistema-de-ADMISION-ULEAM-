/**
 * Servicio: AsignacionService
 * Gestiona la lógica de negocio para asignaciones de cupos
 */

import { AsignacionManager, Asignacion } from '../models/Asignacion';

export class AsignacionService {
  private asignacionManager = AsignacionManager.obtenerInstancia();

  async procesarAsignacion(datos: {
    idPostulante: number;
    carreraId: number;
    sedeId: number;
    puntajeTotal: number;
    ordenMerito: number;
    tipoAsignacion?: string;
  }): Promise<{ exito: boolean; mensaje: string; asignacion?: any }> {
    
    try {
      const cuposDisponibles = this.asignacionManager.obtenerCuposDisponibles(datos.carreraId);
      
      if (cuposDisponibles <= 0) {
        return {
          exito: false,
          mensaje: 'No hay cupos disponibles para esta carrera'
        };
      }

      if (datos.puntajeTotal < 600) {
        return {
          exito: false,
          mensaje: `Puntaje insuficiente: ${datos.puntajeTotal}. Mínimo requerido: 600 puntos`
        };
      }

      const asignacion = new Asignacion(
        datos.idPostulante,
        datos.carreraId,
        datos.sedeId,
        datos.puntajeTotal,
        datos.ordenMerito,
        datos.tipoAsignacion || 'PRIMERA_OPCION'
      );

      const exito = asignacion.asignar();

      if (exito) {
        return {
          exito: true,
          mensaje: 'Asignación realizada exitosamente',
          asignacion: asignacion.obtenerInformacion()
        };
      } else {
        return {
          exito: false,
          mensaje: 'No se pudo completar la asignación. Verifica requisitos.'
        };
      }

    } catch (error) {
      return {
        exito: false,
        mensaje: error instanceof Error ? error.message : 'Error desconocido en asignación'
      };
    }
  }

  configurarCupos(carreraId: number, cupos: number): void {
    if (cupos < 0) {
      throw new Error('Los cupos no pueden ser negativos');
    }
    this.asignacionManager.configurarCupos(carreraId, cupos);
  }

  obtenerAsignacionPorId(idAsignacion: number): any {
    const asignacion = this.asignacionManager.obtenerAsignacion(idAsignacion);
    return asignacion ? asignacion.obtenerInformacion() : null;
  }

  listarTodas(): any[] {
    return this.asignacionManager.obtenerTodasAsignaciones()
      .map((a: any) => a.obtenerInformacion());
  }

  listarPorEstado(estado: string): any[] {
    const estadoUpper = estado.toUpperCase();
    const todas = this.asignacionManager.obtenerTodasAsignaciones();
    
    return todas
      .filter((a: any) => a.estado === estadoUpper)
      .map((a: any) => a.obtenerInformacion());
  }

  listarPorPostulante(idPostulante: number): any[] {
    const todas = this.asignacionManager.obtenerTodasAsignaciones();
    
    return todas
      .filter((a: any) => a.idPostulante === idPostulante)
      .map((a: any) => a.obtenerInformacion());
  }

  cancelarAsignacion(idAsignacion: number): { exito: boolean; mensaje: string } {
    const asignacion = this.asignacionManager.obtenerAsignacion(idAsignacion);
    
    if (!asignacion) {
      return { 
        exito: false, 
        mensaje: `Asignación con ID ${idAsignacion} no encontrada` 
      };
    }

    if (asignacion.estado === 'CANCELADO') {
      return { 
        exito: false, 
        mensaje: 'La asignación ya estaba cancelada' 
      };
    }

    asignacion.cancelar();
    
    return { 
      exito: true, 
      mensaje: 'Asignación cancelada exitosamente. Cupo devuelto.' 
    };
  }

  obtenerEstadisticas(): any {
    return this.asignacionManager.obtenerEstadisticas();
  }

  obtenerCuposDisponibles(carreraId: number): number {
    return this.asignacionManager.obtenerCuposDisponibles(carreraId);
  }

  tieneAsignacion(idPostulante: number): boolean {
    const asignaciones = this.listarPorPostulante(idPostulante);
    return asignaciones.some((a: any) => a.estado === 'ASIGNADO');
  }

  obtenerRanking(carreraId?: number): any[] {
    let asignaciones = this.asignacionManager.obtenerTodasAsignaciones();
    
    if (carreraId) {
      asignaciones = asignaciones.filter((a: any) => a.carreraId === carreraId);
    }

    return asignaciones
      .sort((a: any, b: any) => b.puntajeTotal - a.puntajeTotal)
      .map((a: any, index: number) => ({
        posicion: index + 1,
        idPostulante: a.idPostulante,
        carreraId: a.carreraId,
        puntajeTotal: a.puntajeTotal,
        estado: a.estado
      }));
  }
}