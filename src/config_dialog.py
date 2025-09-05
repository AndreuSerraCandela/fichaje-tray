from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .config import load_config, save_config, APP_NAME


class ConfigDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("320x130")
        self.root.resizable(False, False)
        
        # Centrar en pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (320 // 2)
        y = (self.root.winfo_screenheight() // 2) - (130 // 2)
        self.root.geometry(f"320x130+{x}+{y}")
        
        self.cfg = load_config()
        self._create_widgets()
        
        # Hacer el diálogo modal
        self.root.transient()
        self.root.grab_set()
        self.root.focus_set()

    def _create_widgets(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Código de empleado:").pack(anchor=tk.W)
        self.var = tk.StringVar(value=self.cfg.get("employee_code", ""))
        self.entry = ttk.Entry(main, textvariable=self.var)
        self.entry.pack(fill=tk.X)
        self.entry.focus_set()

        btns = ttk.Frame(main)
        btns.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(btns, text="Guardar", command=self._on_save).pack(side=tk.RIGHT)
        ttk.Button(btns, text="Cancelar", command=self._on_cancel).pack(side=tk.RIGHT, padx=(0, 8))

    def _on_save(self) -> None:
        self.cfg["employee_code"] = self.var.get().strip()
        save_config(self.cfg)
        self.root.destroy()

    def _on_cancel(self) -> None:
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


def run_dialog() -> None:
    """Función de compatibilidad para mantener la API existente"""
    dialog = ConfigDialog()
    dialog.run()


if __name__ == "__main__":
    run_dialog()


