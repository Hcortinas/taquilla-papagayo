# Taquilla Papagayo

> Desktop ticketing system built for **Museo Interactivo Papagayo**, handling daily visitor ticket sales, shift management, and revenue reporting.

---

## Overview

Designed and developed to replace a manual ticketing process at the museum's entrance. The system manages ticket sales across multiple visitor categories, tracks daily shift revenue, and generates PDF reports for administration.

> ⚠️ Source code is shared with permission from Museo Interactivo Papagayo. Database and reports are excluded from this repository.

---

## Features

**Point of Sale**
- Ticket sales across 12 visitor categories (children, adults, seniors, students, family packages, etc.)
- Free ticket handling (courtesy, infants)
- Variable pricing support (Pasaporte Papagayo)

**Shift Management**
- Session-based shift tracking per cashier
- Shift open/close workflow
- Revenue summary per shift

**Reporting**
- PDF shift reports generated automatically via ReportLab
- Daily revenue breakdown by ticket type
- Reports saved locally with timestamp

**Access Control**
- Role-based login: Administrator and Cashier
- Session management per user

**UI**
- Built with Tkinter — native desktop interface
- Museum branding (logo, color scheme)
- Sandbox/demo mode for testing

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| UI | Tkinter (standard library) |
| Database | SQLite (local) |
| PDF Export | ReportLab |
| Architecture | MVC — views / database / utils |

---

## Project Structure

```
taquilla_papagayo/
├── main.py              ← Entry point
├── config.py            ← Colors, paths, app settings
├── requirements.txt
├── database/
│   ├── schema.sql       ← SQLite table definitions
│   └── db_manager.py    ← All database logic
├── views/
│   ├── login.py         ← Login screen
│   ├── venta.py         ← Main sales screen
│   └── reporte.py       ← Shift report screen
├── utils/
│   └── pdf_export.py    ← PDF generation with ReportLab
└── assets/
    └── logo.png         ← Museum logo
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Hcortinas/taquilla-papagayo.git
cd taquilla_papagayo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

---

## Default Users

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| taquilla1 | taquilla1 | Cashier |
| taquilla2 | taquilla2 | Cashier |

> ⚠️ Change passwords before deploying to production.

---

## Ticket Categories

| Key | Name | Price |
|-----|------|-------|
| NINO | Child (2–11 yrs) | $83 |
| ADULTO | Adult (12–59 yrs) | $100 |
| 3RA_EDAD | Senior / Disability | $50 |
| ESTUDIANTE | Student / Teacher | $83 |
| MIERCOLES_2X1 | Wednesday 2x1 | $100 |
| FAM_4 | Family Pack (4 people) | $219 |
| FAM_5 | Family Pack (5 people) | $267 |
| CORTESIA | Courtesy | Free |
| BEBE | Infant (under 2) | Free |

---

## Roadmap

- ✅ Phase 1: Local SQLite + full UI
- 🔄 Phase 2: Remote MySQL sync
- 📋 Phase 3: Admin dashboard (monthly reports, Power BI export)
- 📋 Phase 4: Ticket printing (ESC/POS)

---

## Status

🔄 **In active development** — Phase 1 complete, Phase 2 in progress.

---

## Author

**Hugo David Cortinas González**
[LinkedIn](https://www.linkedin.com/in/hugodavidcortinasgonzalez) · [GitHub](https://github.com/Hcortinas)