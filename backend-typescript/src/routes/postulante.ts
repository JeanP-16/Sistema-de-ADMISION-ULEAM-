import { Router, Request, Response } from 'express';
import { PostulanteService } from '../services';

const router = Router();
const postulanteService = new PostulanteService();

router.post('/', async (req: Request, res: Response) => {
  try {
    const { cedula, nombreCompleto, email, telefono, fechaNacimiento } = req.body;

    if (!cedula || !nombreCompleto || !email || !telefono || !fechaNacimiento) {
      return res.status(400).json({
        exito: false,
        error: 'Faltan campos obligatorios'
      });
    }

    const resultado = await postulanteService.registrarPostulante({
      cedula, nombreCompleto, email, telefono, fechaNacimiento
    });

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
    const postulantes = postulanteService.listarTodos();
    res.json({ exito: true, total: postulantes.length, data: postulantes });
  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

export default router;