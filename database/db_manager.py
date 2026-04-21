"""
db_manager.py
Maneja la conexión a SQLite (local) y MySQL (sincronización).
"""

import sqlite3
import os
import datetime

# ── Ruta de la base de datos ────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "..", "data", "taquilla.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


# ════════════════════════════════════════════════════════════
#  SQLITE
# ════════════════════════════════════════════════════════════

def get_connection() -> sqlite3.Connection:
    """Devuelve una conexión SQLite con row_factory y FK activas."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas si no existen, usando schema.sql."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("[DB] Base de datos inicializada correctamente.")


# ════════════════════════════════════════════════════════════
#  USUARIOS
# ════════════════════════════════════════════════════════════

def autenticar_usuario(usuario: str, password: str) -> dict | None:
    """
    Verifica credenciales. Devuelve dict del usuario o None.
    TODO: cambiar a hash (bcrypt) antes de producción.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE usuario=? AND password=? AND activo=1",
        (usuario, password)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ════════════════════════════════════════════════════════════
#  TURNOS
# ════════════════════════════════════════════════════════════

def abrir_turno(usuario_id: int, fondo_inicial: float = 0.0) -> int:
    """Abre el turno del día (9am-5pm). Un solo turno por día. Devuelve el ID."""
    fecha = datetime.date.today().isoformat()
    conn  = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO turnos (usuario_id, fecha, turno, fondo_inicial)
               VALUES (?, ?, 'unico', ?)""",
            (usuario_id, fecha, fondo_inicial)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        # Ya existe turno para hoy — reutilizar
        row = conn.execute(
            "SELECT id FROM turnos WHERE fecha=? AND turno='unico'",
            (fecha,)
        ).fetchone()
        return row["id"]
    finally:
        conn.close()


def cerrar_turno(turno_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE turnos SET cerrado=1, hora_fin=datetime('now','localtime') WHERE id=?",
        (turno_id,)
    )
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  FOLIOS
# ════════════════════════════════════════════════════════════

def _generar_folio() -> str:
    """Genera folio único: VTA-YYYYMMDD-NNNN"""
    hoy  = datetime.date.today().strftime("%Y%m%d")
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM ventas WHERE fecha_hora LIKE ?",
        (f"{datetime.date.today().isoformat()}%",)
    ).fetchone()[0]
    conn.close()
    return f"VTA-{hoy}-{count+1:04d}"


# ════════════════════════════════════════════════════════════
#  VENTAS
# ════════════════════════════════════════════════════════════

def registrar_venta(
    turno_id: int,
    usuario_id: int,
    forma_pago: str,
    items: list[dict],
    monto_recibido: float | None = None,
    visitantes_data: list[dict] | None = None
) -> int:
    """
    Registra una venta completa.

    items = [
        {"tipo_boleto_id": 1, "cantidad": 2, "precio_unitario": 100.0},
        ...
    ]

    visitantes_data = [
        {"sexo": "M", "edad": 25, "es_local": 1},
        ...
    ]
    Devuelve el ID de la venta.
    """
    total  = sum(i["cantidad"] * i["precio_unitario"] for i in items)
    cambio = (monto_recibido - total) if monto_recibido else None
    folio  = _generar_folio()

    conn = get_connection()
    try:
        # 1. Venta principal
        cur = conn.execute(
            """INSERT INTO ventas
               (turno_id, usuario_id, folio, total, forma_pago, monto_recibido, cambio)
               VALUES (?,?,?,?,?,?,?)""",
            (turno_id, usuario_id, folio, total, forma_pago, monto_recibido, cambio)
        )
        venta_id = cur.lastrowid

        # 2. Detalle
        detalle_ids = []
        for item in items:
            subtotal = item["cantidad"] * item["precio_unitario"]
            cur2 = conn.execute(
                """INSERT INTO venta_detalle
                   (venta_id, tipo_boleto_id, cantidad, precio_unitario, subtotal)
                   VALUES (?,?,?,?,?)""",
                (venta_id, item["tipo_boleto_id"], item["cantidad"],
                 item["precio_unitario"], subtotal)
            )
            detalle_ids.append((cur2.lastrowid, item["cantidad"]))

        # 3. Visitantes — se insertan todos directamente al primer detalle_id
        # El diálogo ya genera 1 entrada por persona real (no por boleto)
        if visitantes_data and detalle_ids:
            # Todos los visitantes van ligados al primer renglón de detalle
            # (la estadística se lee de visitantes, no de venta_detalle)
            detalle_id_principal = detalle_ids[0][0]
            for v in visitantes_data:
                conn.execute(
                    """INSERT INTO visitantes
                       (venta_detalle_id, sexo, edad, es_local)
                       VALUES (?,?,?,?)""",
                    (detalle_id_principal, v["sexo"], v["edad"],
                     v.get("es_local", 1))
                )

        conn.commit()
        return venta_id

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def registrar_visita_pasaporte(turno_id: int, usuario_id: int,
                               visitantes: list[dict]):
    """
    Registra una visita de portador de Pasaporte Papagayo.
    Se crea una venta con total $0 y forma_pago 'pasaporte'.
    """
    conn = get_connection()
    try:
        folio = _generar_folio()
        # Obtener ID del tipo PASAPORTE
        tipo = conn.execute(
            "SELECT id FROM tipos_boleto WHERE clave='PASAPORTE'"
        ).fetchone()
        tipo_id = tipo["id"] if tipo else 1

        cur = conn.execute(
            """INSERT INTO ventas
               (turno_id, usuario_id, folio, total, forma_pago, monto_recibido, cambio)
               VALUES (?,?,?,0,'pasaporte',0,0)""",
            (turno_id, usuario_id, folio)
        )
        venta_id = cur.lastrowid

        cur2 = conn.execute(
            """INSERT INTO venta_detalle
               (venta_id, tipo_boleto_id, cantidad, precio_unitario, subtotal)
               VALUES (?,?,1,0,0)""",
            (venta_id, tipo_id)
        )
        detalle_id = cur2.lastrowid

        for v in visitantes:
            conn.execute(
                """INSERT INTO visitantes (venta_detalle_id, sexo, edad, es_local)
                   VALUES (?,?,?,?)""",
                (detalle_id, v["sexo"], v["edad"], v.get("es_local", 1))
            )
        conn.commit()
        return venta_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def cancelar_venta(venta_id: int, motivo: str):
    conn = get_connection()
    conn.execute(
        "UPDATE ventas SET cancelada=1, motivo_cancel=? WHERE id=?",
        (motivo, venta_id)
    )
    conn.commit()
    conn.close()


def obtener_venta(venta_id: int) -> dict | None:
    conn = get_connection()
    row  = conn.execute("SELECT * FROM ventas WHERE id=?", (venta_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ════════════════════════════════════════════════════════════
#  TIPOS DE BOLETO
# ════════════════════════════════════════════════════════════

def obtener_tipos_boleto() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tipos_boleto WHERE activo=1 ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════
#  REPORTES
# ════════════════════════════════════════════════════════════

def reporte_turno(turno_id: int) -> dict:
    """Devuelve resumen de ventas del turno."""
    conn = get_connection()

    ventas = conn.execute(
        """SELECT v.*, u.nombre as taquillero
           FROM ventas v JOIN usuarios u ON v.usuario_id = u.id
           WHERE v.turno_id=? AND v.cancelada=0
           ORDER BY v.fecha_hora""",
        (turno_id,)
    ).fetchall()

    totales = conn.execute(
        """SELECT forma_pago, SUM(total) as suma, COUNT(*) as cantidad
           FROM ventas
           WHERE turno_id=? AND cancelada=0
           GROUP BY forma_pago""",
        (turno_id,)
    ).fetchall()

    # Visitantes por sexo
    visitantes_sexo = conn.execute(
        """SELECT vi.sexo, COUNT(*) as total
           FROM visitantes vi
           JOIN venta_detalle vd ON vi.venta_detalle_id = vd.id
           JOIN ventas vn ON vd.venta_id = vn.id
           WHERE vn.turno_id=? AND vn.cancelada=0
           GROUP BY vi.sexo""",
        (turno_id,)
    ).fetchall()

    # Visitantes por tipo edad (niño=edad<18, adulto=edad>=18)
    visitantes_edad = conn.execute(
        """SELECT
             CASE WHEN vi.edad < 18 THEN 'nino' ELSE 'adulto' END as grupo,
             COUNT(*) as total
           FROM visitantes vi
           JOIN venta_detalle vd ON vi.venta_detalle_id = vd.id
           JOIN ventas vn ON vd.venta_id = vn.id
           WHERE vn.turno_id=? AND vn.cancelada=0
           GROUP BY grupo""",
        (turno_id,)
    ).fetchall()

    # Visitantes por sexo + edad (cruce)
    visitantes_cruce = conn.execute(
        """SELECT
             CASE WHEN vi.edad < 18 THEN 'nino' ELSE 'adulto' END as grupo,
             vi.sexo,
             COUNT(*) as total
           FROM visitantes vi
           JOIN venta_detalle vd ON vi.venta_detalle_id = vd.id
           JOIN ventas vn ON vd.venta_id = vn.id
           WHERE vn.turno_id=? AND vn.cancelada=0
           GROUP BY grupo, vi.sexo""",
        (turno_id,)
    ).fetchall()

    conn.close()
    return {
        "ventas":           [dict(v) for v in ventas],
        "totales":          [dict(t) for t in totales],
        "visitantes":       [dict(v) for v in visitantes_sexo],
        "visitantes_edad":  [dict(v) for v in visitantes_edad],
        "visitantes_cruce": [dict(v) for v in visitantes_cruce],
    }


def reporte_fecha(fecha: str) -> dict:
    """Reporte completo por fecha (YYYY-MM-DD)."""
    conn = get_connection()

    rows = conn.execute(
        """SELECT tb.nombre, SUM(vd.cantidad) as vendidos,
                  SUM(vd.subtotal) as ingresos
           FROM venta_detalle vd
           JOIN ventas v ON vd.venta_id = v.id
           JOIN tipos_boleto tb ON vd.tipo_boleto_id = tb.id
           WHERE v.fecha_hora LIKE ? AND v.cancelada=0
           GROUP BY tb.id
           ORDER BY ingresos DESC""",
        (f"{fecha}%",)
    ).fetchall()

    total_dia = conn.execute(
        "SELECT SUM(total) FROM ventas WHERE fecha_hora LIKE ? AND cancelada=0",
        (f"{fecha}%",)
    ).fetchone()[0] or 0.0

    conn.close()
    return {"detalle": [dict(r) for r in rows], "total": total_dia}


# ════════════════════════════════════════════════════════════
#  SINCRONIZACIÓN MySQL (stub para fase 2)
# ════════════════════════════════════════════════════════════

def sincronizar_mysql():
    """
    Placeholder. En fase 2:
    1. Leer ventas donde synced=0
    2. Insertar en MySQL remoto
    3. Marcar synced=1
    """
    print("[SYNC] Sincronización MySQL pendiente – implementar en Fase 2.")


# ── Inicialización automática al importar ────────────────────
if __name__ == "__main__":
    init_db()
    print("[DB] Listo.")
