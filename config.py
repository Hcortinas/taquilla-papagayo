"""
config.py
Configuración central del Sistema de Taquilla Museo Papagayo.
"""

# ── Info del museo ───────────────────────────────────────────
MUSEO_NOMBRE   = "Museo Interactivo Papagayo"
MUSEO_CIUDAD   = "Villahermosa, Tabasco"
MUSEO_TELEFONO = ""   # Llenar con número real
MUSEO_EMAIL    = ""   # Llenar con correo real

# ── Versión ──────────────────────────────────────────────────
APP_VERSION = "1.0.0"
APP_TITULO  = f"Sistema de Taquilla – {MUSEO_NOMBRE}"

# ── Horarios ─────────────────────────────────────────────────
TURNO_INICIO   = "09:00"
TURNO_FIN      = "17:00"
DIAS_LABORALES = [1, 2, 3, 4, 5, 6]  # Martes a Domingo (0=Lunes, cerrado)

# ── Colores UI (Tkinter) ─────────────────────────────────────
COLOR_PRIMARIO   = "#005f73"   # Azul petróleo
COLOR_SECUNDARIO = "#0a9396"
COLOR_ACENTO     = "#ee9b00"   # Ámbar
COLOR_FONDO      = "#f8f9fa"
COLOR_TEXTO      = "#212529"
COLOR_ERROR      = "#e63946"
COLOR_EXITO      = "#2a9d8f"
COLOR_BLANCO     = "#ffffff"

FUENTE_TITULO  = ("Segoe UI", 16, "bold")
FUENTE_NORMAL  = ("Segoe UI", 11)
FUENTE_PEQUENA = ("Segoe UI", 9)
FUENTE_MONO    = ("Consolas", 10)

# ── Rutas ────────────────────────────────────────────────────
import os
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(BASE_DIR, "data")
REPORTS_DIR  = os.path.join(BASE_DIR, "reportes")
LOGO_PATH    = os.path.join(BASE_DIR, "assets", "logo.png")  # Agregar logo aquí

os.makedirs(DATA_DIR,    exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── MySQL (Fase 2) ───────────────────────────────────────────
MYSQL_HOST   = "localhost"
MYSQL_PORT   = 3306
MYSQL_DB     = "taquilla_papagayo"
MYSQL_USER   = ""   # Llenar antes de Fase 2
MYSQL_PASS   = ""
