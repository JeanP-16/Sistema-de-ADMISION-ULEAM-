import { Router, Request, Response } from 'express';
import { AsignacionManager, Asignacion } from '../models/Asignacion';

const router = Router();

// Obtener gestor singleton
const manager = AsignacionManager.obtenerInstancia();

// GET /api/asignaciones - Listar todas
router.get('/', (req: Request, res: Response) => {
  try {
    const asignaciones = manager.obtenerTodasAsignaciones();
    res.json({
      success: true,
      total: asignaciones.length,
      data: asignaciones.map(a => a.obtenerInformacion())
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

// POST /api/asignaciones - Crear nueva
router.post('/', (req: Request, res: Response) => {
  try {
    const { idPostulante, carreraId, sedeId, puntajeTotal, ordenMerito, tipoAsignacion } = req.body;

    const asignacion = new Asignacion(
      idPostulante,
      carreraId,
      sedeId,
      puntajeTotal,
      ordenMerito,
      tipoAsignacion
    );

    const exito = asignacion.asignar();

    res.status(201).json({
      success: exito,
      data: asignacion.obtenerInformacion()
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

// GET /api/asignaciones/:id - Obtener por ID
router.get('/:id', (req: Request, res: Response) => {
  try {
    const id = parseInt(req.params.id as string);
    const asignacion = manager.obtenerAsignacion(id);

    if (!asignacion) {
      return res.status(404).json({
        success: false,
        error: 'Asignación no encontrada'
      });
    }

    res.json({
      success: true,
      data: asignacion.obtenerInformacion()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

export default router;