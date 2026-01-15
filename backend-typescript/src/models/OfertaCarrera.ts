/**
 * Rutas: Oferta de Carreras
 * Endpoints HTTP para gestión de ofertas académicas
 */

import { Router, Request, Response } from 'express';

const router = Router();

// ==================== ENDPOINTS ====================

/**
 * POST /api/ofertas-carrera
 * Crear nueva oferta de carrera
 */
router.post('/', (req: Request, res: Response) => {
  try {
    const {
      carreraId,
      nombreCarrera,
      facultad,
      cuposTotal,
      modalidad,
      tipo,
      duracion
    } = req.body;

    if (!carreraId || !nombreCarrera || !facultad || !cuposTotal || 
        !modalidad || !tipo || !duracion) {
      return res.status(400).json({
        exito: false,
        error: 'Faltan campos obligatorios'
      });
    }

    // Simular creación (implementar lógica real después)
    res.status(201).json({
      exito: true,
      mensaje: 'Oferta de carrera creada',
      oferta: {
        idOferta: Date.now(),
        carreraId,
        nombreCarrera,
        facultad,
        cuposTotal,
        cuposDisponibles: cuposTotal,
        modalidad,
        tipo,
        duracion,
        estado: 'ACTIVA',
        fechaCreacion: new Date().toISOString()
      }
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/ofertas-carrera
 * Listar todas las ofertas
 */
router.get('/', (req: Request, res: Response) => {
  try {
    // Ofertas simuladas
    const ofertas = [
      {
        idOferta: 1,
        carreraId: 101,
        nombreCarrera: 'Tecnologías de Información',
        facultad: 'Ingeniería',
        cuposTotal: 50,
        cuposDisponibles: 35,
        modalidad: 'PRESENCIAL',
        tipo: 'PREGRADO',
        duracion: 8,
        estado: 'ACTIVA'
      },
      {
        idOferta: 2,
        carreraId: 102,
        nombreCarrera: 'Medicina',
        facultad: 'Ciencias de la Salud',
        cuposTotal: 40,
        cuposDisponibles: 10,
        modalidad: 'PRESENCIAL',
        tipo: 'PREGRADO',
        duracion: 12,
        estado: 'ACTIVA'
      }
    ];

    res.json({
      exito: true,
      total: ofertas.length,
      data: ofertas
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/ofertas-carrera/:id
 * Obtener oferta por ID
 */
router.get('/:id', (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    // Simular búsqueda
    res.json({
      exito: true,
      data: {
        idOferta: id,
        carreraId: 101,
        nombreCarrera: 'Tecnologías de Información',
        facultad: 'Ingeniería',
        cuposTotal: 50,
        cuposDisponibles: 35,
        modalidad: 'PRESENCIAL',
        tipo: 'PREGRADO',
        estado: 'ACTIVA'
      }
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/ofertas-carrera/facultad/:facultad
 * Listar ofertas por facultad
 */
router.get('/facultad/:facultad', (req: Request, res: Response) => {
  try {
    const { facultad } = req.params;

    res.json({
      exito: true,
      facultad,
      total: 0,
      data: []
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/ofertas-carrera/tipo/:tipo
 * Listar ofertas por tipo (PREGRADO/POSGRADO)
 */
router.get('/tipo/:tipo', (req: Request, res: Response) => {
  try {
    const { tipo } = req.params;

    res.json({
      exito: true,
      tipo: typeof tipo === 'string' ? tipo.toUpperCase() : tipo[0].toUpperCase(),
      total: 0,
      data: []
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

export default router;