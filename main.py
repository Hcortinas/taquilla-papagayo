"""
main.py
Punto de entrada del Sistema de Taquilla – Museo Papagayo.
"""

import tkinter as tk
from tkinter import messagebox

from config import APP_TITULO, COLOR_FONDO, LOGO_PATH
from database.db_manager import init_db
from views.login import LoginView


def main():
    # 1. Inicializar base de datos (crea tablas si no existen)
    try:
        init_db()
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", f"No se pudo inicializar la BD:\n{e}")
        return

    # 2. Ventana raíz
    root = tk.Tk()
    root.title(APP_TITULO)
    root.configure(bg=COLOR_FONDO)
    root.resizable(False, False)

    # Ícono de la ventana
    try:
        icon = tk.PhotoImage(file=LOGO_PATH)
        root.iconphoto(True, icon)
    except Exception:
        pass

    # Centrar ventana de login
    root.update_idletasks()
    w, h = 420, 520
    x = (root.winfo_screenwidth()  // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    # 3. Mostrar pantalla de login
    LoginView(root)

    root.mainloop()


if __name__ == "__main__":
    main()
