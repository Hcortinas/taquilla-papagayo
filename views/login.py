"""
views/login.py
Pantalla de inicio de sesión.
"""

import tkinter as tk
from tkinter import messagebox
import datetime

from config import (
    MUSEO_NOMBRE, COLOR_PRIMARIO, COLOR_SECUNDARIO, COLOR_ACENTO,
    COLOR_FONDO, COLOR_TEXTO, COLOR_ERROR, COLOR_BLANCO,
    FUENTE_TITULO, FUENTE_NORMAL, FUENTE_PEQUENA
)
from database.db_manager import autenticar_usuario

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


class LoginView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        self.master = master
        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        # ── Encabezado ──────────────────────────────────────
        header = tk.Frame(self, bg=COLOR_PRIMARIO, height=160)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo — tk.PhotoImage funciona con PNG sin dependencias externas
        try:
            from config import LOGO_PATH
            self._logo_img = tk.PhotoImage(file=LOGO_PATH).subsample(3, 3)
            tk.Label(header, image=self._logo_img,
                     bg=COLOR_PRIMARIO).pack(pady=(14, 2))
        except Exception:
            tk.Label(header, text="🪁", font=("Segoe UI", 38),
                     bg=COLOR_PRIMARIO, fg=COLOR_BLANCO).pack(pady=(18, 2))

        tk.Label(
            header, text=MUSEO_NOMBRE,
            font=FUENTE_TITULO, bg=COLOR_PRIMARIO, fg=COLOR_BLANCO
        ).pack()

        # Fecha actual en el header
        hoy = datetime.datetime.now()
        dia_nombre = DIAS_ES[hoy.weekday()]
        fecha_str  = hoy.strftime(f"{dia_nombre} %d/%m/%Y")
        tk.Label(
            header, text=fecha_str,
            font=FUENTE_PEQUENA, bg=COLOR_PRIMARIO, fg="#a8dadc"
        ).pack()

        # ── Aviso lunes ──────────────────────────────────────
        if hoy.weekday() == 0:  # 0 = lunes
            aviso = tk.Frame(self, bg="#e63946", pady=8)
            aviso.pack(fill="x")
            tk.Label(aviso, text="⚠️  El museo no labora los lunes.",
                     font=("Segoe UI", 10, "bold"),
                     bg="#e63946", fg=COLOR_BLANCO).pack()

        # ── Formulario ──────────────────────────────────────
        form = tk.Frame(self, bg=COLOR_FONDO, padx=40)
        form.pack(fill="both", expand=True, pady=30)

        tk.Label(form, text="Usuario", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w").pack(fill="x")
        self.entry_usuario = tk.Entry(form, font=FUENTE_NORMAL, relief="solid", bd=1)
        self.entry_usuario.pack(fill="x", ipady=6, pady=(2, 14))

        tk.Label(form, text="Contraseña", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w").pack(fill="x")
        self.entry_pass = tk.Entry(form, font=FUENTE_NORMAL, show="*",
                                   relief="solid", bd=1)
        self.entry_pass.pack(fill="x", ipady=6, pady=(2, 20))

        # Botón
        tk.Button(
            form, text="Iniciar Sesión",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_ACENTO, fg=COLOR_BLANCO,
            relief="flat", cursor="hand2",
            activebackground=COLOR_SECUNDARIO,
            command=self._login
        ).pack(fill="x", ipady=10)

        # Error label
        self.lbl_error = tk.Label(form, text="", font=FUENTE_PEQUENA,
                                  bg=COLOR_FONDO, fg=COLOR_ERROR)
        self.lbl_error.pack(pady=8)

        # Bind Enter
        self.master.bind("<Return>", lambda e: self._login())
        self.entry_usuario.focus()

    def _login(self):
        usuario  = self.entry_usuario.get().strip()
        password = self.entry_pass.get().strip()

        if not usuario or not password:
            self.lbl_error.config(text="Completa todos los campos.")
            return

        # Advertencia si es lunes (pero no bloquea — admin puede necesitar acceso)
        if datetime.datetime.now().weekday() == 0:
            if not messagebox.askyesno("Día no laborable",
                "Hoy es lunes y el museo no labora.\n¿Deseas continuar de todas formas?"):
                return

        user = autenticar_usuario(usuario, password)
        if not user:
            self.lbl_error.config(text="Usuario o contraseña incorrectos.")
            self.entry_pass.delete(0, "end")
            return

        self._abrir_principal(user)

    def _abrir_principal(self, user: dict):
        from views.venta import VentaView
        from database.db_manager import abrir_turno

        turno_id = abrir_turno(user["id"])

        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.resizable(True, True)
        w, h = 1100, 700
        x = (self.master.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.master.winfo_screenheight() // 2) - (h // 2)
        self.master.geometry(f"{w}x{h}+{x}+{y}")

        VentaView(self.master, user=user, turno_id=turno_id)
