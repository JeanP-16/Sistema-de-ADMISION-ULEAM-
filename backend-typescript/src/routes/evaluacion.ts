import { Router, Request, Response } from 'express';

const router = Router();

router.post('/', (req: Request, res: Response) => {
  res.status(201).json({ exito: true, mensaje: 'Evaluación creada' });
});

router.get('/', (req: Request, res: Response) => {
  res.json({ exito: true, data: [] });
});

export default router;