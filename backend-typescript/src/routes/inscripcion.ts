import { Router, Request, Response } from 'express';
import { InscripcionService } from '../services';

const router = Router();
const inscripcionService = new InscripcionService();

router.post('/', async (req: Request, res: Response) => {
  try {
    const resultado = await inscripcionService.procesarInscripcion(req.body);
    if (resultado.exito) {
      res.status(201).json(resultado);
    } else {
      res.status(400).json(resultado);
    }
  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

router.get('/', (req: Request, res: Response) => {
  try {
    const inscripciones = inscripcionService.listarTodas();
    res.json({ exito: true, total: inscripciones.length, data: inscripciones });
  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

export default router;