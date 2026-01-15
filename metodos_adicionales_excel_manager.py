"""
MÉTODOS ADICIONALES para excel_manager.py
Agrega estos métodos a la clase ExcelManager
"""

def obtener_todas_sedes(self):
    """
    Obtiene todas las sedes desde la hoja 'sedes'
    
    Returns:
        list: Lista de diccionarios con datos de sedes
    """
    with self.lock:
        try:
            wb = load_workbook(self.excel_path)
            ws = wb["sedes"]
            
            sedes = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:  # Si tiene ID
                    sede = {
                        'id_sede': row[0],
                        'nombre_sede': row[1] or '',
                        'ciudad': row[2] or '',
                        'direccion': row[3] or '',
                        'telefono': row[4] or '',
                        'capacidad': row[5] or 0,
                        'estado': row[6] or 'ACTIVA'
                    }
                    sedes.append(sede)
            
            wb.close()
            return sedes
        except Exception as e:
            print(f"Error al obtener sedes: {e}")
            return []

def obtener_sede_por_id(self, id_sede):
    """
    Obtiene una sede específica por ID
    
    Args:
        id_sede: ID de la sede
        
    Returns:
        dict: Datos de la sede o None
    """
    with self.lock:
        try:
            wb = load_workbook(self.excel_path)
            ws = wb["sedes"]
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] == id_sede:
                    sede = {
                        'id_sede': row[0],
                        'nombre_sede': row[1] or '',
                        'ciudad': row[2] or '',
                        'direccion': row[3] or '',
                        'telefono': row[4] or '',
                        'capacidad': row[5] or 0,
                        'estado': row[6] or 'ACTIVA'
                    }
                    wb.close()
                    return sede
            
            wb.close()
            return None
        except Exception as e:
            print(f"Error al obtener sede: {e}")
            return None

def obtener_todas_carreras(self):
    """
    Obtiene todas las carreras desde la hoja 'carreras'
    
    Returns:
        list: Lista de diccionarios con datos de carreras
    """
    with self.lock:
        try:
            wb = load_workbook(self.excel_path)
            ws = wb["carreras"]
            
            carreras = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:  # Si tiene ID
                    carrera = {
                        'id_carrera': row[0],
                        'nombre_carrera': row[1] or '',
                        'facultad': row[2] or '',
                        'duracion_semestres': row[3] or 0,
                        'cupos_disponibles': row[4] or 0,
                        'modalidad': row[5] or 'PRESENCIAL',
                        'jornadas_disponibles': row[6] or '',
                        'estado': row[7] or 'ACTIVA'
                    }
                    carreras.append(carrera)
            
            wb.close()
            return carreras
        except Exception as e:
            print(f"Error al obtener carreras: {e}")
            return []

def obtener_carrera_por_id(self, id_carrera):
    """
    Obtiene una carrera específica por ID
    
    Args:
        id_carrera: ID de la carrera
        
    Returns:
        dict: Datos de la carrera o None
    """
    with self.lock:
        try:
            wb = load_workbook(self.excel_path)
            ws = wb["carreras"]
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] == id_carrera:
                    carrera = {
                        'id_carrera': row[0],
                        'nombre_carrera': row[1] or '',
                        'facultad': row[2] or '',
                        'duracion_semestres': row[3] or 0,
                        'cupos_disponibles': row[4] or 0,
                        'modalidad': row[5] or 'PRESENCIAL',
                        'jornadas_disponibles': row[6] or '',
                        'estado': row[7] or 'ACTIVA'
                    }
                    wb.close()
                    return carrera
            
            wb.close()
            return None
        except Exception as e:
            print(f"Error al obtener carrera: {e}")
            return None

def buscar_carreras_por_facultad(self, facultad):
    """
    Busca carreras por nombre de facultad
    
    Args:
        facultad: Nombre de la facultad (puede ser parcial)
        
    Returns:
        list: Lista de carreras que coinciden
    """
    todas_carreras = self.obtener_todas_carreras()
    
    if not facultad:
        return todas_carreras
    
    resultados = []
    facultad_lower = facultad.lower()
    
    for carrera in todas_carreras:
        if facultad_lower in carrera['facultad'].lower():
            resultados.append(carrera)
    
    return resultados

def obtener_carreras_activas(self):
    """
    Obtiene solo las carreras activas
    
    Returns:
        list: Lista de carreras con estado ACTIVA
    """
    todas_carreras = self.obtener_todas_carreras()
    return [c for c in todas_carreras if c['estado'] == 'ACTIVA']

def obtener_sedes_activas(self):
    """
    Obtiene solo las sedes activas
    
    Returns:
        list: Lista de sedes con estado ACTIVA
    """
    todas_sedes = self.obtener_todas_sedes()
    return [s for s in todas_sedes if s['estado'] == 'ACTIVA']
