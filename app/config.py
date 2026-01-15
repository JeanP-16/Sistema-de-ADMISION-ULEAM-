"""
Configuración del Sistema de Admisión ULEAM
Incluye configuración de Flask-Mail para envío de correos
"""

import os

class Config:
    """Configuración base del sistema"""
    
    # Configuración Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sistema_sipu_uleam_2025_clave_secreta'
    
    # Configuración Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # Credenciales de correo (IMPORTANTE: usar variables de entorno en producción)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'florespilosojeanpierre@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'huzd muvp anyv ftud'
    
    # Configuración del remitente
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'admisiones@uleam.edu.ec'
    
    # Configuración adicional
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False
    
    # Ruta del archivo Excel
    EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos_admision.xlsx')


# ========== INSTRUCCIONES PARA CONFIGURAR GMAIL ==========

"""
CONFIGURACIÓN DE GMAIL PARA FLASK-MAIL:

1. Habilitar verificación en dos pasos:
   - Ir a: https://myaccount.google.com/security
   - Buscar "Verificación en dos pasos"
   - Activarla si no está activada

2. Crear contraseña de aplicación:
   - Ir a: https://myaccount.google.com/apppasswords
   - Seleccionar "Correo" y "Otro (nombre personalizado)"
   - Nombrar: "Sistema ULEAM"
   - Copiar la contraseña de 16 caracteres generada

3. Configurar variables de entorno (RECOMENDADO):
   
   En Windows (CMD):
   set MAIL_USERNAME=tu_correo@gmail.com
   set MAIL_PASSWORD=tu_contraseña_de_aplicacion
   
   En Linux/Mac:
   export MAIL_USERNAME=tu_correo@gmail.com
   export MAIL_PASSWORD=tu_contraseña_de_aplicacion
   
   O crear archivo .env:
   MAIL_USERNAME=tu_correo@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop  (contraseña de aplicación, sin espacios)
   MAIL_DEFAULT_SENDER=admisiones@uleam.edu.ec

4. Para desarrollo/pruebas:
   - Editar directamente MAIL_USERNAME y MAIL_PASSWORD arriba
   - NUNCA subir a Git con credenciales reales
   - Usar archivo .gitignore para .env

SEGURIDAD:
- NUNCA uses tu contraseña real de Gmail
- SIEMPRE usa contraseña de aplicación
- NO compartas tus credenciales
- NO subas archivos con credenciales a repositorios públicos

TESTING:
Para probar sin correo real, puedes usar:
- MailHog (servidor SMTP de prueba local)
- Mailtrap (servicio online de prueba)

IMPORTANTE:
Este sistema enviará correos automáticamente cuando:
1. Se registra una evaluación → correo con resultados
2. Se confirma una inscripción → correo de confirmación
3. Se asigna un laboratorio → correo con detalles de asignación
"""
