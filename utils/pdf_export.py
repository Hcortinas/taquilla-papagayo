"""
utils/pdf_export.py
Exporta reportes de turno a PDF usando ReportLab.
"""

import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

from config import MUSEO_NOMBRE, MUSEO_CIUDAD, REPORTS_DIR


AZUL   = colors.HexColor("#005f73")
AMBER  = colors.HexColor("#ee9b00")
CLARO  = colors.HexColor("#e9f5f7")


def exportar_reporte_turno(turno_id: int, data: dict) -> str:
    """
    Genera el PDF del reporte de turno.
    Devuelve la ruta del archivo generado.
    """
    fecha_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"reporte_turno_{turno_id}_{fecha_str}.pdf"
    filepath  = os.path.join(REPORTS_DIR, filename)

    doc    = SimpleDocTemplate(filepath, pagesize=letter,
                                topMargin=0.6*inch, bottomMargin=0.6*inch,
                                leftMargin=0.75*inch, rightMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    # ── Encabezado ──────────────────────────────────────────
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                  textColor=AZUL, fontSize=18, spaceAfter=4)
    sub_style   = ParagraphStyle("Sub", parent=styles["Normal"],
                                  textColor=colors.grey, fontSize=10)

    story.append(Paragraph(MUSEO_NOMBRE, title_style))
    story.append(Paragraph(f"{MUSEO_CIUDAD}  —  Reporte de Turno #{turno_id}", sub_style))
    story.append(Paragraph(
        datetime.datetime.now().strftime("Generado el %d/%m/%Y a las %H:%M"),
        sub_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=AZUL, spaceAfter=12))

    # ── Resumen ──────────────────────────────────────────────
    story.append(Paragraph("Resumen de Ingresos", styles["Heading2"]))
    total_general = sum(t.get("suma", 0) for t in data["totales"])
    total_txn     = sum(t.get("cantidad", 0) for t in data["totales"])

    resumen_data = [["Concepto", "Transacciones", "Monto"]]
    for t in data["totales"]:
        resumen_data.append([
            t["forma_pago"].capitalize(),
            str(t["cantidad"]),
            f"${t['suma']:,.2f}"
        ])
    resumen_data.append(["TOTAL", str(total_txn), f"${total_general:,.2f}"])

    tbl = Table(resumen_data, colWidths=[3*inch, 1.5*inch, 2*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0),  (-1, 0),  AZUL),
        ("TEXTCOLOR",   (0, 0),  (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0),  (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",  (0, -1), (-1, -1), AMBER),
        ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID",        (0, 0),  (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [CLARO, colors.white]),
        ("ALIGN",       (1, 0),  (-1, -1), "CENTER"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.3*inch))

    # ── Detalle de ventas ────────────────────────────────────
    if data["ventas"]:
        story.append(Paragraph("Detalle de Transacciones", styles["Heading2"]))
        v_data = [["Folio", "Hora", "Total", "Pago", "Taquillero"]]
        for v in data["ventas"]:
            hora = v["fecha_hora"][11:16] if v["fecha_hora"] else ""
            v_data.append([
                v["folio"], hora,
                f"${v['total']:.2f}",
                v["forma_pago"],
                v.get("taquillero", "–")
            ])

        vt = Table(v_data, colWidths=[2.2*inch, 0.8*inch, 1*inch, 0.9*inch, 1.5*inch])
        vt.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0),  (-1, 0),  AZUL),
            ("TEXTCOLOR",      (0, 0),  (-1, 0),  colors.white),
            ("FONTNAME",       (0, 0),  (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0),  (-1, -1), 8),
            ("GRID",           (0, 0),  (-1, -1), 0.3, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1),  (-1, -1), [CLARO, colors.white]),
            ("ALIGN",          (1, 0),  (-1, -1), "CENTER"),
        ]))
        story.append(vt)
        story.append(Spacer(1, 0.3*inch))

    # ── Visitantes ───────────────────────────────────────────
    if data["visitantes"]:
        story.append(Paragraph("Perfil de Visitantes", styles["Heading2"]))
        sexo_labels = {"M": "Masculino", "F": "Femenino",
                       "NB": "No Binario", "NE": "No Especificado"}
        total_vis   = sum(v["total"] for v in data["visitantes"])

        vis_data = [["Sexo", "Cantidad", "Porcentaje"]]
        for v in data["visitantes"]:
            pct = (v["total"] / total_vis * 100) if total_vis else 0
            vis_data.append([
                sexo_labels.get(v["sexo"], v["sexo"]),
                str(v["total"]),
                f"{pct:.1f}%"
            ])
        vis_data.append(["TOTAL", str(total_vis), "100%"])

        vit = Table(vis_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        vit.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0),  (-1, 0),  AZUL),
            ("TEXTCOLOR",   (0, 0),  (-1, 0),  colors.white),
            ("FONTNAME",    (0, 0),  (-1, 0),  "Helvetica-Bold"),
            ("BACKGROUND",  (0, -1), (-1, -1), AMBER),
            ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID",        (0, 0),  (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [CLARO, colors.white]),
            ("ALIGN",       (1, 0),  (-1, -1), "CENTER"),
        ]))
        story.append(vit)

    # ── Pie de página ────────────────────────────────────────
    story.append(Spacer(1, 0.4*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph(
        f"Documento generado automáticamente por el Sistema de Taquilla – {MUSEO_NOMBRE}",
        ParagraphStyle("Footer", parent=styles["Normal"],
                        fontSize=8, textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    return filepath
