-- ============================================================
--  TAQUILLA MUSEO PAPAGAYO - ESQUEMA SQLite
--  Versión 1.0
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- USUARIOS (taquilleros + admin)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL,
    usuario     TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,           -- hash bcrypt/sha256
    rol         TEXT    NOT NULL DEFAULT 'taquillero'
                        CHECK(rol IN ('admin', 'taquillero')),
    activo      INTEGER NOT NULL DEFAULT 1,
    creado_en   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- Usuarios por defecto
INSERT OR IGNORE INTO usuarios (nombre, usuario, password, rol)
VALUES
    ('Administrador', 'admin',      'admin123',  'admin'),
    ('Taquillero 1',  'taquilla1',  'taquilla1', 'taquillero'),
    ('Taquillero 2',  'taquilla2',  'taquilla2', 'taquillero');

-- ------------------------------------------------------------
-- TIPOS DE BOLETO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipos_boleto (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    clave       TEXT    NOT NULL UNIQUE,    -- e.g. "ADULTO", "NINO"
    nombre      TEXT    NOT NULL,
    precio      REAL    NOT NULL,
    edad_min    INTEGER,                    -- NULL = sin restricción
    edad_max    INTEGER,
    activo      INTEGER NOT NULL DEFAULT 1,
    notas       TEXT
);

INSERT OR IGNORE INTO tipos_boleto (clave, nombre, precio, edad_min, edad_max, notas) VALUES
    ('NINO',          'Niño (2–11 años)',               83.00,  2,  11, NULL),
    ('ADULTO',        'Adulto (12–59 años)',            100.00, 12, 59, NULL),
    ('3RA_EDAD',      '3ra Edad / Cap. Diferentes',     50.00,  60, NULL, 'Requiere identificación'),
    ('ESTUDIANTE',    'Estudiante / Profesor',           83.00,  NULL, NULL, 'Requiere credencial'),
    ('MIERCOLES_2X1', 'Miércoles 2x1',                 100.00, NULL, NULL, 'Solo miércoles, precio por pareja'),
    ('FAM_4',         'Paquete Familiar (4 personas)',  219.00, NULL, NULL, NULL),
    ('FAM_5',         'Paquete Familiar (5 personas)',  267.00, NULL, NULL, NULL),
    ('PASE_2X1',      'Pase Cortesía 2x1',              83.00,  NULL, NULL, NULL),
    ('CLUB',          'Club Papagayo',                 100.00, NULL, NULL, NULL),
    ('PASAPORTE',     'Pasaporte Papagayo',              0.00,  NULL, NULL, 'Precio variable – editar al vender'),
    ('CORTESIA',      'Cortesía',                        0.00,  NULL, NULL, 'Gratuito'),
    ('BEBE',          'Niño menor de 2 años',            0.00,  0,   1,  'Gratuito');

-- ------------------------------------------------------------
-- TURNOS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS turnos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    fecha           TEXT    NOT NULL,               -- YYYY-MM-DD
    turno           TEXT    NOT NULL CHECK(turno IN ('unico', 'manana', 'tarde')),
    hora_inicio     TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    hora_fin        TEXT,
    fondo_inicial   REAL    NOT NULL DEFAULT 0.0,
    cerrado         INTEGER NOT NULL DEFAULT 0,
    UNIQUE(fecha, turno)
);

-- ------------------------------------------------------------
-- VENTAS (cada transacción / cobro)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ventas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    turno_id        INTEGER NOT NULL REFERENCES turnos(id),
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    folio           TEXT    NOT NULL UNIQUE,        -- e.g. "VTA-20250601-0001"
    fecha_hora      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    total           REAL    NOT NULL,
    forma_pago      TEXT    NOT NULL CHECK(forma_pago IN ('efectivo', 'tpv', 'pasaporte')),
    monto_recibido  REAL,                           -- solo efectivo
    cambio          REAL,
    cancelada       INTEGER NOT NULL DEFAULT 0,
    motivo_cancel   TEXT,
    synced          INTEGER NOT NULL DEFAULT 0      -- 0=pendiente MySQL, 1=sincronizado
);

-- ------------------------------------------------------------
-- DETALLE DE VENTA (renglones)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS venta_detalle (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id        INTEGER NOT NULL REFERENCES ventas(id),
    tipo_boleto_id  INTEGER NOT NULL REFERENCES tipos_boleto(id),
    cantidad        INTEGER NOT NULL DEFAULT 1,
    precio_unitario REAL    NOT NULL,
    subtotal        REAL    NOT NULL
);

-- ------------------------------------------------------------
-- VISITANTES (el dato que hoy se captura en papel)
-- Cada visitante individual ligado a un renglón de venta
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS visitantes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_detalle_id INTEGER NOT NULL REFERENCES venta_detalle(id),
    sexo            TEXT    NOT NULL CHECK(sexo IN ('M', 'F', 'NB', 'NE')),
                                    -- M=Masculino F=Femenino NB=No Binario NE=No Especificado
    edad            INTEGER NOT NULL CHECK(edad >= 0 AND edad <= 120),
    es_local        INTEGER NOT NULL DEFAULT 1  -- 1=Tabasco, 0=Foráneo (útil para stats)
);

-- ------------------------------------------------------------
-- ÍNDICES para rendimiento en reportes
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_ventas_fecha    ON ventas(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_ventas_turno    ON ventas(turno_id);
CREATE INDEX IF NOT EXISTS idx_visitantes_sexo ON visitantes(sexo);
CREATE INDEX IF NOT EXISTS idx_visitantes_edad ON visitantes(edad);
CREATE INDEX IF NOT EXISTS idx_ventas_synced   ON ventas(synced);
