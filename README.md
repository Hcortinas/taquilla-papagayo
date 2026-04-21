# Sistema de Taquilla – Museo Interactivo Papagayo

## Requisitos
- Python 3.11+
- Tkinter (incluido en Python estándar)
- ReportLab

## Instalación

```bash
# 1. Clonar / copiar el proyecto
cd taquilla_papagayo

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

## Estructura del proyecto
```
taquilla_papagayo/
├── main.py              ← Punto de entrada
├── config.py            ← Configuración (colores, rutas, MySQL)
├── requirements.txt
├── database/
│   ├── schema.sql       ← Esquema de tablas SQLite
│   └── db_manager.py    ← Toda la lógica de BD
├── views/
│   ├── login.py         ← Pantalla de login
│   ├── venta.py         ← Pantalla principal de venta
│   └── reporte.py       ← Reporte de turno
├── utils/
│   └── pdf_export.py    ← Exportación PDF con ReportLab
├── data/                ← Se crea automáticamente (aquí vive taquilla.db)
└── reportes/            ← Se crea automáticamente (PDFs generados)
```

## Usuarios por defecto
| Usuario    | Contraseña  | Rol         |
|------------|-------------|-------------|
| admin      | admin123    | Administrador |
| taquilla1  | taquilla1   | Taquillero  |
| taquilla2  | taquilla2   | Taquillero  |

⚠️ **Cambiar contraseñas antes de poner en producción.**

## Tipos de boleto incluidos
| Clave        | Nombre                          | Precio   |
|--------------|---------------------------------|----------|
| NINO         | Niño (2–11 años)                | $83      |
| ADULTO       | Adulto (12–59 años)             | $100     |
| 3RA_EDAD     | 3ra Edad / Cap. Diferentes      | $50      |
| ESTUDIANTE   | Estudiante / Profesor           | $83      |
| MIERCOLES_2X1| Miércoles 2x1                   | $100     |
| FAM_4        | Paquete Familiar (4 personas)   | $219     |
| FAM_5        | Paquete Familiar (5 personas)   | $267     |
| PASE_2X1     | Pase Cortesía 2x1               | $83      |
| CLUB         | Club Papagayo                   | $100     |
| PASAPORTE    | Pasaporte Papagayo              | Variable |
| CORTESIA     | Cortesía                        | Gratis   |
| BEBE         | Niño menor de 2 años            | Gratis   |

## Roadmap
- **Fase 1 (actual):** Sistema local SQLite + UI completa
- **Fase 2:** Sincronización MySQL remoto
- **Fase 3:** Dashboard admin (reportes por mes, Power BI export)
- **Fase 4:** Impresión de tickets (ESC/POS)
