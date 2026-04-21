"""
views/reporte.py
Vista de reporte del turno actual + exportar PDF.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from config import (
    COLOR_PRIMARIO, COLOR_ACENTO, COLOR_FONDO, COLOR_TEXTO,
    COLOR_BLANCO, COLOR_EXITO, FUENTE_TITULO, FUENTE_NORMAL, FUENTE_PEQUENA
)
from database.db_manager import reporte_turno


class ReporteView(tk.Toplevel):
    def __init__(self, parent, turno_id: int, cierre: bool = False):
        super().__init__(parent)
        self.turno_id = turno_id
        self.cierre   = cierre
        self.title("Reporte de Turno" + (" – CIERRE" if cierre else ""))
        self.configure(bg=COLOR_FONDO)
        self.resizable(True, True)
        self.grab_set()

        self.data = reporte_turno(turno_id)
        self._build_ui()
        self._centrar()

    def _centrar(self):
        self.update_idletasks()
        w, h = 700, 560
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=COLOR_PRIMARIO, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        titulo = "📊 Reporte de Turno" + (" — CIERRE DE TURNO" if self.cierre else "")
        tk.Label(hdr, text=titulo, font=FUENTE_TITULO,
                 bg=COLOR_PRIMARIO, fg=COLOR_BLANCO).pack(side="left", padx=14)

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_resumen(notebook)
        self._tab_ventas(notebook)
        self._tab_visitantes(notebook)

        # Botones
        btn_frame = tk.Frame(self, bg=COLOR_FONDO, pady=8)
        btn_frame.pack()
        tk.Button(btn_frame, text="📄 Exportar PDF",
                  font=FUENTE_NORMAL, bg=COLOR_ACENTO, fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2",
                  command=self._exportar_pdf
                  ).pack(side="left", padx=8, ipadx=10, ipady=6)
        tk.Button(btn_frame, text="Cerrar",
                  font=FUENTE_NORMAL, bg="#6c757d", fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2",
                  command=self.destroy
                  ).pack(side="left", padx=8, ipadx=10, ipady=6)

    # ── Tab Resumen ──────────────────────────────────────────

    def _tab_resumen(self, nb):
        frame = tk.Frame(nb, bg=COLOR_FONDO, padx=20, pady=16)
        nb.add(frame, text="  Resumen  ")

        total_general = sum(t.get("suma", 0) for t in self.data["totales"])
        total_ventas  = sum(t.get("cantidad", 0) for t in self.data["totales"])

        stats = [
            ("Total de transacciones", str(total_ventas)),
            ("Ingreso total",           f"${total_general:,.2f}"),
        ]
        for t in self.data["totales"]:
            stats.append((
                f"  · {t['forma_pago'].capitalize()}",
                f"${t['suma']:,.2f}  ({t['cantidad']} transacc.)"
            ))

        for label, valor in stats:
            row = tk.Frame(frame, bg=COLOR_FONDO)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=FUENTE_NORMAL,
                     bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w").pack(side="left")
            tk.Label(row, text=valor, font=("Segoe UI", 11, "bold"),
                     bg=COLOR_FONDO, fg=COLOR_PRIMARIO, anchor="e").pack(side="right")

    # ── Tab Ventas ───────────────────────────────────────────

    def _tab_ventas(self, nb):
        frame = tk.Frame(nb, bg=COLOR_FONDO)
        nb.add(frame, text="  Ventas  ")

        cols = ("Folio", "Hora", "Total", "Pago", "Taquillero")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
        tree.column("Folio",      width=160)
        tree.column("Hora",       width=90, anchor="center")
        tree.column("Total",      width=90, anchor="e")
        tree.column("Pago",       width=80, anchor="center")
        tree.column("Taquillero", width=120)

        for v in self.data["ventas"]:
            hora = v["fecha_hora"][11:16] if v["fecha_hora"] else ""
            tree.insert("", "end", values=(
                v["folio"], hora,
                f"${v['total']:.2f}",
                v["forma_pago"],
                v.get("taquillero", "–")
            ))

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb.pack(side="right", fill="y")

    # ── Tab Visitantes ───────────────────────────────────────

    def _tab_visitantes(self, nb):
        frame = tk.Frame(nb, bg=COLOR_FONDO, padx=20, pady=16)
        nb.add(frame, text="  Visitantes  ")

        # Construir conteos desde el cruce
        conteos = {"nino_M": 0, "nino_F": 0, "adulto_M": 0, "adulto_F": 0}
        for v in self.data.get("visitantes_cruce", []):
            key = f"{v['grupo']}_{v['sexo']}"
            if key in conteos:
                conteos[key] = v["total"]

        total_vis = sum(conteos.values())

        tk.Label(frame,
                 text=f"Total de visitantes: {total_vis}",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(anchor="w", pady=(0, 16))

        etiquetas = [
            ("nino_M",   "Niños"),
            ("nino_F",   "Niñas"),
            ("adulto_M", "Hombres"),
            ("adulto_F", "Mujeres"),
        ]
        for key, nombre in etiquetas:
            cant = conteos[key]
            pct  = (cant / total_vis * 100) if total_vis else 0
            row  = tk.Frame(frame, bg=COLOR_FONDO)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{nombre}:",
                     font=("Segoe UI", 11), bg=COLOR_FONDO,
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=f"{cant}",
                     font=("Segoe UI", 13, "bold"),
                     bg=COLOR_FONDO, fg=COLOR_PRIMARIO,
                     width=6, anchor="e").pack(side="left")
            tk.Label(row, text=f"  ({pct:.1f}%)",
                     font=("Segoe UI", 10),
                     bg=COLOR_FONDO, fg="#6c757d").pack(side="left")

    # ── Exportar PDF ─────────────────────────────────────────

    def _exportar_pdf(self):
        try:
            from utils.pdf_export import exportar_reporte_turno
            path = exportar_reporte_turno(self.turno_id, self.data)
            messagebox.showinfo("PDF Generado", f"Reporte guardado en:\n{path}")
        except ImportError:
            messagebox.showerror("Error",
                "ReportLab no está instalado.\nEjecuta: pip install reportlab")
        except Exception as e:
            messagebox.showerror("Error al generar PDF", str(e))
