/**
 * Servidor Principal - TypeScript API
 * Sistema de Admisión ULEAM
 * Puerto: 3000
 */

import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';

// Importar rutas
// Importar rutas
import asignacionRoutes from './routes/asignacion';
import postulanteRoutes from './routes/postulante';
import inscripcionRoutes from './routes/inscripcion';
import registroRoutes from './routes/registro';
import evaluacionRoutes from './routes/evaluacion';
import ofertaCarreraRoutes from './routes/ofertaCarrera';
import sedeCampusRoutes from './routes/sedeCampus';

// Configuración
const app: Application = express();
const PORT = process.env.PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:5000';

// ==================== MIDDLEWARES ====================

// CORS - Permitir conexión desde Flask
app.use(cors({
  origin: [FLASK_URL, 'http://localhost:5000', 'http://127.0.0.1:5000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Parser JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logger simple
app.use((req: Request, res: Response, next: NextFunction) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// ==================== RUTAS ====================

// Ruta raíz
app.get('/', (req: Request, res: Response) => {
  res.json({
    servicio: 'TypeScript API - Sistema Admisión ULEAM',
    version: '1.0.0',
    estado: 'Activo',
    timestamp: new Date().toISOString(),
    endpoints: {
      asignaciones: '/api/asignaciones',
      postulantes: '/api/postulantes',
      inscripciones: '/api/inscripciones',
      registros: '/api/registros',
      evaluaciones: '/api/evaluaciones',
      ofertas: '/api/ofertas-carrera',
      sedes: '/api/sedes'
    }
  });
});

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ 
    status: 'OK',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// API Routes
app.use('/api/asignaciones', asignacionRoutes);
app.use('/api/postulantes', postulanteRoutes);
app.use('/api/inscripciones', inscripcionRoutes);
app.use('/api/registros', registroRoutes);
app.use('/api/evaluaciones', evaluacionRoutes);
app.use('/api/ofertas-carrera', ofertaCarreraRoutes);
app.use('/api/sedes', sedeCampusRoutes);

// ==================== MANEJO DE ERRORES ====================

// Ruta no encontrada
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Endpoint no encontrado',
    path: req.path,
    metodo: req.method
  });
});

// Error handler global
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Error:', err.stack);
  res.status(500).json({
    error: 'Error interno del servidor',
    mensaje: err.message,
    timestamp: new Date().toISOString()
  });
});

// ==================== INICIAR SERVIDOR ====================

app.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 SERVIDOR TYPESCRIPT INICIADO');
  console.log('='.repeat(60));
  console.log(`📡 Puerto: ${PORT}`);
  console.log(`🌐 URL: http://localhost:${PORT}`);
  console.log(`🔗 Flask: ${FLASK_URL}`);
  console.log(`✅ Health check: http://localhost:${PORT}/health`);
  console.log('='.repeat(60));
  console.log('\n📋 Endpoints disponibles:');
  console.log(`   POST   /api/asignaciones`);
  console.log(`   GET    /api/asignaciones`);
  console.log(`   POST   /api/postulantes`);
  console.log(`   GET    /api/postulantes`);
  console.log(`   POST   /api/inscripciones`);
  console.log(`   GET    /api/inscripciones`);
  console.log(`   POST   /api/registros`);
  console.log(`   GET    /api/registros`);
  console.log(`   POST   /api/evaluaciones`);
  console.log(`   GET    /api/evaluaciones`);
  console.log(`   GET    /api/ofertas-carrera`);
  console.log(`   GET    /api/sedes`);
  console.log('='.repeat(60) + '\n');
});

export default app;