/**
 * Módulo: PoliticaAccionAfirmativa con PATRÓN CHAIN OF RESPONSIBILITY
 * Autores: Jean Pierre Flores Piloso, Braddy Londre Vera, Bismark Gabriel Cevallos
 * Fecha: Diciembre 2025
 * 
 * PATRÓN APLICADO: CHAIN OF RESPONSIBILITY (Comportamiento)
 * ¿Por qué? La determinación del segmento sigue una cadena de verificaciones en orden de prioridad
 */

// ==================== PATRÓN CHAIN OF RESPONSIBILITY ====================

abstract class ManejadorSegmento {
    /**
     * PATRÓN CHAIN OF RESPONSIBILITY
     * Cada manejador decide si procesa la solicitud o la pasa al siguiente
     */
    protected siguiente: ManejadorSegmento | null = null;
    
    establecerSiguiente(manejador: ManejadorSegmento): ManejadorSegmento {
        this.siguiente = manejador;
        return manejador;  // Permite encadenamiento fluido
    }
    
    abstract manejar(marcadores: Map<string, string>): string | null;
}

class ManejadorCuotas extends ManejadorSegmento {
    /**
     * PRIORIDAD 1: Verifica si aplica para CUOTAS
     */
    manejar(marcadores: Map<string, string>): string | null {
        const tieneCuotas = (
            marcadores.get('condicion_socioeconomica') === 'SI' ||
            marcadores.get('ruralidad') === 'SI' ||
            marcadores.get('discapacidad') === 'SI' ||
            marcadores.get('pueblos_nacionalidades') === 'SI' ||
            marcadores.get('victima_violencia') === 'SI' ||
            marcadores.get('migrantes_retornados') === 'SI'
        );
        
        if (tieneCuotas) {
            console.log("  [Chain] ManejadorCuotas: CUOTAS (Prioridad 1)");
            return 'CUOTAS';
        }
        
        // Pasar al siguiente en la cadena
        if (this.siguiente) {
            return this.siguiente.manejar(marcadores);
        }
        return null;
    }
}

class ManejadorVulnerabilidad extends ManejadorSegmento {
    /**
     * PRIORIDAD 2: Verifica VULNERABILIDAD socioeconómica
     */
    manejar(marcadores: Map<string, string>): string | null {
        if (marcadores.get('vulnerabilidad_socioeconomica') === 'SI') {
            console.log("  [Chain] ManejadorVulnerabilidad: VULNERABILIDAD (Prioridad 2)");
            return 'VULNERABILIDAD';
        }
        
        if (this.siguiente) {
            return this.siguiente.manejar(marcadores);
        }
        return null;
    }
}

class ManejadorMeritoAcademico extends ManejadorSegmento {
    /**
     * PRIORIDAD 3: Verifica MÉRITO ACADÉMICO
     */
    manejar(marcadores: Map<string, string>): string | null {
        if (marcadores.get('merito_academico') === 'SI') {
            console.log("  [Chain] ManejadorMeritoAcademico: MERITO_ACADEMICO (Prioridad 3)");
            return 'MERITO_ACADEMICO';
        }
        
        if (this.siguiente) {
            return this.siguiente.manejar(marcadores);
        }
        return null;
    }
}

class ManejadorPueblosNacionalidades extends ManejadorSegmento {
    /**
     * PRIORIDAD 5: Verifica PUEBLOS Y NACIONALIDADES (bachilleres)
     */
    manejar(marcadores: Map<string, string>): string | null {
        if (marcadores.get('bachiller_pueblos_nacionalidad') === 'SI') {
            console.log("  [Chain] ManejadorPueblosNacionalidades: PUEBLOS_NACIONALIDADES (Prioridad 5)");
            return 'PUEBLOS_NACIONALIDADES';
        }
        
        if (this.siguiente) {
            return this.siguiente.manejar(marcadores);
        }
        return null;
    }
}

class ManejadorBachilleres extends ManejadorSegmento {
    /**
     * PRIORIDAD 6: Verifica BACHILLERES
     */
    manejar(marcadores: Map<string, string>): string | null {
        if (marcadores.get('bachiller_periodo_academico') === 'SI') {
            console.log("  [Chain] ManejadorBachilleres: BACHILLERES (Prioridad 6)");
            return 'BACHILLERES';
        }
        
        if (this.siguiente) {
            return this.siguiente.manejar(marcadores);
        }
        return null;
    }
}

class ManejadorGeneral extends ManejadorSegmento {
    /**
     * PRIORIDAD 7: POBLACIÓN GENERAL (por defecto)
     */
    manejar(marcadores: Map<string, string>): string | null {
        console.log("  [Chain] ManejadorGeneral: GENERAL (Prioridad 7)");
        return 'GENERAL';
    }
}

// ==================== CLASE PRINCIPAL ====================

class PoliticaAccionAfirmativa {
    private static _contador: number = 0;
    
    private static readonly ORDEN_SEGMENTOS = [
        'CUOTAS',
        'VULNERABILIDAD',
        'MERITO_ACADEMICO',
        'RECONOCIMIENTOS',
        'PUEBLOS_NACIONALIDADES',
        'BACHILLERES',
        'GENERAL'
    ];
    
    idPostulante: number;
    identificacion: string;
    
    // Marcaciones
    cupoAceptadoHistoricoPc: string = 'NO';
    cupoHistoricoActivo: string = 'NO';
    numeroCuposActivos: number = 0;
    
    // Marcadores de condiciones
    private _marcadores: Map<string, string> = new Map();
    
    // Segmento
    segmentoAsignado: string | null = null;
    prioridadSegmento: number = 99;
    
    // CHAIN OF RESPONSIBILITY
    private _cadenaManejadores: ManejadorSegmento;
    
    constructor(idPostulante: number, identificacion: string) {
        PoliticaAccionAfirmativa._contador++;
        
        this.idPostulante = idPostulante;
        this.identificacion = identificacion;
        
        // Inicializar marcadores
        this._marcadores.set('condicion_socioeconomica', 'NO');
        this._marcadores.set('ruralidad', 'NO');
        this._marcadores.set('discapacidad', 'NO');
        this._marcadores.set('pueblos_nacionalidades', 'NO');
        this._marcadores.set('victima_violencia', 'NO');
        this._marcadores.set('migrantes_retornados', 'NO');
        this._marcadores.set('merito_academico', 'NO');
        this._marcadores.set('vulnerabilidad_socioeconomica', 'NO');
        this._marcadores.set('bachiller_pueblos_nacionalidad', 'NO');
        this._marcadores.set('bachiller_periodo_academico', 'NO');
        this._marcadores.set('poblacion_general', 'SI');
        
        // CONSTRUIR CADENA DE RESPONSABILIDAD
        this._cadenaManejadores = this._construirCadena();
        
        console.log(`PAA creada para postulante ID: ${idPostulante}`);
    }
    
    private _construirCadena(): ManejadorSegmento {
        /**
         * PATRÓN CHAIN OF RESPONSIBILITY
         * Construye la cadena en orden de prioridad
         */
        const cuotas = new ManejadorCuotas();
        const vulnerabilidad = new ManejadorVulnerabilidad();
        const merito = new ManejadorMeritoAcademico();
        const pueblos = new ManejadorPueblosNacionalidades();
        const bachilleres = new ManejadorBachilleres();
        const general = new ManejadorGeneral();
        
        // Encadenar: cada uno apunta al siguiente
        cuotas
            .establecerSiguiente(vulnerabilidad)
            .establecerSiguiente(merito)
            .establecerSiguiente(pueblos)
            .establecerSiguiente(bachilleres)
            .establecerSiguiente(general);
        
        return cuotas;  // Retorna el primero de la cadena
    }
    
    marcarCupoHistorico(tieneCupo: boolean, activo: boolean = false): void {
        this.cupoAceptadoHistoricoPc = tieneCupo ? 'SI' : 'NO';
        this.cupoHistoricoActivo = activo ? 'SI' : 'NO';
        if (activo) {
            this.numeroCuposActivos++;
        }
        console.log(`  Cupo histórico: ${this.cupoAceptadoHistoricoPc}`);
    }
    
    aplicarCondicionSocioeconomica(quintil: number): void {
        if (quintil <= 2) {
            this._marcadores.set('condicion_socioeconomica', 'SI');
            if (quintil === 1) {
                this._marcadores.set('vulnerabilidad_socioeconomica', 'SI');
                console.log(`  Vulnerabilidad socioeconómica detectada (Quintil ${quintil})`);
            }
        }
        console.log(`  Condición socioeconómica: Quintil ${quintil}`);
    }
    
    aplicarRuralidad(tipoInstitucion: string, zona: string): void {
        if (tipoInstitucion.toUpperCase() === 'FISCAL' && zona.toUpperCase() === 'RURAL') {
            this._marcadores.set('ruralidad', 'SI');
            console.log(`  Ruralidad aplicada`);
        }
    }
    
    aplicarDiscapacidad(porcentaje: number, tieneCarnet: boolean): void {
        if (tieneCarnet && porcentaje >= 30) {
            this._marcadores.set('discapacidad', 'SI');
            console.log(`  Discapacidad aplicada: ${porcentaje}%`);
        }
    }
    
    aplicarPueblosNacionalidades(autoidentificacion: string): void {
        const grupos = ['INDIGENA', 'AFROECUATORIANO', 'MONTUBIO'];
        if (grupos.includes(autoidentificacion.toUpperCase())) {
            this._marcadores.set('pueblos_nacionalidades', 'SI');
            console.log(`  Pueblos y nacionalidades: ${autoidentificacion}`);
        }
    }
    
    aplicarMeritoAcademico(cuadroHonor: string, distincion?: string): void {
        if (cuadroHonor === 'SI') {
            const distinciones = [
                'ABANDERADO PABELLON NACIONAL',
                'PORTA ESTANDARTE PLANTEL',
                '1er. ESCOLTA PABELLON NACIONAL'
            ];
            
            if (distincion && distinciones.includes(distincion)) {
                this._marcadores.set('merito_academico', 'SI');
                console.log(`  Mérito académico: ${distincion}`);
            }
        }
    }
    
    aplicarBachillerUltimoAnio(esBachiller: boolean, pertenecePueblos: boolean = false): void {
        if (esBachiller) {
            this._marcadores.set('bachiller_periodo_academico', 'SI');
            if (pertenecePueblos) {
                this._marcadores.set('bachiller_pueblos_nacionalidad', 'SI');
                console.log(`  Bachiller de pueblos y nacionalidades`);
            } else {
                console.log(`  Bachiller último año`);
            }
        }
    }
    
    calcularSegmento(): string {
        /**
         * EJECUTA LA CADENA DE RESPONSABILIDAD
         * Cada manejador verifica si aplica o pasa al siguiente
         */
        console.log("\n[Chain of Responsibility] Iniciando cadena de verificación...");
        
        const segmento = this._cadenaManejadores.manejar(this._marcadores);
        
        if (segmento) {
            this.segmentoAsignado = segmento;
            this.prioridadSegmento = PoliticaAccionAfirmativa.ORDEN_SEGMENTOS.indexOf(segmento) + 1;
        }
        
        return this.segmentoAsignado!;
    }
    
    obtenerResumen(): any {
        return {
            idPostulante: this.idPostulante,
            segmento: this.segmentoAsignado,
            prioridad: this.prioridadSegmento,
            vulnerabilidad: this._marcadores.get('vulnerabilidad_socioeconomica'),
            merito: this._marcadores.get('merito_academico'),
            pueblos: this._marcadores.get('pueblos_nacionalidades'),
            discapacidad: this._marcadores.get('discapacidad'),
            ruralidad: this._marcadores.get('ruralidad')
        };
    }
    
    toString(): string {
        return `PAA(Postulante:${this.idPostulante}, Segmento:${this.segmentoAsignado}, Prioridad:${this.prioridadSegmento})`;
    }
    
    static obtenerTotal(): number {
        return PoliticaAccionAfirmativa._contador;
    }
}

// ==================== EJEMPLOS DE USO ====================

console.log("\n" + "=".repeat(80));
console.log("PATRÓN CHAIN OF RESPONSIBILITY - POLÍTICA DE ACCIÓN AFIRMATIVA");
console.log("=".repeat(80));

// ===== EJEMPLO 1: Mérito académico =====
console.log("\n\nEJEMPLO 1: Estudiante con merito academico");
console.log("-".repeat(80));

const paa1 = new PoliticaAccionAfirmativa(1, "1316202082");

paa1.aplicarMeritoAcademico('SI', 'ABANDERADO PABELLON NACIONAL');
paa1.calcularSegmento();

console.log(`\nResumen:`, paa1.obtenerResumen());

// ===== EJEMPLO 2: Vulnerabilidad (pasa por Cuotas primero) =====
console.log("\n\nEJEMPLO 2: Estudiante con vulnerabilidad socioeconomica");
console.log("-".repeat(80));

const paa2 = new PoliticaAccionAfirmativa(2, "1350123456");

paa2.aplicarCondicionSocioeconomica(1);  // Quintil 1 → Vulnerabilidad
paa2.aplicarRuralidad('FISCAL', 'RURAL');
paa2.aplicarPueblosNacionalidades('MONTUBIO');
paa2.calcularSegmento();

console.log(`\nResumen:`, paa2.obtenerResumen());

// ===== EJEMPLO 3: Población general (pasa por TODA la cadena) =====
console.log("\n\nEJEMPLO 3: Poblacion general");
console.log("-".repeat(80));

const paa3 = new PoliticaAccionAfirmativa(3, "1360234567");

paa3.calcularSegmento();

console.log(`\nResumen:`, paa3.obtenerResumen());

// ===== EJEMPLO 4: Bachiller pueblos (pasa por varios manejadores) =====
console.log("\n\nEJEMPLO 4: Bachiller de pueblos y nacionalidades");
console.log("-".repeat(80));

const paa4 = new PoliticaAccionAfirmativa(4, "1370345678");

paa4.aplicarPueblosNacionalidades('INDIGENA');
paa4.aplicarBachillerUltimoAnio(true, true);
paa4.calcularSegmento();

console.log(`\nResumen:`, paa4.obtenerResumen());

console.log(`\nTotal PAA creadas: ${PoliticaAccionAfirmativa.obtenerTotal()}`);

console.log("\n" + "=".repeat(80));
console.log("VENTAJAS DEL PATRÓN CHAIN OF RESPONSIBILITY:");
console.log("=".repeat(80));
console.log("1. Desacopla emisor de receptor de solicitud");
console.log("2. Orden de verificación claro y modificable");
console.log("3. Fácil agregar/quitar/reordenar manejadores");
console.log("4. Cada manejador tiene UNA responsabilidad");
console.log("5. Cumple Open/Closed Principle");
console.log("=".repeat(80));