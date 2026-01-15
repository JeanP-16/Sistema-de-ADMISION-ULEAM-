"""
Sistema de Admisión ULEAM - Versión con Excel y Flask-Mail
Implementa roles (Admin/Estudiante) y operaciones CRUD sobre Excel
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail
import requests

TYPESCRIPT_API = "http://localhost:3000"

from database.excel_manager import ExcelManager
from services.mail_service import MailService as EmailService
from config import Config
import os


def llamar_typescript(endpoint, metodo='GET', datos=None):
    """
    Llama al servidor TypeScript
    """
    url = f"{TYPESCRIPT_API}{endpoint}"
    
    try:
        if metodo == 'GET':
            respuesta = requests.get(url)
        elif metodo == 'POST':
            respuesta = requests.post(url, json=datos)
        
        return respuesta.json()
    except Exception as e:
        print(f"Error llamando a TypeScript: {e}")
        return {'exito': False, 'error': str(e)}

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar Flask-Mail
mail = Mail(app)

# Inicializar gestor de Excel
db = ExcelManager(app.config['EXCEL_PATH'])

# Inicializar servicio de email
email_service = EmailService(mail)

# ========== RUTAS PÚBLICAS ==========

@app.route('/')
def index():
    """Página principal - Réplica del sistema de admisión"""
    return render_template('Replica_ADMISION_ULEAM.html')

@app.route('/login', methods=['POST'])
def login():
    """Maneja el inicio de sesión"""
    cedula = request.form.get('usuario', '').strip()
    
    # Validar formato de cédula
    if not cedula or len(cedula) != 10 or not cedula.isdigit():
        flash('Cédula inválida. Debe contener exactamente 10 dígitos', 'error')
        return redirect(url_for('index'))
    
    # Verificar si es administrador
    if db.es_administrador(cedula):
        admin_info = db.obtener_info_administrador(cedula)
        session['cedula'] = cedula
        session['nombre'] = admin_info['nombre_completo']
        session['rol'] = 'ADMIN'
        session['email'] = admin_info['email']
        return redirect(url_for('dashboard'))
    
    # Verificar si es estudiante registrado
    elif db.existe_registro(cedula):
        registro = db.obtener_registro_por_cedula(cedula)
        nombre_completo = f"{registro['primer_nombre']} {registro['apellido_paterno']}"
        session['cedula'] = cedula
        session['nombre'] = nombre_completo
        session['rol'] = 'ESTUDIANTE'
        session['email'] = registro['correo']
        session['estado'] = registro['estado']  # IMPORTANTE: Guardar estado
        return redirect(url_for('dashboard'))
    
    else:
        flash('Cédula no encontrada en el sistema', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - muestra opciones según el rol"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', 
                         cedula=session['cedula'],
                         nombre=session['nombre'],
                         rol=session.get('rol', 'ESTUDIANTE'),
                         estado=session.get('estado', 'PENDIENTE'))

# ========================================
# OPCIÓN 1: VER SEDES (Desde Excel)
# ========================================
@app.route('/opcion1')
def opcion1():
    """Muestra todas las sedes desde la base de datos Excel"""
    if 'cedula' not in session:
        flash('Debe iniciar sesión', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Obtener sedes desde Excel
        sedes = db.obtener_todas_sedes()
        
        if not sedes:
            flash('No hay sedes registradas en el sistema', 'warning')
        
        return render_template('sedes.html',
                             sedes=sedes,
                             cedula=session.get('cedula'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    except Exception as e:
        flash(f'Error al cargar sedes: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


# ========================================
# OPCIÓN 2: VER CARRERAS (Desde Excel)
# ========================================
@app.route('/opcion2')
def opcion2():
    """Muestra todas las carreras desde la base de datos Excel"""
    if 'cedula' not in session:
        flash('Debe iniciar sesión', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Obtener carreras desde Excel
        carreras = db.obtener_todas_carreras()
        
        if not carreras:
            flash('No hay carreras registradas en el sistema', 'warning')
        
        # Agrupar por facultad
        carreras_por_facultad = {}
        for carrera in carreras:
            facultad = carrera['facultad']
            if facultad not in carreras_por_facultad:
                carreras_por_facultad[facultad] = []
            carreras_por_facultad[facultad].append(carrera)
        
        return render_template('carreras.html',
                             carreras=carreras,
                             carreras_por_facultad=carreras_por_facultad,
                             cedula=session.get('cedula'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    except Exception as e:
        flash(f'Error al cargar carreras: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


# ========================================
# RUTA ADICIONAL: Buscar carreras por facultad
# ========================================
@app.route('/buscar_carreras', methods=['GET'])
def buscar_carreras():
    """Busca carreras por facultad"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    facultad = request.args.get('facultad', '')
    
    if facultad:
        carreras = db.buscar_carreras_por_facultad(facultad)
    else:
        carreras = db.obtener_todas_carreras()
    
    return render_template('carreras.html',
                         carreras=carreras,
                         cedula=session.get('cedula'),
                         nombre=session.get('nombre'),
                         rol=session.get('rol'))

# ========== OPCIÓN 3: VERIFICAR REGISTRO (CON CRUD PARA ADMIN) ==========

@app.route('/opcion3', methods=['GET', 'POST'])
def opcion3():
    """
    Verificar Registro Nacional
    - Estudiante: Solo ve su información (sin opciones de crear/editar)
    - Administrador: CRUD completo (Insertar, Modificar, Eliminar)
    """
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    rol = session.get('rol', 'ESTUDIANTE')
    
    # POST: Buscar registro por cédula
    if request.method == 'POST':
        cedula_buscar = request.form.get('cedula_buscar', '').strip()
        
        if not cedula_buscar:
            flash('Debe ingresar una cédula', 'error')
            return redirect(url_for('opcion3'))
        
        registro = db.obtener_registro_por_cedula(cedula_buscar)
        
        if not registro:
            flash('Registro no encontrado en la base de datos', 'error')
            # ADMIN puede crear, ESTUDIANTE no
            if rol == 'ADMIN':
                return redirect(url_for('opcion3_crear', cedula=cedula_buscar))
            else:
                return redirect(url_for('opcion3'))
        
        # Mostrar registro encontrado
        nombre_completo = f"{registro['primer_nombre']} {registro.get('segundo_nombre', '')} {registro['apellido_paterno']} {registro['apellido_materno']}".strip()
        
        html = f"""
        <style>
            body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .info-row {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; border: none; cursor: pointer; }}
            .btn-danger {{ background: #dc3545; }}
            .btn:hover {{ opacity: 0.9; }}
            h1 {{ color: #333; }}
            .label {{ font-weight: bold; color: #555; }}
            .estado-completo {{ color: green; font-weight: bold; }}
            .estado-pendiente {{ color: orange; font-weight: bold; }}
        </style>
        <div class='container'>
            <h1>✅ Registro Encontrado</h1>
            <div class='info-row'><span class='label'>Nombre Completo:</span> {nombre_completo}</div>
            <div class='info-row'><span class='label'>Cédula:</span> {registro['cedula']}</div>
            <div class='info-row'><span class='label'>Email:</span> {registro['correo']}</div>
            <div class='info-row'><span class='label'>Celular:</span> {registro['celular']}</div>
            <div class='info-row'><span class='label'>Calificación:</span> {registro['calificacion']}/10</div>
            <div class='info-row'><span class='label'>Cuadro de Honor:</span> {registro['cuadro_honor']}</div>
            <div class='info-row'><span class='label'>Estado:</span> <span class='estado-{'completo' if registro['estado'] == 'COMPLETO' else 'pendiente'}'>{registro['estado']}</span></div>
            <div class='info-row'><span class='label'>Fecha Registro:</span> {registro['fecha_registro']}</div>
            <br>
        """
        
        # Solo ADMIN puede editar/eliminar
        if rol == 'ADMIN':
            html += f"""
            <a href='/opcion3_editar/{registro['cedula']}' class='btn'>✏️ Modificar</a>
            <a href='/opcion3_eliminar/{registro['cedula']}' class='btn btn-danger' onclick="return confirm('¿Está seguro de eliminar este registro?')">🗑️ Eliminar</a>
            """
        
        html += """
            <a href='/opcion3' class='btn'>← Nueva búsqueda</a>
            <a href='/dashboard' class='btn'>← Volver al menú</a>
        </div>
        """
        
        return html
    
    # GET: Mostrar formulario de búsqueda
    # Si es ESTUDIANTE, pre-llenar con su cédula
    cedula_default = session['cedula'] if rol == 'ESTUDIANTE' else ''
    
    html = f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        input[type='text'] {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }}
        .btn:hover {{ background: #5568d3; }}
        .btn-secondary {{ background: #6c757d; margin-top: 10px; }}
        h1 {{ color: #333; }}
    </style>
    <div class='container'>
        <h1>🔍 Verificar Registro Nacional</h1>
        <p>Busca registros en la base de datos Excel</p>
        <form method='POST'>
            <label><strong>Ingrese número de cédula:</strong></label>
            <input type='text' name='cedula_buscar' required pattern='[0-9]{{10}}' 
                   placeholder='Ej: 1316202082' value='{cedula_default}'>
            <button type='submit' class='btn'>Buscar en Base de Datos</button>
        </form>
    """
    
    # Solo ADMIN puede crear nuevos registros
    if rol == 'ADMIN':
        html += """
        <br>
        <a href='/opcion3_crear' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>➕ Crear Nuevo Registro</a>
        """
    
    html += """
        <br>
        <a href='/dashboard' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>← Volver al menú</a>
    </div>
    """
    
    return html

@app.route('/opcion3_crear', methods=['GET', 'POST'])
def opcion3_crear():
    """Crear nuevo registro (solo Admin)"""
    if session.get('rol') != 'ADMIN':
        flash('Acceso denegado. Solo administradores pueden crear registros.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        datos = {
            'cedula': request.form.get('cedula', '').strip(),
            'primer_nombre': request.form.get('primer_nombre', '').strip().upper(),
            'segundo_nombre': request.form.get('segundo_nombre', '').strip().upper(),
            'apellido_paterno': request.form.get('apellido_paterno', '').strip().upper(),
            'apellido_materno': request.form.get('apellido_materno', '').strip().upper(),
            'correo': request.form.get('correo', '').strip().lower(),
            'celular': request.form.get('celular', '').strip(),
            'calificacion': request.form.get('calificacion', '0'),
            'cuadro_honor': request.form.get('cuadro_honor', 'NO'),
            'estado': request.form.get('estado', 'PENDIENTE')
        }
        
        exito, mensaje = db.insertar_registro(datos)
        
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('opcion3'))
        else:
            flash(mensaje, 'error')
    
    cedula_param = request.args.get('cedula', '')
    
    return f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        input, select {{ width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; margin-top: 10px; }}
        .btn:hover {{ background: #5568d3; }}
        .btn-secondary {{ background: #6c757d; }}
        label {{ font-weight: bold; color: #555; margin-top: 10px; display: block; }}
        h1 {{ color: #333; }}
    </style>
    <div class='container'>
        <h1>➕ Crear Nuevo Registro</h1>
        <form method='POST'>
            <label>Cédula: *</label>
            <input type='text' name='cedula' required pattern='[0-9]{{10}}' placeholder='10 dígitos' value='{cedula_param}'>
            
            <label>Primer Nombre: *</label>
            <input type='text' name='primer_nombre' required>
            
            <label>Segundo Nombre:</label>
            <input type='text' name='segundo_nombre'>
            
            <label>Apellido Paterno: *</label>
            <input type='text' name='apellido_paterno' required>
            
            <label>Apellido Materno: *</label>
            <input type='text' name='apellido_materno' required>
            
            <label>Email: *</label>
            <input type='email' name='correo' required placeholder='ejemplo@correo.com'>
            
            <label>Celular: *</label>
            <input type='text' name='celular' required pattern='[0-9]{{10}}' placeholder='10 dígitos'>
            
            <label>Calificación (0-10): *</label>
            <input type='number' name='calificacion' required min='0' max='10' step='0.01' value='0'>
            
            <label>Cuadro de Honor:</label>
            <select name='cuadro_honor'>
                <option value='NO'>NO</option>
                <option value='SI'>SI</option>
            </select>
            
            <label>Estado:</label>
            <select name='estado'>
                <option value='PENDIENTE'>PENDIENTE</option>
                <option value='COMPLETO'>COMPLETO</option>
            </select>
            
            <button type='submit' class='btn'>💾 Guardar</button>
            <a href='/opcion3' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>← Cancelar</a>
        </form>
    </div>
    """

@app.route('/opcion3_editar/<cedula>', methods=['GET', 'POST'])
def opcion3_editar(cedula):
    """Editar registro existente (solo Admin)"""
    if session.get('rol') != 'ADMIN':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    registro = db.obtener_registro_por_cedula(cedula)
    if not registro:
        flash('Registro no encontrado', 'error')
        return redirect(url_for('opcion3'))
    
    if request.method == 'POST':
        datos = {
            'primer_nombre': request.form.get('primer_nombre', '').strip().upper(),
            'segundo_nombre': request.form.get('segundo_nombre', '').strip().upper(),
            'apellido_paterno': request.form.get('apellido_paterno', '').strip().upper(),
            'apellido_materno': request.form.get('apellido_materno', '').strip().upper(),
            'correo': request.form.get('correo', '').strip().lower(),
            'celular': request.form.get('celular', '').strip(),
            'calificacion': request.form.get('calificacion', '0'),
            'cuadro_honor': request.form.get('cuadro_honor', 'NO'),
            'estado': request.form.get('estado', 'PENDIENTE')
        }
        
        exito, mensaje = db.actualizar_registro(cedula, datos)
        
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('opcion3'))
        else:
            flash(mensaje, 'error')
    
    return f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        input, select {{ width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; margin-top: 10px; }}
        .btn:hover {{ background: #5568d3; }}
        .btn-secondary {{ background: #6c757d; }}
        label {{ font-weight: bold; color: #555; margin-top: 10px; display: block; }}
        h1 {{ color: #333; }}
    </style>
    <div class='container'>
        <h1>✏️ Modificar Registro</h1>
        <p><strong>Cédula:</strong> {registro['cedula']} (no modificable)</p>
        <form method='POST'>
            <label>Primer Nombre: *</label>
            <input type='text' name='primer_nombre' required value='{registro['primer_nombre']}'>
            
            <label>Segundo Nombre:</label>
            <input type='text' name='segundo_nombre' value='{registro.get('segundo_nombre', '')}'>
            
            <label>Apellido Paterno: *</label>
            <input type='text' name='apellido_paterno' required value='{registro['apellido_paterno']}'>
            
            <label>Apellido Materno: *</label>
            <input type='text' name='apellido_materno' required value='{registro['apellido_materno']}'>
            
            <label>Email: *</label>
            <input type='email' name='correo' required value='{registro['correo']}'>
            
            <label>Celular: *</label>
            <input type='text' name='celular' required pattern='[0-9]{{10}}' value='{registro['celular']}'>
            
            <label>Calificación (0-10): *</label>
            <input type='number' name='calificacion' required min='0' max='10' step='0.01' value='{registro['calificacion']}'>
            
            <label>Cuadro de Honor:</label>
            <select name='cuadro_honor'>
                <option value='NO' {'selected' if registro['cuadro_honor'] == 'NO' else ''}>NO</option>
                <option value='SI' {'selected' if registro['cuadro_honor'] == 'SI' else ''}>SI</option>
            </select>
            
            <label>Estado:</label>
            <select name='estado'>
                <option value='PENDIENTE' {'selected' if registro['estado'] == 'PENDIENTE' else ''}>PENDIENTE</option>
                <option value='COMPLETO' {'selected' if registro['estado'] == 'COMPLETO' else ''}>COMPLETO</option>
            </select>
            
            <button type='submit' class='btn'>💾 Actualizar</button>
            <a href='/opcion3' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>← Cancelar</a>
        </form>
    </div>
    """

@app.route('/opcion3_eliminar/<cedula>')
def opcion3_eliminar(cedula):
    """Eliminar registro (solo Admin)"""
    if session.get('rol') != 'ADMIN':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    exito, mensaje = db.eliminar_registro(cedula)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'error')
    
    return redirect(url_for('opcion3'))

# ========== OPCIÓN 4: VER TODOS LOS POSTULANTES ==========

@app.route('/opcion4')
def opcion4():
    """Lista todos los postulantes registrados"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    registros = db.listar_todos_registros()
    
    html = """
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; }
        .postulante-card { background: white; padding: 20px; margin: 15px; border-radius: 10px; 
                          box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 5px solid #667eea; }
        .btn { background: #667eea; color: white; padding: 10px 20px; text-decoration: none; 
              border-radius: 5px; display: inline-block; margin: 10px 5px; }
        .btn:hover { background: #5568d3; }
        .estado-completo { color: green; font-weight: bold; }
        .estado-pendiente { color: orange; font-weight: bold; }
    </style>
    <h1>👥 Lista de Postulantes Registrados</h1>
    """
    
    for reg in registros:
        nombre_completo = f"{reg['primer_nombre']} {reg['apellido_paterno']}"
        clase_estado = 'estado-completo' if reg['estado'] == 'COMPLETO' else 'estado-pendiente'
        
        html += f"""
        <div class='postulante-card'>
            <h3>{nombre_completo}</h3>
            <p><strong>Cédula:</strong> {reg['cedula']}</p>
            <p><strong>Email:</strong> {reg['correo']}</p>
            <p><strong>Estado:</strong> <span class='{clase_estado}'>{reg['estado']}</span></p>
        </div>
        """
    
    html += f"<br><p><strong>Total de registros:</strong> {len(registros)}</p>"
    html += "<br><a href='/dashboard' class='btn'>← Volver al menú</a>"
    return html

# ========== OPCIÓN 5: CREAR INSCRIPCIÓN (CON VALIDACIÓN DE ESTADO) ==========

@app.route('/opcion5', methods=['GET', 'POST'])
def opcion5():
    """Crear inscripción a carrera - SOLO si estado es COMPLETO"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    cedula = session.get('cedula')
    registro = db.obtener_registro_por_cedula(cedula)
    
    # VALIDAR ESTADO COMPLETO
    if registro['estado'] != 'COMPLETO':
        flash(f'❌ No puede inscribirse. Su estado es: {registro["estado"]}. Debe tener estado COMPLETO.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        carrera_id = request.form.get('carrera_id')
        jornada_num = request.form.get('jornada')
        
        # Mapear jornadas
        jornadas = {
            '1': 'Matutina',
            '2': 'Vespertina',
            '3': 'Nocturna'
        }
        
        # Mapear carreras
        carreras_dict = {
            '101': 'Tecnologías de Información',
            '102': 'Medicina',
            '103': 'Ingeniería Civil',
            '104': 'Administración',
            '105': 'Derecho'
        }
        
        jornada = jornadas.get(jornada_num, 'Matutina')
        carrera_nombre = carreras_dict.get(carrera_id, 'No especificada')
        
        # Insertar inscripción
        datos_inscripcion = {
            'cedula_postulante': cedula,
            'carrera_id': int(carrera_id),
            'carrera_nombre': carrera_nombre,
            'jornada': jornada,
            'estado': 'CONFIRMADA'
        }
        
        exito, mensaje = db.insertar_inscripcion(datos_inscripcion)
        
        if exito:
            # Enviar correo de confirmación
            datos_estudiante = registro
            datos_insc = db.obtener_inscripcion_por_cedula(cedula)
            
            try:
                email_service.enviar_confirmacion_inscripcion(
                    registro['correo'],
                    datos_estudiante,
                    datos_insc
                )
                flash(f'Inscripción confirmada. Se envió un correo a {registro["correo"]}', 'success')
            except Exception as e:
                flash(f'Inscripción confirmada, pero no se pudo enviar el correo: {str(e)}', 'warning')
            
            return redirect(url_for('opcion5_confirmacion'))
        else:
            flash(mensaje, 'error')
    
    return """
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
        .btn:hover { background: #5568d3; }
        .btn-secondary { background: #6c757d; margin-top: 10px; }
        label { font-weight: bold; color: #555; margin-top: 10px; display: block; }
    </style>
    <div class='container'>
        <h1>📝 Crear Inscripción</h1>
        <div style='background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
            ✅ <strong>Estado verificado: COMPLETO</strong>
        </div>
        <form method='POST'>
            <label>Seleccione una carrera:</label>
            <select name='carrera_id' required>
                <option value=''>-- Seleccione --</option>
                <option value='101'>101 - Tecnologías de Información</option>
                <option value='102'>102 - Medicina</option>
                <option value='103'>103 - Ingeniería Civil</option>
                <option value='104'>104 - Administración</option>
                <option value='105'>105 - Derecho</option>
            </select>
            
            <label>Seleccione jornada:</label>
            <select name='jornada' required>
                <option value=''>-- Seleccione --</option>
                <option value='1'>Matutina (07:00 - 12:00)</option>
                <option value='2'>Vespertina (13:00 - 18:00)</option>
                <option value='3'>Nocturna (18:00 - 22:00)</option>
            </select>
            
            <button type='submit' class='btn'>Confirmar Inscripción</button>
        </form>
        <br>
        <a href='/dashboard' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>← Volver al menú</a>
    </div>
    """

@app.route('/opcion5_confirmacion')
def opcion5_confirmacion():
    """Muestra confirmación de inscripción"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    cedula = session.get('cedula')
    inscripcion = db.obtener_inscripcion_por_cedula(cedula)
    
    if not inscripcion:
        flash('No se encontró inscripción', 'error')
        return redirect(url_for('opcion5'))
    
    return f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success-box {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .info-row {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
    </style>
    <div class='container'>
        <h1>✅ Inscripción Confirmada</h1>
        <div class='success-box'>
            <h3>¡Su inscripción ha sido registrada exitosamente!</h3>
            <p>Se ha enviado un correo de confirmación a su email registrado.</p>
        </div>
        <div class='info-row'><strong>Carrera:</strong> {inscripcion['carrera_nombre']}</div>
        <div class='info-row'><strong>Jornada:</strong> {inscripcion['jornada']}</div>
        <div class='info-row'><strong>Estado:</strong> {inscripcion['estado']}</div>
        <div class='info-row'><strong>Fecha:</strong> {inscripcion['fecha_inscripcion']}</div>
        <br>
        <a href='/dashboard' class='btn'>← Volver al menú</a>
    </div>
    """

# ========== OPCIÓN 6: VERIFICAR EVALUACIÓN ==========

@app.route('/opcion6', methods=['GET', 'POST'])
def opcion6():
    """Verificar evaluación del postulante"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    # ESTUDIANTE solo ve su evaluación
    # ADMIN puede buscar cualquier cédula
    rol = session.get('rol')
    cedula_sesion = session.get('cedula')
    
    if request.method == 'POST':
        cedula = request.form.get('cedula', '').strip()
        
        # Si es ESTUDIANTE, forzar que solo vea su cédula
        if rol == 'ESTUDIANTE' and cedula != cedula_sesion:
            flash('Solo puede ver su propia evaluación', 'error')
            cedula = cedula_sesion
        
        if not db.existe_registro(cedula):
            flash('Cédula no encontrada', 'error')
            return redirect(url_for('opcion6'))
        
        evaluacion = db.obtener_evaluacion_por_cedula(cedula)
        
        if not evaluacion:
            flash('No se encontró evaluación para esta cédula', 'warning')
            return redirect(url_for('opcion6'))
        
        registro = db.obtener_registro_por_cedula(cedula)
        nombre_completo = f"{registro['primer_nombre']} {registro['apellido_paterno']}"
        
        # Enviar correo con resultados
        try:
            email_service.enviar_confirmacion_evaluacion(
                registro['correo'],
                registro,
                evaluacion
            )
            mensaje_correo = f"✅ Resultados enviados a {registro['correo']}"
        except Exception as e:
            mensaje_correo = f"⚠️ No se pudo enviar el correo: {str(e)}"
        
        return f"""
        <style>
            body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .info-row {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
            .success {{ color: green; font-weight: bold; }}
        </style>
        <div class='container'>
            <h1>📝 Resultados de Evaluación</h1>
            <h3>{nombre_completo}</h3>
            <div class='info-row'><strong>Cédula:</strong> {cedula}</div>
            <div class='info-row'><strong>Email:</strong> {registro['correo']}</div>
            <hr>
            <h3>Resultados:</h3>
            <div class='info-row'><strong>Razonamiento Verbal:</strong> {evaluacion['nota_verbal']}/10</div>
            <div class='info-row'><strong>Razonamiento Numérico:</strong> {evaluacion['nota_numerica']}/10</div>
            <div class='info-row'><strong>Razonamiento Abstracto:</strong> {evaluacion['nota_abstracta']}/10</div>
            <div class='info-row'><strong>Puntaje Total:</strong> <span class='success'>{evaluacion['puntaje_total']}/1000</span></div>
            <div class='info-row'><strong>Estado:</strong> {evaluacion['estado']}</div>
            <br>
            <p><em>{mensaje_correo}</em></p>
            <a href='/opcion6' class='btn'>← Nueva consulta</a>
            <a href='/dashboard' class='btn'>← Volver al menú</a>
        </div>
        """
    
    # GET: Formulario (pre-llenar si es ESTUDIANTE)
    cedula_default = cedula_sesion if rol == 'ESTUDIANTE' else ''
    readonly = "readonly" if rol == 'ESTUDIANTE' else ""
    
    return f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        input[type='text'] {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }}
        .btn:hover {{ background: #5568d3; }}
        .btn-secondary {{ background: #6c757d; margin-top: 10px; }}
    </style>
    <div class='container'>
        <h1>📝 Verificar Evaluación</h1>
        <form method='POST'>
            <label><strong>Ingrese cédula:</strong></label>
            <input type='text' name='cedula' required pattern='[0-9]{{10}}' 
                   placeholder='Ej: 1316202082' value='{cedula_default}' {readonly}>
            <button type='submit' class='btn'>Verificar</button>
        </form>
        <br>
        <a href='/dashboard' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>← Volver al menú</a>
    </div>
    """

# ========== OPCIÓN 7: CONSULTAR ASIGNACIÓN ==========

@app.route('/opcion7', methods=['GET', 'POST'])
def opcion7():
    """Consultar asignación de laboratorio"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    rol = session.get('rol')
    cedula_sesion = session.get('cedula')
    
    if request.method == 'POST':
        cedula = request.form.get('cedula', '').strip()
        
        # Si es ESTUDIANTE, solo su cédula
        if rol == 'ESTUDIANTE' and cedula != cedula_sesion:
            flash('Solo puede ver su propia asignación', 'error')
            cedula = cedula_sesion
        
        if not db.existe_registro(cedula):
            flash('Cédula no encontrada', 'error')
            return redirect(url_for('opcion7'))
        
        asignacion = db.obtener_asignacion_por_cedula(cedula)
        
        if not asignacion:
            flash('No se encontró asignación para esta cédula', 'warning')
            return redirect(url_for('opcion7'))
        
        registro = db.obtener_registro_por_cedula(cedula)
        nombre_completo = f"{registro['primer_nombre']} {registro['apellido_paterno']}"
        
        # Enviar correo con asignación
        try:
            email_service.enviar_asignacion_laboratorio(
                registro['correo'],
                registro,
                asignacion
            )
            mensaje_correo = f"✅ Asignación enviada a {registro['correo']}"
        except Exception as e:
            mensaje_correo = f"⚠️ No se pudo enviar el correo: {str(e)}"
        
        # Mapeo de carreras
        carreras = {
            101: 'Tecnologías de Información',
            102: 'Medicina',
            103: 'Ingeniería Civil',
            104: 'Administración',
            105: 'Derecho'
        }
        
        carrera_nombre = carreras.get(asignacion['carrera_id'], 'No especificada')
        
        return f"""
        <style>
            body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .info-row {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
            .success {{ color: green; font-weight: bold; }}
        </style>
        <div class='container'>
            <h1>📍 Asignación de Laboratorio</h1>
            <h3>{nombre_completo}</h3>
            <div class='info-row'><strong>Cédula:</strong> {cedula}</div>
            <div class='info-row'><strong>Email:</strong> {registro['correo']}</div>
            <hr>
            <h3>🏫 Información de Asignación:</h3>
            <div class='info-row'><strong>Carrera:</strong> {carrera_nombre}</div>
            <div class='info-row'><strong>Sede:</strong> Sede {asignacion['sede_id']} - Matriz Manta</div>
            <div class='info-row'><strong>Edificio:</strong> {asignacion['edificio']}</div>
            <div class='info-row'><strong>Laboratorio:</strong> {asignacion['laboratorio']}</div>
            <hr>
            <h3>📅 Fecha y Hora:</h3>
            <div class='info-row'><strong>Fecha del Examen:</strong> {asignacion['fecha_examen']}</div>
            <div class='info-row'><strong>Hora de Inicio:</strong> {asignacion['hora_inicio']}</div>
            <div class='info-row'><strong>Estado:</strong> <span class='success'>{asignacion['estado']}</span></div>
            <br>
            <p><em>{mensaje_correo}</em></p>
            <a href='/opcion7' class='btn'>← Nueva consulta</a>
            <a href='/dashboard' class='btn'>← Volver al menú</a>
        </div>
        """
    
    cedula_default = cedula_sesion if rol == 'ESTUDIANTE' else ''
    readonly = "readonly" if rol == 'ESTUDIANTE' else ""
    
    return f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        input[type='text'] {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }}
        .btn:hover {{ background: #5568d3; }}
        .btn-secondary {{ background: #6c757d; margin-top: 10px; }}
    </style>
    <div class='container'>
        <h1>📍 Consultar Asignación</h1>
        <form method='POST'>
            <label><strong>Ingrese cédula:</strong></label>
            <input type='text' name='cedula' required pattern='[0-9]{{10}}' 
                   placeholder='Ej: 1316202082' value='{cedula_default}' {readonly}>
            <button type='submit' class='btn'>Consultar</button>
        </form>
        <br>
        <a href='/dashboard' class='btn btn-secondary' style='text-decoration: none; display: block; text-align: center;'>← Volver al menú</a>
    </div>
    """

# ========== OPCIÓN 8: CONSULTAR PUNTAJE ==========

@app.route('/opcion8')
def opcion8():
    """Consultar puntaje final del postulante"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    cedula = session.get('cedula')
    puntaje = db.obtener_puntaje_por_cedula(cedula)
    
    if not puntaje:
        flash('No se encontró puntaje registrado', 'warning')
        return redirect(url_for('dashboard'))
    
    registro = db.obtener_registro_por_cedula(cedula)
    nombre_completo = f"{registro['primer_nombre']} {registro['apellido_paterno']}"
    
    porcentaje = puntaje['porcentaje']
    
    if porcentaje >= 90:
        calificacion_txt = "EXCELENTE"
        color = "green"
    elif porcentaje >= 80:
        calificacion_txt = "MUY BUENO"
        color = "green"
    elif porcentaje >= 70:
        calificacion_txt = "BUENO"
        color = "green"
    elif porcentaje >= 60:
        calificacion_txt = "ACEPTABLE"
        color = "orange"
    else:
        calificacion_txt = "INSUFICIENTE"
        color = "red"
    
    return f"""
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .info-row {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
    </style>
    <div class='container'>
        <h1>📊 Consultar Puntaje</h1>
        <h3>{nombre_completo}</h3>
        <div class='info-row'><strong>Cédula:</strong> {cedula}</div>
        <hr>
        <h3>📝 Desglose de Puntaje:</h3>
        <div class='info-row'><strong>Nota Bachillerato:</strong> {puntaje['nota_bachillerato']}/10 (30%)</div>
        <div class='info-row'><strong>Puntaje SENESCYT:</strong> {puntaje['puntaje_senescyt']}/1000 (60%)</div>
        <div class='info-row'><strong>Bonificación Mérito:</strong> {puntaje['bonificacion_merito']} puntos (10%)</div>
        <hr>
        <h3>🎯 Resultado Final:</h3>
        <div class='info-row'><strong>Puntaje Final:</strong> {puntaje['puntaje_final']:.2f}/1000</div>
        <div class='info-row'><strong>Porcentaje:</strong> {porcentaje:.2f}%</div>
        <div class='info-row'><strong>Calificación:</strong> {calificacion_txt}</div>
        <div class='info-row'><strong>Estado:</strong> <span style='color: {color}; font-weight: bold;'>{puntaje['estado_aprobacion']}</span></div>
        <br>
        <a href='/dashboard' class='btn'>← Volver al menú</a>
    </div>
    """

# ========== RUTAS TYPESCRIPT CON VALIDACIONES ==========

@app.route('/index_ts')
def index_ts():
    """Menú funciones tradicionales"""
    if 'cedula' not in session:
        flash('Debe iniciar sesión', 'warning')
        return redirect(url_for('index'))
    
    return render_template('index_ts.html',
                         cedula=session.get('cedula'),
                         nombre=session.get('nombre'),
                         rol=session.get('rol'),
                         estado=session.get('estado'))

@app.route('/verificar_registro_ts', methods=['GET', 'POST'])
def verificar_registro_ts():
    """Verificar Registro Nacional en Excel para TypeScript - Valida estado COMPLETO"""
    if 'cedula' not in session:
        flash('Debe iniciar sesión', 'warning')
        return redirect(url_for('index'))
    
    rol = session.get('rol')
    cedula_sesion = session.get('cedula')
    
    # Pre-llenar cédula si es ESTUDIANTE
    cedula_default = cedula_sesion if rol == 'ESTUDIANTE' else ''
    
    registro = None
    
    if request.method == 'POST':
        cedula = request.form.get('cedula', '').strip()
        
        # Si es ESTUDIANTE, forzar su cédula
        if rol == 'ESTUDIANTE' and cedula != cedula_sesion:
            flash('Solo puede verificar su propio registro', 'error')
            cedula = cedula_sesion
        
        if not cedula or len(cedula) != 10:
            flash('Cédula inválida. Debe tener 10 dígitos', 'error')
            return redirect(url_for('verificar_registro_ts'))
        
        # BUSCAR EN BASE DE DATOS EXCEL
        registro = db.obtener_registro_por_cedula(cedula)
        
        if not registro:
            flash('❌ Cédula no encontrada en la base de datos. No puedes inscribirte.', 'error')
        else:
            # Actualizar estado en sesión
            if cedula == cedula_sesion:
                session['estado'] = registro['estado']
    
    return render_template('verificar_registro_ts.html',
                         cedula_default=cedula_default,
                         registro=registro,
                         rol=rol)

@app.route('/ver_postulantes_ts')
def ver_postulantes_ts():
    """Ver postulantes TypeScript - Solo ADMIN"""
    if session.get('rol') != 'ADMIN':
        flash('Acceso denegado. Solo administradores', 'error')
        return redirect(url_for('dashboard'))
    
    resultado = llamar_typescript('/api/postulantes', 'GET')
    return render_template('ver_postulantes_ts.html', postulantes=resultado.get('data', []))

@app.route('/crear_postulante_ts', methods=['GET', 'POST'])
def crear_postulante_ts():
    """Crear postulante TypeScript - Solo ADMIN"""
    if session.get('rol') != 'ADMIN':
        flash('Acceso denegado. Solo administradores', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        datos = {
            'cedula': request.form.get('cedula'),
            'nombreCompleto': request.form.get('nombre'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'fechaNacimiento': request.form.get('fecha_nacimiento')
        }
        
        resultado = llamar_typescript('/api/postulantes', 'POST', datos)
        
        if resultado.get('exito'):
            flash('✅ Postulante creado en TypeScript', 'success')
        else:
            flash(f'❌ Error: {resultado.get("error")}', 'error')
        
        return redirect(url_for('dashboard'))
    
    return render_template('crear_postulante.html')

@app.route('/crear_inscripcion_ts', methods=['GET', 'POST'])
def crear_inscripcion_ts():
    """Crear inscripción TypeScript - SOLO si estado COMPLETO"""
    if 'cedula' not in session:
        return redirect(url_for('index'))
    
    cedula = session.get('cedula')
    
    # VALIDAR ESTADO
    if session.get('rol') == 'ESTUDIANTE':
        registro = db.obtener_registro_por_cedula(cedula)
        if registro['estado'] != 'COMPLETO':
            flash(f'❌ Estado: {registro["estado"]}. Debe ser COMPLETO para inscribirse.', 'error')
            return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        datos = {
            'cedula': request.form.get('cedula'),
            'carrera': request.form.get('carrera'),
            'periodo': request.form.get('periodo')
        }
        
        resultado = llamar_typescript('/api/inscripciones', 'POST', datos)
        
        if resultado.get('exito'):
            flash('✅ Inscripción creada exitosamente', 'success')
            return redirect(url_for('ver_postulantes_ts'))
        else:
            flash(f'❌ Error: {resultado.get("error")}', 'error')
    
    return render_template('crear_inscripcion_ts.html')

@app.route('/crear_registro_ts', methods=['GET', 'POST'])
def crear_registro_ts():
    """Crear registro TypeScript - Solo ADMIN"""
    if session.get('rol') != 'ADMIN':
        flash('Acceso denegado. Solo administradores', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        datos = {
            'cedula': request.form.get('cedula'),
            'nombres': request.form.get('nombres'),
            'apellidos': request.form.get('apellidos'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'direccion': request.form.get('direccion'),
            'fecha_nacimiento': request.form.get('fecha_nacimiento'),
            'genero': request.form.get('genero')
        }
        
        resultado = llamar_typescript('/api/postulantes', 'POST', datos)
        
        if resultado.get('exito'):
            flash('✅ Postulante registrado exitosamente', 'success')
            return redirect(url_for('ver_postulantes_ts'))
        else:
            flash(f'❌ Error: {resultado.get("error")}', 'error')
    
    return render_template('crear_registro_ts.html')

# ========== MANEJO DE ERRORES ==========

@app.errorhandler(404)
def not_found(error):
    return """
    <h1>404 - Página no encontrada</h1>
    <p>La página que buscas no existe.</p>
    <a href='/'>Volver al inicio</a>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    return """
    <h1>500 - Error interno del servidor</h1>
    <p>Ocurrió un error inesperado.</p>
    <a href='/'>Volver al inicio</a>
    """, 500

@app.route('/test_typescript')
def test_typescript():
    """Prueba la conexión con TypeScript"""
    try:
        resultado = llamar_typescript('/health', 'GET')
        
        if resultado.get('status') == 'OK':
            return f"""
            <h1 style='color: green;'>✅ CONEXIÓN EXITOSA</h1>
            <p>Flask puede comunicarse con TypeScript</p>
            <pre>{resultado}</pre>
            <br>
            <a href='/dashboard'>← Volver al dashboard</a>
            """
        else:
            return f"""
            <h1 style='color: orange;'>⚠️ RESPUESTA INESPERADA</h1>
            <pre>{resultado}</pre>
            """
    except Exception as e:
        return f"""
        <h1 style='color: red;'>❌ ERROR DE CONEXIÓN</h1>
        <p>Flask NO puede conectarse con TypeScript</p>
        <p>Error: {str(e)}</p>
        <br>
        <p>Verifica que el servidor TypeScript esté corriendo en puerto 3000</p>
        """

# ========== PUNTO DE ENTRADA ==========

if __name__ == '__main__':
    if not os.path.exists(app.config['EXCEL_PATH']):
        print("⚠️  ADVERTENCIA: No se encontró el archivo datos_admision.xlsx")
        print("Ejecute primero: python crear_excel_inicial.py")
    else:
        print("✅ Archivo Excel encontrado")
        print("🚀 Iniciando sistema...")
        print(f"📊 Base de datos: {app.config['EXCEL_PATH']}")
    
    app.run(debug=True, port=5000)