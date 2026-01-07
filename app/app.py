from flask import Flask, render_template, request, redirect, url_for, flash, session
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

from models.RegistroNacional import RegistroNacional
from models.Postulante import Postulante
from models.SedeCampus import SedeCampus
from models.Inscripcion import Inscripcion
from models.Evaluacion import Evaluacion, CalculadoraPuntaje, ValidadorNotas
from models.Asignacion import Asignacion, ValidadorAsignacion, ServicioCupos
from models.PuntajePostulacion import (
    PuntajePostulacion, ValidadorNotasPuntaje, 
    CalculadorPuntajePostulacion, FormateadorSalidaPuntaje
)

app = Flask(__name__)
app.secret_key = 'sistema_sipu_2025'

# Precargar datos
def precargar_datos():
    if not RegistroNacional.existe_registro("1316202082"):
        registro1 = RegistroNacional("1316202082", "JEAN PIERRE", "FLORES PILOSO")
        registro1.completar_datos_personales("2007-05-15", "HOMBRE", "MESTIZO")
        registro1.completar_ubicacion("MANABÍ", "MANTA", "MANTA", "LOS ESTEROS", "AV. 24")
        registro1.completar_contacto("0999999999", "jean@gmail.com")
        registro1.completar_datos_academicos("U.E. MANTA", "FISCAL", 9.5, "SI")
        registro1.validar_completitud()
    
    if not RegistroNacional.existe_registro("1350123456"):
        registro2 = RegistroNacional("1350123456", "BRADDY", "LONDRE VERA")
        registro2.completar_datos_personales("2008-03-20", "HOMBRE", "MESTIZO")
        registro2.completar_ubicacion("MANABÍ", "CHONE", "CHONE", "CENTRO", "CALLE PRINCIPAL")
        registro2.completar_contacto("0988888888", "braddy@gmail.com")
        registro2.completar_datos_academicos("U.E. CHONE", "FISCAL", 8.8, "NO")
        registro2.validar_completitud()

    if not RegistroNacional.existe_registro("1317924551"):
        registro3 = RegistroNacional("1317924551", "Jesus", "Gregorio")
        registro3.completar_datos_personales("2004-12-24", "HOMBRE", "MESTIZO")
        registro3.completar_ubicacion("MANABÍ", "Manta", "Manta", "Los esteros", "CALLE PRINCIPAL")
        registro3.completar_contacto("0984314823", "jesusgabriel@gmail.com")
        registro3.completar_datos_academicos("U.E. CHONE", "FISCAL", 8.8, "NO")
        registro3.validar_completitud()
    
    print("✅ Datos precargados")

precargar_datos()

@app.route('/')
def index():
    return render_template('Replica_ADMISION_ULEAM.html')

@app.route('/login', methods=['POST'])
def login():
    cedula = request.form.get('usuario')
    
    if RegistroNacional.existe_registro(cedula):
        registro = RegistroNacional.consultar_por_cedula(cedula)
        session['cedula'] = cedula
        session['nombre'] = registro.obtener_nombre_completo()
        return redirect(url_for('dashboard'))
    else:
        flash('Cédula no encontrada')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'cedula' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', 
                         cedula=session['cedula'],
                         nombre=session['nombre'])

# ========== OPCIÓN 1: VER SEDES ==========
@app.route('/opcion1')
def opcion1():
    sedes_html = "<h1>🏫 Sedes Disponibles ULEAM</h1>"
    for id_sede, datos in SedeCampus.SEDES_ULEAM.items():
        sedes_html += f"""
        <div style='background: white; padding: 15px; margin: 10px; border-radius: 8px;'>
            <h3>{id_sede}. {datos['nombre']}</h3>
            <p><strong>Cantón:</strong> {datos['canton']}</p>
            <p><strong>Provincia:</strong> {datos['provincia']}</p>
        </div>
        """
    sedes_html += "<br><a href='/dashboard'>← Volver al menú</a>"
    return sedes_html

# ========== OPCIÓN 2: VER CARRERAS ==========
@app.route('/opcion2')
def opcion2():
    carreras = [
        {'id': 101, 'nombre': 'Tecnologías de Información', 'cupos': 40},
        {'id': 102, 'nombre': 'Medicina', 'cupos': 70},
        {'id': 103, 'nombre': 'Ingeniería Civil', 'cupos': 50},
        {'id': 104, 'nombre': 'Administración', 'cupos': 30},
        {'id': 105, 'nombre': 'Derecho', 'cupos': 45},
    ]
    
    html = "<h1>📚 Carreras Disponibles</h1>"
    for carrera in carreras:
        html += f"""
        <div style='background: white; padding: 15px; margin: 10px; border-radius: 8px;'>
            <h3>{carrera['id']} - {carrera['nombre']}</h3>
            <p><strong>Cupos:</strong> {carrera['cupos']}</p>
        </div>
        """
    html += "<br><a href='/dashboard'>← Volver al menú</a>"
    return html

# ========== OPCIÓN 3: VERIFICAR REGISTRO ==========
@app.route('/opcion3')
def opcion3():
    cedula = session.get('cedula')
    if RegistroNacional.existe_registro(cedula):
        registro = RegistroNacional.consultar_por_cedula(cedula)
        return f"""
        <h1>✅ Registro Encontrado</h1>
        <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px;'>
            <p><strong>Nombre:</strong> {registro.obtener_nombre_completo()}</p>
            <p><strong>Cédula:</strong> {registro.identificacion}</p>
            <p><strong>Email:</strong> {registro.correo}</p>
            <p><strong>Celular:</strong> {registro.celular}</p>
            <p><strong>Calificación:</strong> {registro.calificacion}/10</p>
            <p><strong>Cuadro de Honor:</strong> {registro.cuadro_honor}</p>
            <p><strong>Estado:</strong> {registro.estado}</p>
        </div>
        <a href='/dashboard'>← Volver al menú</a>
        """
    return "<p>No se encontró registro</p>"

# ========== OPCIÓN 4: VER POSTULANTES ==========
@app.route('/opcion4')
def opcion4():
    # Obtener todos los registros
    html = "<h1>👥 Lista de Postulantes Registrados</h1>"
    html += "<div style='padding: 20px;'>"
    
    # Simular lista de postulantes (puedes obtenerlos del repositorio)
    postulantes = [
        {"cedula": "1316202082", "nombre": "JEAN PIERRE FLORES PILOSO", "estado": "COMPLETO"},
        {"cedula": "1350123456", "nombre": "BRADDY LONDRE VERA", "estado": "COMPLETO"},
        {"cedula": "1317924551", "nombre": "Jesus Gabriel Gegrorio", "estado": "Completo"}
    ]
    
    for post in postulantes:
        html += f"""
        <div style='background: white; padding: 15px; margin: 10px; border-radius: 8px; border-left: 4px solid #667eea;'>
            <h3>{post['nombre']}</h3>
            <p><strong>Cédula:</strong> {post['cedula']}</p>
            <p><strong>Estado:</strong> <span style='color: green;'>{post['estado']}</span></p>
        </div>
        """
    
    html += "</div><br><a href='/dashboard'>← Volver al menú</a>"
    return html

# ========== OPCIÓN 5: CREAR INSCRIPCIÓN (MEJORADA) ==========
@app.route('/opcion5', methods=['GET', 'POST'])
def opcion5():
    if request.method == 'POST':
        carrera_id = request.form.get('carrera_id')
        jornada_num = request.form.get('jornada')
        
        # Mapear jornada
        jornadas = {
            '1': 'matutina',
            '2': 'vespertina',
            '3': 'nocturna'
        }
        jornada = jornadas.get(jornada_num, 'matutina')
        
        # Mapear carreras
        carreras_dict = {
            '101': 'Tecnologías de Información',
            '102': 'Medicina',
            '103': 'Ingeniería Civil',
            '104': 'Administración',
            '105': 'Derecho'
        }
        
        # Mapear jornadas con horarios
        jornadas_texto = {
            '1': 'Matutina (07:00 - 12:00)',
            '2': 'Vespertina (13:00 - 18:00)',
            '3': 'Nocturna (18:00 - 22:00)'
        }
        
        carrera_nombre = carreras_dict.get(carrera_id, 'No especificada')
        jornada_nombre = jornadas_texto.get(jornada_num, 'No especificada')
        
        cedula = session.get('cedula')
        registro = RegistroNacional.consultar_por_cedula(cedula)
        
        try:
            # Desactivar creación automática de evaluación
            import models.Inscripcion as InscripcionModule
            metodo_original = InscripcionModule.Inscripcion._crear_evaluacion_automatica
            InscripcionModule.Inscripcion._crear_evaluacion_automatica = lambda self: None
            
            # Crear inscripción
            inscripcion = Inscripcion(
                id_postulante=1,
                carrera_id=int(carrera_id),
                orden_preferencia=1,
                sede_id=1,
                jornada=jornada,
                cedula_postulante=cedula,
                email_postulante=registro.correo
            )
            
            # Restaurar método
            InscripcionModule.Inscripcion._crear_evaluacion_automatica = metodo_original
            
            # Crear evaluación
            evaluacion = Evaluacion(
                id_inscripcion=inscripcion.id_inscripcion,
                tipo_evaluacion='INTEGRAL',
                tipo_calculo='ESTANDAR',
                calculadora=CalculadoraPuntaje(),
                validador=ValidadorNotas()
            )
            
            return f"""
            <h1>✅ Inscripción Creada Exitosamente</h1>
            <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px; max-width: 600px;'>
                <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>📋 Datos del Ciudadano</h3>
                <p><strong>Nombre Completo:</strong> {registro.obtener_nombre_completo()}</p>
                <p><strong>Cédula:</strong> {cedula}</p>
                <p><strong>Email:</strong> {registro.correo}</p>
                <p><strong>Teléfono:</strong> {registro.celular}</p>
                
                <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 20px;'>🎓 Inscripción Solicitada</h3>
                <p><strong>Carrera:</strong> {carrera_id} - {carrera_nombre}</p>
                <p><strong>Jornada:</strong> {jornada_nombre}</p>
                <p><strong>Sede:</strong> Matriz - Manta</p>
                
                <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 20px;'>📄 Detalles de Inscripción</h3>
                <p><strong>ID Inscripción:</strong> {inscripcion.id_inscripcion}</p>
                <p><strong>Comprobante:</strong> {inscripcion.comprobante_pdf_url}</p>
                <p><strong>Estado:</strong> <span style='color: green; font-weight: bold;'>{inscripcion.estado}</span></p>
                <p><strong>Fecha:</strong> {inscripcion.fecha_inscripcion.strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>ID Evaluación:</strong> {evaluacion.id_evaluacion}</p>
            </div>
            <a href='/dashboard' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Volver al menú</a>
            """
        except Exception as e:
            return f"""
            <h1>❌ Error al crear inscripción</h1>
            <p style='color: red;'>{str(e)}</p>
            <a href='/opcion5'>← Reintentar</a>
            """
    
    # GET: Mostrar formulario
    return """
    <h1>✍️ Crear Inscripción</h1>
    <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px; max-width: 500px;'>
        <form method='POST'>
            <label><strong>Seleccione Carrera:</strong></label><br>
            <select name='carrera_id' required style='width: 100%; padding: 10px; margin: 10px 0;'>
                <option value='101'>101 - Tecnologías de Información</option>
                <option value='102'>102 - Medicina</option>
                <option value='103'>103 - Ingeniería Civil</option>
                <option value='104'>104 - Administración</option>
                <option value='105'>105 - Derecho</option>
            </select><br>
            
            <label><strong>Seleccione Jornada:</strong></label><br>
            <select name='jornada' required style='width: 100%; padding: 10px; margin: 10px 0;'>
                <option value='1'>1 - Matutina (07:00 - 12:00)</option>
                <option value='2'>2 - Vespertina (13:00 - 18:00)</option>
                <option value='3'>3 - Nocturna (18:00 - 22:00)</option>
            </select><br><br>
            
            <button type='submit' style='background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                Crear Inscripción
            </button>
        </form>
    </div>
    <a href='/dashboard'>← Volver al menú</a>
    """

# ========== OPCIÓN 6: CONSULTAR EVALUACIÓN (MODIFICADA) ==========
@app.route('/opcion6', methods=['GET', 'POST'])
def opcion6():
    if request.method == 'POST':
        cedula_ingresada = request.form.get('cedula')
        
        # Verificar si la cédula existe
        if RegistroNacional.existe_registro(cedula_ingresada):
            registro = RegistroNacional.consultar_por_cedula(cedula_ingresada)
            
            return f"""
            <h1>📝 Información de Evaluación</h1>
            <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px;'>
                <h2>{registro.obtener_nombre_completo()}</h2>
                <p><strong>Cédula:</strong> {cedula_ingresada}</p>
                <hr>
                <h3>📅 Detalles del Examen</h3>
                <p><strong>Fecha:</strong> Sábado, 15 de Febrero de 2025</p>
                <p><strong>Hora de Ingreso:</strong> 07:30 AM</p>
                <p><strong>Hora de Inicio:</strong> 08:00 AM</p>
                <p><strong>Sede:</strong> Matriz - Manta</p>
                <p><strong>Dirección:</strong> Av. Circunvalación - Vía San Mateo</p>
                <p><strong>Tipo de Examen:</strong> EXAMEN GENERAL</p>
                <hr>
                <p style='color: #667eea;'><strong>⚠️ Importante:</strong> Presentarse 30 minutos antes</p>
                <p style='color: #667eea;'><strong>📋 Requisitos:</strong> Cédula original, lápiz 2B, borrador</p>
            </div>
            <a href='/opcion6' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Nueva consulta</a>
            <a href='/dashboard' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Volver al menú</a>
            """
        else:
            return f"""
            <h1>❌ Error de Verificación</h1>
            <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px; border-left: 4px solid red;'>
                <p style='color: red; font-size: 1.1em;'><strong>La cédula ingresada es incorrecta. Vuelva a intentar.</strong></p>
                <p><strong>Cédula ingresada:</strong> {cedula_ingresada}</p>
            </div>
            <a href='/opcion6' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Reintentar</a>
            <a href='/dashboard' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Volver al menú</a>
            """
    
    # GET: Solo mostrar campo de cédula
    return """
    <h1>📝 Verificar Evaluación</h1>
    <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px; max-width: 500px;'>
        <form method='POST'>
            <label><strong>Ingrese su cédula:</strong></label><br>
            <input type='text' name='cedula' required 
                   pattern='[0-9]{10}' 
                   placeholder='Ej: 1316202082'
                   style='width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;'><br><br>
            
            <button type='submit' style='background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;'>
                Verificar
            </button>
        </form>
    </div>
    <a href='/dashboard'>← Volver al menú</a>
    """

# ========== OPCIÓN 7: CONSULTAR ASIGNACIÓN (MODIFICADA) ==========
@app.route('/opcion7', methods=['GET', 'POST'])
def opcion7():
    if request.method == 'POST':
        cedula_ingresada = request.form.get('cedula')
        
        # Verificar si la cédula existe
        if RegistroNacional.existe_registro(cedula_ingresada):
            registro = RegistroNacional.consultar_por_cedula(cedula_ingresada)
            
            try:
                # Crear servicios
                servicio_cupos = ServicioCupos()
                servicio_cupos.configurar_cupos(101, 50)
                validador = ValidadorAsignacion(servicio_cupos)
                
                # Crear asignación
                asignacion = Asignacion(
                    id_postulante=1,
                    carrera_id=101,
                    sede_id=1,
                    puntaje_total=850,
                    orden_merito=1,
                    validador=validador,
                    servicio_cupos=servicio_cupos
                )
                
                if asignacion.validar_requisitos():
                    asignacion.asignar()
                    
                    return f"""
                    <h1>📍 Asignación de Laboratorio</h1>
                    <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px;'>
                        <h2>{registro.obtener_nombre_completo()}</h2>
                        <p><strong>Cédula:</strong> {cedula_ingresada}</p>
                        <p><strong>Email:</strong> {registro.correo}</p>
                        <hr>
                        <h3>🏫 Información de Asignación</h3>
                        <p><strong>Carrera:</strong> Tecnologías de Información</p>
                        <p><strong>Sede:</strong> Matriz - Manta</p>
                        <p><strong>Edificio:</strong> Edificio A - Tecnología</p>
                        <p><strong>Laboratorio:</strong> LAB-101 - Laboratorio de Informática</p>
                        <p><strong>Ubicación:</strong> Edificio A, Piso 2, Ala Norte</p>
                        <hr>
                        <h3>📅 Fecha y Hora</h3>
                        <p><strong>Fecha:</strong> Sábado, 15 de Febrero de 2025</p>
                        <p><strong>Hora de Ingreso:</strong> 07:30 AM</p>
                        <p><strong>Hora de Inicio:</strong> 08:00 AM</p>
                        <hr>
                        <p style='color: green;'><strong>✅ Estado:</strong> {asignacion.estado}</p>
                    </div>
                    <a href='/opcion7' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Nueva consulta</a>
                    <a href='/dashboard' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Volver al menú</a>
                    """
                else:
                    return f"""
                    <h1>❌ No cumple requisitos para asignación</h1>
                    <p>Puntaje mínimo requerido no alcanzado</p>
                    <a href='/opcion7'>← Reintentar</a>
                    <a href='/dashboard'>← Volver al menú</a>
                    """
            except Exception as e:
                return f"""
                <h1>❌ Error al consultar asignación</h1>
                <p style='color: red;'>{str(e)}</p>
                <a href='/opcion7'>← Reintentar</a>
                <a href='/dashboard'>← Volver al menú</a>
                """
        else:
            return f"""
            <h1>❌ Error de Verificación</h1>
            <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px; border-left: 4px solid red;'>
                <p style='color: red; font-size: 1.1em;'><strong>La cédula ingresada es incorrecta. Vuelva a intentar.</strong></p>
                <p><strong>Cédula ingresada:</strong> {cedula_ingresada}</p>
            </div>
            <a href='/opcion7' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Reintentar</a>
            <a href='/dashboard' style='background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px;'>← Volver al menú</a>
            """
    
    # GET: Solo mostrar campo de cédula
    return """
    <h1>📍 Consultar Asignación</h1>
    <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px; max-width: 500px;'>
        <form method='POST'>
            <label><strong>Ingrese su cédula:</strong></label><br>
            <input type='text' name='cedula' required 
                   pattern='[0-9]{10}' 
                   placeholder='Ej: 1316202082'
                   style='width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;'><br><br>
            
            <button type='submit' style='background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;'>
                Consultar
            </button>
        </form>
    </div>
    <a href='/dashboard'>← Volver al menú</a>
    """

# ========== OPCIÓN 8: CONSULTAR PUNTAJE ==========
@app.route('/opcion8')
def opcion8():
    cedula = session.get('cedula')
    registro = RegistroNacional.consultar_por_cedula(cedula)
    
    validador = ValidadorNotasPuntaje()
    calculador = CalculadorPuntajePostulacion()
    formateador = FormateadorSalidaPuntaje()
    
    calificacion = registro.calificacion if registro.calificacion else 9.0
    puntaje_senescyt = 850
    bonificacion = 100 if registro.cuadro_honor == 'SI' else 0
    
    puntaje = PuntajePostulacion(
        id_postulante=1,
        cedula_postulante=cedula,
        nota_grado=calificacion,
        puntaje_evaluacion=puntaje_senescyt,
        puntaje_meritos=bonificacion,
        validador=validador,
        calculador=calculador,
        formateador=formateador
    )
    
    porcentaje = (puntaje.puntaje_final / 1000) * 100
    
    if porcentaje >= 90:
        calificacion_txt = "EXCELENTE"
        estado = "✅ APROBADO"
        color = "green"
    elif porcentaje >= 80:
        calificacion_txt = "MUY BUENO"
        estado = "✅ APROBADO"
        color = "green"
    elif porcentaje >= 70:
        calificacion_txt = "BUENO"
        estado = "✅ APROBADO"
        color = "green"
    elif porcentaje >= 60:
        calificacion_txt = "ACEPTABLE"
        estado = "✅ APROBADO"
        color = "orange"
    else:
        calificacion_txt = "INSUFICIENTE"
        estado = "❌ NO APROBADO"
        color = "red"
    
    return f"""
    <h1>📊 Consultar Puntaje</h1>
    <div style='background: white; padding: 20px; margin: 20px; border-radius: 10px;'>
        <h2>{registro.obtener_nombre_completo()}</h2>
        <p><strong>Cédula:</strong> {cedula}</p>
        <hr>
        <h3>📝 Desglose de Puntaje</h3>
        <p><strong>Nota Bachillerato:</strong> {calificacion}/10 (30%)</p>
        <p><strong>Puntaje SENESCYT:</strong> {puntaje_senescyt}/1000 (60%)</p>
        <p><strong>Bonificación Mérito:</strong> {bonificacion} puntos (10%)</p>
        <hr>
        <h3>🎯 Resultado Final</h3>
        <p><strong>Puntaje Final:</strong> {puntaje.puntaje_final:.2f}/1000</p>
        <p><strong>Porcentaje:</strong> {porcentaje:.2f}%</p>
        <p><strong>Calificación:</strong> {calificacion_txt}</p>
        <p style='color: {color}; font-size: 1.2em;'><strong>Estado:</strong> {estado}</p>
    </div>
    <a href='/dashboard'>← Volver al menú</a>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5000)