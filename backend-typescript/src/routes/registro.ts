import { Router, Request, Response } from 'express';
import { RegistroNacionalService } from '../services';

const router = Router();
const registroService = new RegistroNacionalService();

router.post('/basico', async (req: Request, res: Response) => {
  try {
    const resultado = await registroService.crearRegistroBasico(req.body);
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
    const registros = registroService.listarTodos();
    res.json({ exito: true, total: registros.length, data: registros });
  } catch (error) {
    res.status(500).json({
      exito: false,
      error: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

export default router;