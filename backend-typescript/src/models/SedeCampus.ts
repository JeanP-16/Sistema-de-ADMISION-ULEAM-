/**
 * Rutas: Sedes y Campus
 * Endpoints HTTP para gestión de sedes
 */

import { Router, Request, Response } from 'express';

const router = Router();

// ==================== ENDPOINTS ====================

/**
 * POST /api/sedes
 * Crear nueva sede
 */
router.post('/', (req: Request, res: Response) => {
  try {
    const { nombre, ciudad, direccion } = req.body;

    if (!nombre || !ciudad || !direccion) {
      return res.status(400).json({
        exito: false,
        error: 'Faltan campos obligatorios: nombre, ciudad, direccion'
      });
    }

    // Simular creación
    res.status(201).json({
      exito: true,
      mensaje: 'Sede creada exitosamente',
      sede: {
        idSede: Date.now(),
        nombre,
        ciudad,
        direccion,
        capacidadTotal: 0,
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
 * GET /api/sedes
 * Listar todas las sedes
 */
router.get('/', (req: Request, res: Response) => {
  try {
    // Sedes simuladas
    const sedes = [
      {
        idSede: 1,
        nombre: 'Sede Matriz Manta',
        ciudad: 'Manta',
        direccion: 'Av. Circunvalación',
        capacidadTotal: 5000,
        edificios: 5,
        laboratorios: 25
      },
      {
        idSede: 2,
        nombre: 'Sede El Carmen',
        ciudad: 'El Carmen',
        direccion: 'Calle Principal',
        capacidadTotal: 2000,
        edificios: 3,
        laboratorios: 10
      },
      {
        idSede: 3,
        nombre: 'Sede Chone',
        ciudad: 'Chone',
        direccion: 'Av. Eloy Alfaro',
        capacidadTotal: 1500,
        edificios: 2,
        laboratorios: 8
      }
    ];

    res.json({
      exito: true,
      total: sedes.length,
      data: sedes
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/sedes/:id
 * Obtener sede por ID
 */
router.get('/:id', (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    // Simular búsqueda
    res.json({
      exito: true,
      data: {
        idSede: id,
        nombre: 'Sede Matriz Manta',
        ciudad: 'Manta',
        direccion: 'Av. Circunvalación',
        capacidadTotal: 5000,
        edificios: [
          {
            numero: 1,
            nombre: 'Edificio Administrativo',
            laboratorios: 5
          },
          {
            numero: 2,
            nombre: 'Edificio Académico A',
            laboratorios: 10
          }
        ]
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
 * GET /api/sedes/:id/laboratorios
 * Listar laboratorios de una sede
 */
router.get('/:id/laboratorios', (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    // Laboratorios simulados
    const laboratorios = [
      {
        idLaboratorio: 1,
        nombre: 'Lab. Cómputo 1',
        edificio: 'Edificio A',
        capacidad: 30,
        tipo: 'COMPUTO',
        disponible: true
      },
      {
        idLaboratorio: 2,
        nombre: 'Lab. Física',
        edificio: 'Edificio B',
        capacidad: 25,
        tipo: 'FISICA',
        disponible: true
      }
    ];

    res.json({
      exito: true,
      idSede: id,
      total: laboratorios.length,
      data: laboratorios
    });

  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/sedes/ciudad/:ciudad
 * Listar sedes por ciudad
 */
router.get('/ciudad/:ciudad', (req: Request, res: Response) => {
  try {
    const { ciudad } = req.params;

    res.json({
      exito: true,
      ciudad,
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