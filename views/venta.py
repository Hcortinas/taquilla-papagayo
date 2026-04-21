"""
views/venta.py - Pantalla principal de venta de boletos.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime

from config import (
    COLOR_PRIMARIO, COLOR_SECUNDARIO, COLOR_ACENTO,
    COLOR_FONDO, COLOR_TEXTO, COLOR_ERROR, COLOR_EXITO, COLOR_BLANCO,
    FUENTE_NORMAL, FUENTE_PEQUENA, MUSEO_NOMBRE, LOGO_PATH
)
from database.db_manager import (
    obtener_tipos_boleto, registrar_venta, registrar_visita_pasaporte,
    reporte_turno, cerrar_turno
)

# ── Reglas por clave ─────────────────────────────────────────
# personas: cuántas personas entran por 1 boleto
# solo_nino / solo_adulto / mixto (distinguir_edad=True)
REGLAS_BOLETO = {
    "NINO":          {"personas": 1, "solo_nino":   True},
    "ADULTO":        {"personas": 1, "solo_adulto": True},
    "3RA_EDAD":      {"personas": 1, "mixto":       True},   # puede ser niño/adulto con discapacidad
    "ESTUDIANTE":    {"personas": 1, "mixto":       True},
    "MIERCOLES_2X1": {"personas": 2, "mixto":       True},
    "FAM_4":         {"personas": 4, "mixto":       True},
    "FAM_5":         {"personas": 5, "mixto":       True},
    "PASE_2X1":      {"personas": 2, "mixto":       True},
    "CLUB":          {"personas": 1, "solo_nino":   True},
    "CORTESIA":      {"personas": 1, "mixto":       True},
    "BEBE":          {"personas": 1, "solo_nino":   True},
}


class VentaView(tk.Frame):
    def __init__(self, master, user: dict, turno_id: int):
        super().__init__(master, bg=COLOR_FONDO)
        self.master   = master
        self.user     = user
        self.turno_id = turno_id
        self.carrito: list[dict] = []
        self.pack(fill="both", expand=True)
        self._cargar_tipos()
        self._build_ui()

    def _cargar_tipos(self):
        self.tipos = obtener_tipos_boleto()
        self.tipos_dict = {t["id"]: t for t in self.tipos}

    def _build_ui(self):
        self._build_header()
        c = tk.Frame(self, bg=COLOR_FONDO)
        c.pack(fill="both", expand=True, padx=10, pady=6)
        c.columnconfigure(0, weight=3)
        c.columnconfigure(1, weight=2)
        c.rowconfigure(0, weight=1)
        self._build_panel_boletos(c)
        self._build_panel_carrito(c)

    # ── Header ───────────────────────────────────────────────
    def _build_header(self):
        bar = tk.Frame(self, bg=COLOR_PRIMARIO, height=54)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Logo
        try:
            self._logo_img = tk.PhotoImage(file=LOGO_PATH).subsample(5, 5)
            tk.Label(bar, image=self._logo_img,
                     bg=COLOR_PRIMARIO).pack(side="left", padx=(8, 4))
        except Exception:
            tk.Label(bar, text="🪁", font=("Segoe UI", 22),
                     bg=COLOR_PRIMARIO, fg=COLOR_BLANCO).pack(side="left", padx=(10, 4))

        DIAS_ES = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        hoy = datetime.datetime.now()
        fecha_txt = hoy.strftime(f"{DIAS_ES[hoy.weekday()]} %d/%m/%Y")
        tk.Label(bar, text=f"{MUSEO_NOMBRE}  —  {fecha_txt}",
                 font=("Segoe UI", 12, "bold"),
                 bg=COLOR_PRIMARIO, fg=COLOR_BLANCO).pack(side="left", padx=6)

        tk.Label(bar, text=f"👤 {self.user['nombre']}",
                 font=FUENTE_NORMAL, bg=COLOR_PRIMARIO,
                 fg="#a8dadc").pack(side="right", padx=14)
        self.lbl_hora = tk.Label(bar, text="", font=FUENTE_PEQUENA,
                                  bg=COLOR_PRIMARIO, fg="#a8dadc")
        self.lbl_hora.pack(side="right", padx=10)
        self._tick_reloj()

    def _tick_reloj(self):
        self.lbl_hora.config(text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_reloj)

    # ── Panel boletos ────────────────────────────────────────
    def _build_panel_boletos(self, parent):
        frame = tk.LabelFrame(parent, text="Tipo de Boleto",
                              font=FUENTE_NORMAL, bg=COLOR_FONDO,
                              fg=COLOR_PRIMARIO, padx=8, pady=8)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        canvas = tk.Canvas(frame, bg=COLOR_FONDO, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLOR_FONDO)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Botones Pasaporte (fila especial) ──
        pas_frame = tk.Frame(inner, bg=COLOR_FONDO)
        pas_frame.grid(row=0, column=0, columnspan=3,
                       sticky="ew", padx=4, pady=(4, 2))
        pas_frame.columnconfigure(0, weight=1)
        pas_frame.columnconfigure(1, weight=1)

        tk.Button(pas_frame,
                  text="💳 Venta Pasaporte Papagayo\n$550",
                  font=("Segoe UI", 9, "bold"),
                  bg="#1d6a2b", fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2", wraplength=180,
                  command=self._vender_pasaporte
                  ).grid(row=0, column=0, sticky="ew",
                          padx=(0, 3), ipadx=4, ipady=8)

        tk.Button(pas_frame,
                  text="🪪 Visita con Pasaporte\n(sin cobro)",
                  font=("Segoe UI", 9, "bold"),
                  bg="#6c757d", fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2", wraplength=180,
                  command=self._registrar_visita_pasaporte
                  ).grid(row=0, column=1, sticky="ew",
                          padx=(3, 0), ipadx=4, ipady=8)

        # ── Resto de boletos ──
        cols = 3
        tipos_venta = [t for t in self.tipos if t["clave"] != "PASAPORTE"]
        for i, tipo in enumerate(tipos_venta):
            r = (i // cols) + 1
            c = i % cols
            precio_txt = f"${tipo['precio']:.0f}" if tipo["precio"] > 0 else "GRATIS"
            tk.Button(inner,
                      text=f"{tipo['nombre']}\n{precio_txt}",
                      font=("Segoe UI", 9, "bold"),
                      bg=COLOR_SECUNDARIO, fg=COLOR_BLANCO,
                      relief="flat", cursor="hand2",
                      wraplength=160, justify="center",
                      activebackground=COLOR_ACENTO,
                      command=lambda t=tipo: self._agregar_al_carrito(t)
                      ).grid(row=r, column=c, padx=4, pady=4,
                              sticky="nsew", ipadx=4, ipady=10)
            inner.columnconfigure(c, weight=1)

    # ── Panel carrito ────────────────────────────────────────
    def _build_panel_carrito(self, parent):
        frame = tk.LabelFrame(parent, text="Carrito de Venta",
                              font=FUENTE_NORMAL, bg=COLOR_FONDO,
                              fg=COLOR_PRIMARIO, padx=8, pady=8)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        cols_tree = ("Boleto", "Cant", "P.Unit", "Subtotal")
        self.tree = ttk.Treeview(frame, columns=cols_tree,
                                  show="headings", height=12)
        for c in cols_tree:
            self.tree.heading(c, text=c)
        self.tree.column("Boleto",   width=160)
        self.tree.column("Cant",     width=50,  anchor="center")
        self.tree.column("P.Unit",   width=70,  anchor="e")
        self.tree.column("Subtotal", width=80,  anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)

        tk.Button(frame, text="✖ Quitar seleccionado",
                  font=FUENTE_PEQUENA, bg=COLOR_ERROR, fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2", command=self._quitar_item
                  ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4,0))

        tf = tk.Frame(frame, bg=COLOR_FONDO)
        tf.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)
        tk.Label(tf, text="TOTAL:", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
        self.lbl_total = tk.Label(tf, text="$0.00",
                                   font=("Segoe UI", 18, "bold"),
                                   bg=COLOR_FONDO, fg=COLOR_PRIMARIO)
        self.lbl_total.pack(side="right")

        pf = tk.Frame(frame, bg=COLOR_FONDO)
        pf.grid(row=3, column=0, columnspan=2, sticky="ew")
        tk.Label(pf, text="Forma de pago:", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO).pack(side="left")
        self.pago_var = tk.StringVar(value="efectivo")
        tk.Radiobutton(pf, text="Efectivo", variable=self.pago_var,
                       value="efectivo", bg=COLOR_FONDO,
                       font=FUENTE_NORMAL).pack(side="left", padx=8)
        tk.Radiobutton(pf, text="TPV", variable=self.pago_var,
                       value="tpv", bg=COLOR_FONDO,
                       font=FUENTE_NORMAL).pack(side="left")

        bf = tk.Frame(frame, bg=COLOR_FONDO)
        bf.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8,0))
        bf.columnconfigure(0, weight=1)
        bf.columnconfigure(1, weight=1)
        tk.Button(bf, text="🧹 Limpiar", font=FUENTE_NORMAL,
                  bg="#6c757d", fg=COLOR_BLANCO, relief="flat", cursor="hand2",
                  command=self._limpiar_carrito
                  ).grid(row=0, column=0, sticky="ew", padx=(0,4), ipady=8)
        tk.Button(bf, text="✅ Cobrar", font=("Segoe UI", 11, "bold"),
                  bg=COLOR_EXITO, fg=COLOR_BLANCO, relief="flat", cursor="hand2",
                  command=self._iniciar_cobro
                  ).grid(row=0, column=1, sticky="ew", ipady=8)

        tk.Button(frame, text="📊 Ver Reporte del Turno",
                  font=FUENTE_PEQUENA, bg=COLOR_ACENTO, fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2", command=self._ver_reporte
                  ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6,0), ipady=6)
        tk.Button(frame, text="🔒 Cerrar Turno",
                  font=FUENTE_PEQUENA, bg=COLOR_ERROR, fg=COLOR_BLANCO,
                  relief="flat", cursor="hand2", command=self._cerrar_turno
                  ).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4,0), ipady=6)

    # ── Carrito ──────────────────────────────────────────────
    def _agregar_al_carrito(self, tipo: dict):
        for item in self.carrito:
            if item["tipo_boleto_id"] == tipo["id"]:
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                self._refrescar_tree()
                return
        self.carrito.append({
            "tipo_boleto_id":  tipo["id"],
            "clave":           tipo["clave"],
            "nombre":          tipo["nombre"],
            "cantidad":        1,
            "precio_unitario": tipo["precio"],
            "subtotal":        tipo["precio"],
        })
        self._refrescar_tree()

    def _quitar_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.carrito):
            self.carrito.pop(idx)
            self._refrescar_tree()

    def _limpiar_carrito(self):
        self.carrito.clear()
        self._refrescar_tree()

    def _refrescar_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        total = 0.0
        for item in self.carrito:
            self.tree.insert("", "end", values=(
                item["nombre"], item["cantidad"],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total += item["subtotal"]
        self.lbl_total.config(text=f"${total:.2f}")

    # ── Pasaporte ────────────────────────────────────────────
    def _vender_pasaporte(self):
        """Venta normal del Pasaporte Papagayo a $550."""
        tipo_pas = next((t for t in self.tipos if t["clave"] == "PASAPORTE"), None)
        if not tipo_pas:
            return
        # Agregar al carrito con precio fijo $550
        for item in self.carrito:
            if item["clave"] == "PASAPORTE":
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * 550.0
                self._refrescar_tree()
                return
        self.carrito.append({
            "tipo_boleto_id":  tipo_pas["id"],
            "clave":           "PASAPORTE",
            "nombre":          "Pasaporte Papagayo",
            "cantidad":        1,
            "precio_unitario": 550.0,
            "subtotal":        550.0,
        })
        self._refrescar_tree()

    def _registrar_visita_pasaporte(self):
        """Visita de portador de Pasaporte — sin cobro."""
        dialog = PasaporteVisitaDialog(self)
        self.wait_window(dialog)
        if not dialog.resultado:
            return
        try:
            registrar_visita_pasaporte(
                turno_id=self.turno_id,
                usuario_id=self.user["id"],
                visitantes=dialog.resultado
            )
            messagebox.showinfo("Visita registrada",
                                "✅ Visita de Pasaporte Papagayo registrada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Cobro ────────────────────────────────────────────────
    def _iniciar_cobro(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agrega boletos antes de cobrar.")
            return
        total = sum(i["subtotal"] for i in self.carrito)
        monto_recibido = None
        if self.pago_var.get() == "efectivo":
            monto_str = simpledialog.askstring(
                "Cobro en Efectivo",
                f"Total a cobrar: ${total:.2f}\n\nMonto recibido:",
                parent=self)
            if monto_str is None:
                return
            try:
                monto_recibido = float(monto_str)
                if monto_recibido < total:
                    messagebox.showerror("Monto insuficiente",
                        f"Recibido ${monto_recibido:.2f} < Total ${total:.2f}")
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingresa un monto válido.")
                return

        visitantes = self._capturar_visitantes()
        if visitantes is None:
            return

        try:
            registrar_venta(
                turno_id=self.turno_id, usuario_id=self.user["id"],
                forma_pago=self.pago_var.get(), items=self.carrito,
                monto_recibido=monto_recibido, visitantes_data=visitantes)
        except Exception as e:
            messagebox.showerror("Error al registrar", str(e))
            return

        cambio = (monto_recibido - total) if monto_recibido else 0
        msg = f"✅ Venta registrada\nTotal: ${total:.2f}"
        if cambio > 0:
            msg += f"\nCambio: ${cambio:.2f}"
        messagebox.showinfo("Venta exitosa", msg)
        self._limpiar_carrito()

    def _capturar_visitantes(self):
        # El Pasaporte en venta solo registra 1 persona (el comprador)
        carrito_para_dialog = []
        for item in self.carrito:
            if item["clave"] == "PASAPORTE":
                carrito_para_dialog.append({**item, "clave": "ADULTO"})
            else:
                carrito_para_dialog.append(item)
        dialog = VisitantesDialog(self, carrito_para_dialog)
        self.wait_window(dialog)
        return dialog.resultado

    def _ver_reporte(self):
        from views.reporte import ReporteView
        ReporteView(self.master, turno_id=self.turno_id)

    def _cerrar_turno(self):
        if not messagebox.askyesno("Cerrar Turno",
                "¿Deseas cerrar el turno?\nEsto generará el reporte final."):
            return
        cerrar_turno(self.turno_id)
        from views.reporte import ReporteView
        ReporteView(self.master, turno_id=self.turno_id, cierre=True)


# ════════════════════════════════════════════════════════════
#  DIÁLOGO DE VISITANTES — layout en 2 filas para que quepan
# ════════════════════════════════════════════════════════════

class VisitantesDialog(tk.Toplevel):
    def __init__(self, parent, carrito: list[dict]):
        super().__init__(parent)
        self.title("Captura de Visitantes")
        self.resizable(False, True)
        self.grab_set()
        self.resultado = None
        self.carrito   = carrito
        self.bloques   = []
        self._build_ui()
        self._centrar()

    def _centrar(self):
        self.update_idletasks()
        w = 560
        h = min(self.winfo_reqheight() + 40, 580)
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        tk.Label(self, text="Captura el sexo de los visitantes por boleto:",
                 font=FUENTE_NORMAL, padx=14, pady=8,
                 bg=COLOR_FONDO).pack(fill="x")

        container = tk.Frame(self, bg=COLOR_FONDO)
        container.pack(fill="both", expand=True, padx=10)
        canvas = tk.Canvas(container, bg=COLOR_FONDO, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLOR_FONDO)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for item in self.carrito:
            clave    = item.get("clave", "ADULTO")
            regla    = REGLAS_BOLETO.get(clave, {"personas": 1, "mixto": True})
            pers_por = regla.get("personas", 1)
            total_p  = item["cantidad"] * pers_por
            solo_n   = regla.get("solo_nino",   False)
            solo_a   = regla.get("solo_adulto", False)
            mixto    = regla.get("mixto",        False)

            bloque = tk.LabelFrame(
                inner,
                text=f"  {item['nombre']}  "
                     f"(x{item['cantidad']} = {total_p} persona(s))  ",
                font=("Segoe UI", 9, "bold"),
                bg=COLOR_FONDO, fg=COLOR_PRIMARIO, padx=12, pady=8)
            bloque.pack(fill="x", pady=6, padx=4)

            vb = {"total_esperado": total_p}

            if solo_n:
                # Fila única: Niños ♂  |  Niñas ♀
                vb["nino_m"] = self._contador(bloque, "Niños ♂",  0, 0, total_p)
                vb["nino_f"] = self._contador(bloque, "Niñas ♀",  0, 1, total_p)

            elif solo_a:
                # Fila única: Hombres ♂  |  Mujeres ♀
                vb["adul_m"] = self._contador(bloque, "Hombres ♂", 0, 0, total_p)
                vb["adul_f"] = self._contador(bloque, "Mujeres ♀", 0, 1, total_p)

            else:
                # 2 filas: fila 0 = niños, fila 1 = adultos
                tk.Label(bloque, text="Niños:", font=("Segoe UI", 8, "bold"),
                         bg=COLOR_FONDO, fg="#555").grid(
                             row=0, column=0, sticky="w", padx=(0,4))
                vb["nino_m"] = self._contador(bloque, "♂ Masculino", 0, 1, total_p)
                vb["nino_f"] = self._contador(bloque, "♀ Femenino",  0, 2, total_p)

                tk.Label(bloque, text="Adultos:", font=("Segoe UI", 8, "bold"),
                         bg=COLOR_FONDO, fg="#555").grid(
                             row=1, column=0, sticky="w", padx=(0,4))
                vb["adul_m"] = self._contador(bloque, "♂ Masculino", 1, 1, total_p)
                vb["adul_f"] = self._contador(bloque, "♀ Femenino",  1, 2, total_p)

            lbl = tk.Label(bloque, text=f"Total: 0 / {total_p}",
                           font=("Segoe UI", 9, "italic"),
                           bg=COLOR_FONDO, fg="#555")
            lbl.grid(row=3, column=0, columnspan=6, sticky="w", pady=(4,0))
            vb["lbl_suma"] = lbl

            for key in ("nino_m","nino_f","adul_m","adul_f"):
                if key in vb:
                    vb[key].trace_add("write",
                        lambda *a, v=vb: self._actualizar_suma(v))

            self.bloques.append(vb)

        btn_frame = tk.Frame(self, bg=COLOR_FONDO, pady=10)
        btn_frame.pack()
        tk.Button(btn_frame, text="Cancelar", width=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(btn_frame, text="✅ Confirmar", width=14,
                  bg=COLOR_EXITO, fg=COLOR_BLANCO, relief="flat",
                  command=self._confirmar).pack(side="left", padx=6)

    def _contador(self, parent, label, row, col_base, maximo):
        """Crea label + spinbox en la fila/columna indicada."""
        var = tk.IntVar(value=0)
        tk.Label(parent, text=label, font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO).grid(row=row, column=col_base*2+1,
                                       padx=(12,2), pady=3, sticky="e")
        tk.Spinbox(parent, textvariable=var, from_=0, to=maximo,
                   width=5, font=FUENTE_NORMAL).grid(
                       row=row, column=col_base*2+2, padx=(0,8))
        return var

    def _actualizar_suma(self, vb):
        total = sum(vb[k].get() for k in
                    ("nino_m","nino_f","adul_m","adul_f") if k in vb)
        esp = vb["total_esperado"]
        vb["lbl_suma"].config(
            text=f"Total: {total} / {esp}",
            fg=COLOR_EXITO if total == esp else COLOR_ERROR)

    def _confirmar(self):
        resultado = []
        for vb in self.bloques:
            esp   = vb["total_esperado"]
            total = sum(vb[k].get() for k in
                        ("nino_m","nino_f","adul_m","adul_f") if k in vb)
            if total != esp:
                messagebox.showerror("Total incorrecto",
                    f"Un boleto tiene {total} persona(s) "
                    f"pero se esperan {esp}.\nVerifica los contadores.")
                return
            for key, sexo, es_nino in [
                ("nino_m","M",True), ("nino_f","F",True),
                ("adul_m","M",False),("adul_f","F",False)
            ]:
                if key in vb:
                    for _ in range(vb[key].get()):
                        resultado.append({
                            "sexo": sexo,
                            "edad": 5 if es_nino else 25,
                            "es_local": 1
                        })
        self.resultado = resultado
        self.destroy()


# ════════════════════════════════════════════════════════════
#  DIÁLOGO VISITA PASAPORTE
# ════════════════════════════════════════════════════════════

class PasaporteVisitaDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Visita — Pasaporte Papagayo")
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        self._build_ui()
        self._centrar()

    def _centrar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        tk.Label(self, text="Pasaporte Papagayo — Visita sin cobro",
                 font=("Segoe UI", 11, "bold"),
                 bg=COLOR_PRIMARIO, fg=COLOR_BLANCO, pady=10).pack(fill="x")
        frame = tk.Frame(self, bg=COLOR_FONDO, padx=20, pady=14)
        frame.pack()
        tk.Label(frame, text="Tipo:", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO).grid(row=0, column=0, sticky="w", pady=4)
        self.tipo_var = tk.StringVar(value="Adulto")
        ttk.Combobox(frame, textvariable=self.tipo_var,
                     values=["Adulto", "Niño"], state="readonly",
                     width=10).grid(row=0, column=1, padx=10)
        tk.Label(frame, text="Sexo:", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO).grid(row=1, column=0, sticky="w", pady=4)
        self.sexo_var = tk.StringVar(value="M – Masculino")
        ttk.Combobox(frame, textvariable=self.sexo_var,
                     values=["M – Masculino", "F – Femenino"],
                     state="readonly", width=16).grid(row=1, column=1, padx=10)
        btn = tk.Frame(self, bg=COLOR_FONDO, pady=10)
        btn.pack()
        tk.Button(btn, text="Cancelar", width=10,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(btn, text="✅ Registrar", width=12,
                  bg=COLOR_EXITO, fg=COLOR_BLANCO, relief="flat",
                  command=self._confirmar).pack(side="left", padx=6)

    def _confirmar(self):
        sexo    = self.sexo_var.get().split(" ")[0]
        es_nino = self.tipo_var.get() == "Niño"
        self.resultado = [{"sexo": sexo, "edad": 5 if es_nino else 25, "es_local": 1}]
        self.destroy()
