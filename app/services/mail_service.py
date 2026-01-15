"""
Servicio de Correo Electrónico - Sistema de Admisión ULEAM
Gestiona el envío de correos para evaluaciones, inscripciones y asignaciones
"""

from flask_mail import Message
from datetime import datetime


class MailService:
    """
    Servicio de envío de correos electrónicos
    """
    
    def __init__(self, mail_instance):
        """
        Inicializa el servicio
        
        Args:
            mail_instance: Instancia de Flask-Mail
        """
        self.mail = mail_instance
    
    def _crear_template_base(self, titulo, contenido):
        """
        Crea template HTML base para correos
        
        Args:
            titulo: Título del correo
            contenido: Contenido HTML del cuerpo
            
        Returns:
            str: HTML completo
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    margin: 20px auto;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 0;
                    font-size: 14px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .info-box {{
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .info-box h3 {{
                    margin: 0 0 10px 0;
                    color: #667eea;
                    font-size: 16px;
                }}
                .info-box p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .success {{
                    color: #28a745;
                    font-weight: bold;
                }}
                .warning {{
                    color: #ffc107;
                    font-weight: bold;
                }}
                .danger {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #666;
                    font-size: 12px;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #eee;
                    margin: 20px 0;
                }}
                strong {{
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 ULEAM</h1>
                    <p>Sistema de Admisión Universitaria</p>
                    <p style="font-size: 18px; margin-top: 10px;">{titulo}</p>
                </div>
                <div class="content">
                    {contenido}
                </div>
                <div class="footer">
                    <p><strong>Universidad Laica Eloy Alfaro de Manabí</strong></p>
                    <p>Sistema de Admisión {datetime.now().year}</p>
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def enviar_confirmacion_evaluacion(self, destinatario, datos_estudiante, datos_evaluacion):
        """
        Envía correo de confirmación de evaluación
        
        Args:
            destinatario: Email del estudiante
            datos_estudiante: Dict con nombre, cedula, etc
            datos_evaluacion: Dict con notas y puntajes
            
        Returns:
            tuple: (bool exito, str mensaje)
        """
        nombre = self._obtener_nombre_estudiante(datos_estudiante)
        
        contenido = f"""
        <h2 style="color: #667eea;">Resultados de Evaluación</h2>
        <p>Estimado/a <strong>{nombre}</strong>,</p>
        <p>Nos complace informarle que su evaluación ha sido procesada exitosamente.</p>
        
        <div class="info-box">
            <h3>📋 Datos del Postulante</h3>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Cédula:</strong> {datos_estudiante.get('cedula', 'N/A')}</p>
            <p><strong>Email:</strong> {destinatario}</p>
        </div>
        
        <div class="info-box">
            <h3>📝 Resultados de Evaluación</h3>
            <p><strong>Razonamiento Verbal:</strong> {datos_evaluacion.get('nota_verbal', 0)}/10</p>
            <p><strong>Razonamiento Numérico:</strong> {datos_evaluacion.get('nota_numerica', 0)}/10</p>
            <p><strong>Razonamiento Abstracto:</strong> {datos_evaluacion.get('nota_abstracta', 0)}/10</p>
            <hr>
            <p class="success"><strong>Puntaje Total:</strong> {datos_evaluacion.get('puntaje_total', 0)}/1000</p>
            <p><strong>Estado:</strong> <span class="success">{datos_evaluacion.get('estado', 'N/A')}</span></p>
        </div>
        
        <p>Puede consultar su asignación de laboratorio ingresando al sistema con su cédula.</p>
        
        <p><strong>¡Felicitaciones por completar esta etapa del proceso!</strong></p>
        """
        
        html_completo = self._crear_template_base("Resultados de Evaluación", contenido)
        
        try:
            msg = Message(
                subject=f"ULEAM - Resultados de Evaluación - {datos_estudiante.get('cedula', '')}",
                recipients=[destinatario],
                html=html_completo
            )
            self.mail.send(msg)
            return True, "Correo de evaluación enviado exitosamente"
        except Exception as e:
            return False, f"Error al enviar correo: {str(e)}"
    
    def enviar_confirmacion_inscripcion(self, destinatario, datos_estudiante, datos_inscripcion):
        """
        Envía correo de confirmación de inscripción
        
        Args:
            destinatario: Email del estudiante
            datos_estudiante: Dict con datos personales
            datos_inscripcion: Dict con carrera, jornada, etc
            
        Returns:
            tuple: (bool exito, str mensaje)
        """
        nombre = self._obtener_nombre_estudiante(datos_estudiante)
        
        # Mapeo de jornadas con horarios
        jornadas_info = {
            'Matutina': '07:00 - 12:00',
            'MATUTINA': '07:00 - 12:00',
            'Vespertina': '13:00 - 18:00',
            'VESPERTINA': '13:00 - 18:00',
            'Nocturna': '18:00 - 22:00',
            'NOCTURNA': '18:00 - 22:00'
        }
        
        jornada = datos_inscripcion.get('jornada', 'N/A')
        horario = jornadas_info.get(jornada, 'Por definir')
        
        contenido = f"""
        <h2 style="color: #667eea;">Confirmación de Inscripción</h2>
        <p>Estimado/a <strong>{nombre}</strong>,</p>
        <p>Su inscripción ha sido registrada exitosamente en nuestro sistema.</p>
        
        <div class="info-box">
            <h3>👤 Datos Personales</h3>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Cédula:</strong> {datos_estudiante.get('cedula', 'N/A')}</p>
            <p><strong>Email:</strong> {destinatario}</p>
            <p><strong>Celular:</strong> {datos_estudiante.get('celular', 'N/A')}</p>
        </div>
        
        <div class="info-box">
            <h3>📚 Información de Inscripción</h3>
            <p><strong>Carrera:</strong> {datos_inscripcion.get('carrera_nombre', 'N/A')}</p>
            <p><strong>Código de Carrera:</strong> {datos_inscripcion.get('carrera_id', 'N/A')}</p>
            <p><strong>Jornada:</strong> {jornada} ({horario})</p>
            <p><strong>Fecha de Inscripción:</strong> {datos_inscripcion.get('fecha_inscripcion', 'N/A')}</p>
            <p><strong>Estado:</strong> <span class="success">{datos_inscripcion.get('estado', 'N/A')}</span></p>
        </div>
        
        <h3 style="color: #667eea;">📌 Próximos Pasos:</h3>
        <ol>
            <li>Realizar la evaluación SENESCYT (si aún no la has completado)</li>
            <li>Consultar la asignación de laboratorio en el sistema</li>
            <li>Presentarse el día indicado con 30 minutos de anticipación</li>
        </ol>
        
        <p class="warning"><strong>IMPORTANTE:</strong> Conserve este correo como comprobante de inscripción.</p>
        """
        
        html_completo = self._crear_template_base("Confirmación de Inscripción", contenido)
        
        try:
            msg = Message(
                subject=f"ULEAM - Confirmación de Inscripción - {datos_inscripcion.get('carrera_nombre', '')}",
                recipients=[destinatario],
                html=html_completo
            )
            self.mail.send(msg)
            return True, "Correo de inscripción enviado exitosamente"
        except Exception as e:
            return False, f"Error al enviar correo: {str(e)}"
    
    def enviar_asignacion_laboratorio(self, destinatario, datos_estudiante, datos_asignacion):
        """
        Envía correo con detalles de asignación de laboratorio
        
        Args:
            destinatario: Email del estudiante
            datos_estudiante: Dict con datos personales
            datos_asignacion: Dict con laboratorio, fecha, hora, etc
            
        Returns:
            tuple: (bool exito, str mensaje)
        """
        nombre = self._obtener_nombre_estudiante(datos_estudiante)
        
        # Mapeo de carreras
        carreras_info = {
            101: 'Tecnologías de Información',
            102: 'Medicina',
            103: 'Ingeniería Civil',
            104: 'Administración',
            105: 'Derecho'
        }
        
        carrera_id = datos_asignacion.get('carrera_id', 0)
        carrera_nombre = carreras_info.get(int(carrera_id) if carrera_id else 0, 'No especificada')
        
        contenido = f"""
        <h2 style="color: #667eea;">Asignación de Laboratorio</h2>
        <p>Estimado/a <strong>{nombre}</strong>,</p>
        <p>Se le ha asignado un laboratorio para la evaluación presencial.</p>
        
        <div class="info-box">
            <h3>👤 Datos del Postulante</h3>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Cédula:</strong> {datos_estudiante.get('cedula', 'N/A')}</p>
            <p><strong>Email:</strong> {destinatario}</p>
        </div>
        
        <div class="info-box">
            <h3>📍 Información de Asignación</h3>
            <p><strong>Carrera:</strong> {carrera_nombre}</p>
            <p><strong>Edificio:</strong> {datos_asignacion.get('edificio', 'N/A')}</p>
            <p><strong>Laboratorio:</strong> {datos_asignacion.get('laboratorio', 'N/A')}</p>
            <p><strong>Sede:</strong> Sede {datos_asignacion.get('sede_id', 'N/A')} - Matriz Manta</p>
        </div>
        
        <div class="info-box">
            <h3>📅 Fecha y Hora</h3>
            <p><strong>Fecha del Examen:</strong> {datos_asignacion.get('fecha_examen', 'N/A')}</p>
            <p><strong>Hora de Inicio:</strong> {datos_asignacion.get('hora_inicio', 'N/A')}</p>
            <p class="warning"><strong>⚠️ Llegue 30 minutos antes</strong></p>
        </div>
        
        <h3 style="color: #667eea;">📋 Requisitos:</h3>
        <ul>
            <li>Presentar cédula de identidad original</li>
            <li>Llegar puntualmente (30 minutos antes)</li>
            <li>Traer lápiz, borrador y calculadora (si aplica)</li>
            <li>No se permite el ingreso de celulares</li>
        </ul>
        
        <p class="danger"><strong>IMPORTANTE:</strong> No se permitirá el ingreso después de la hora establecida.</p>
        
        <p><strong>Le deseamos mucho éxito en su evaluación.</strong></p>
        """
        
        html_completo = self._crear_template_base("Asignación de Laboratorio", contenido)
        
        try:
            msg = Message(
                subject=f"ULEAM - Asignación de Laboratorio - {datos_asignacion.get('fecha_examen', '')}",
                recipients=[destinatario],
                html=html_completo
            )
            self.mail.send(msg)
            return True, "Correo de asignación enviado exitosamente"
        except Exception as e:
            return False, f"Error al enviar correo: {str(e)}"
    
    def enviar_notificacion_admin(self, destinatario, accion, detalles):
        """
        Envía notificación al administrador sobre acciones del sistema
        
        Args:
            destinatario: Email del administrador
            accion: Tipo de acción (INSERT, UPDATE, DELETE)
            detalles: Dict con información de la acción
            
        Returns:
            tuple: (bool exito, str mensaje)
        """
        acciones_texto = {
            'INSERT': 'Nuevo Registro Creado',
            'UPDATE': 'Registro Actualizado',
            'DELETE': 'Registro Eliminado'
        }
        
        titulo = acciones_texto.get(accion, 'Notificación del Sistema')
        
        contenido = f"""
        <h2 style="color: #667eea;">{titulo}</h2>
        <p>Se ha realizado una modificación en el sistema de admisión.</p>
        
        <div class="info-box">
            <h3>📊 Detalles de la Acción</h3>
            <p><strong>Acción:</strong> {accion}</p>
            <p><strong>Fecha/Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Cédula afectada:</strong> {detalles.get('cedula', 'N/A')}</p>
            <p><strong>Nombre:</strong> {detalles.get('nombre', 'N/A')}</p>
        </div>
        
        <p>Esta es una notificación automática del sistema.</p>
        """
        
        html_completo = self._crear_template_base(titulo, contenido)
        
        try:
            msg = Message(
                subject=f"ULEAM - {titulo}",
                recipients=[destinatario],
                html=html_completo
            )
            self.mail.send(msg)
            return True, "Notificación enviada al administrador"
        except Exception as e:
            return False, f"Error al enviar notificación: {str(e)}"
    
    def _obtener_nombre_estudiante(self, datos):
        """
        Obtiene el nombre completo del estudiante
        
        Args:
            datos: Dict con datos del estudiante
            
        Returns:
            str: Nombre completo
        """
        partes = [
            datos.get('primer_nombre', ''),
            datos.get('segundo_nombre', ''),
            datos.get('apellido_paterno', ''),
            datos.get('apellido_materno', '')
        ]
        
        nombre = ' '.join([p for p in partes if p]).strip()
        
        return nombre if nombre else 'Estudiante'
    
    def test_conexion(self, email_destino):
        """
        Envía correo de prueba para verificar configuración
        
        Args:
            email_destino: Email para prueba
            
        Returns:
            tuple: (bool exito, str mensaje)
        """
        contenido = """
        <h2 style="color: #667eea;">Correo de Prueba</h2>
        <p>Este es un correo de prueba del Sistema de Admisión ULEAM.</p>
        
        <div class="info-box">
            <h3>✅ Configuración Correcta</h3>
            <p>Si estás viendo este correo, significa que la configuración de Flask-Mail está funcionando correctamente.</p>
        </div>
        
        <p><strong>El sistema está listo para enviar notificaciones automáticas.</strong></p>
        """
        
        html_completo = self._crear_template_base("Prueba de Conexión", contenido)
        
        try:
            msg = Message(
                subject="ULEAM - Correo de Prueba",
                recipients=[email_destino],
                html=html_completo
            )
            self.mail.send(msg)
            return True, "Correo de prueba enviado exitosamente"
        except Exception as e:
            return False, f"Error al enviar correo de prueba: {str(e)}"
