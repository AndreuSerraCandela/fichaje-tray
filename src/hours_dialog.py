import tkinter as tk
from tkinter import ttk, messagebox
from .config import load_config, save_config


class HoursDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configurar Horas de Fichaje Automático")
        self.root.geometry("400x350")  # Aumentar altura para el nuevo elemento
        self.root.resizable(False, False)
        
        # Centrar en pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (350 // 2)
        self.root.geometry(f"400x350+{x}+{y}")
        
        # Cargar configuración actual
        self.config = load_config()
        
        self._create_widgets()
        self._load_current_values()
        
        # Hacer el diálogo modal
        self.root.transient()
        self.root.grab_set()
        self.root.focus_set()
        
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Configurar Horas de Fichaje Automático", 
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Hora de entrada
        ttk.Label(main_frame, text="Hora de Entrada:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entrada_var = tk.StringVar()
        entrada_frame = ttk.Frame(main_frame)
        entrada_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.entrada_hour = ttk.Spinbox(entrada_frame, from_=0, to=23, width=5, 
                                       textvariable=self.entrada_var, format="%02.0f")
        self.entrada_hour.grid(row=0, column=0)
        ttk.Label(entrada_frame, text=":").grid(row=0, column=1, padx=2)
        self.entrada_minute = ttk.Spinbox(entrada_frame, from_=0, to=59, width=5, format="%02.0f")
        self.entrada_minute.grid(row=0, column=2)
        
        # Hora de salida
        ttk.Label(main_frame, text="Hora de Salida:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.salida_var = tk.StringVar()
        salida_frame = ttk.Frame(main_frame)
        salida_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.salida_hour = ttk.Spinbox(salida_frame, from_=0, to=23, width=5, 
                                      textvariable=self.salida_var, format="%02.0f")
        self.salida_hour.grid(row=0, column=0)
        ttk.Label(salida_frame, text=":").grid(row=0, column=1, padx=2)
        self.salida_minute = ttk.Spinbox(salida_frame, from_=0, to=59, width=5, format="%02.0f")
        self.salida_minute.grid(row=0, column=2)
        
        # Ventana de tiempo
        ttk.Label(main_frame, text="Ventana de tiempo (min):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.ventana_var = tk.StringVar(value="2")  # Valor por defecto
        self.ventana_spinbox = ttk.Spinbox(main_frame, from_=1, to=30, width=10, 
                                          textvariable=self.ventana_var, format="%d",
                                          command=self._update_info_text)
        self.ventana_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Verificar actividad del sistema
        self.check_activity_var = tk.BooleanVar(value=True)
        check_activity_checkbox = ttk.Checkbutton(main_frame, text="Verificar actividad del sistema", 
                                                variable=self.check_activity_var,
                                                command=self._update_info_text)
        check_activity_checkbox.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Información
        self.info_text = tk.StringVar()
        info_label = ttk.Label(main_frame, textvariable=self.info_text, wraplength=350, 
                              foreground="gray", justify=tk.CENTER)
        info_label.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Guardar", command=self._save).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", command=self._cancel).grid(row=0, column=1)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
    def _load_current_values(self):
        # Cargar hora de entrada
        entrada_str = self.config.get("auto_entrada_hora", "08:00")
        try:
            hour, minute = map(int, entrada_str.split(":"))
            self.entrada_hour.set(hour)
            self.entrada_minute.set(minute)
        except ValueError:
            self.entrada_hour.set(8)
            self.entrada_minute.set(0)
            
        # Cargar hora de salida
        salida_str = self.config.get("auto_salida_hora", "17:00")
        try:
            hour, minute = map(int, salida_str.split(":"))
            self.salida_hour.set(hour)
            self.salida_minute.set(minute)
        except ValueError:
            self.salida_hour.set(17)
            self.salida_minute.set(0)
        
        # Cargar ventana de tiempo
        ventana = self.config.get("auto_ventana_minutos", 2)
        self.ventana_var.set(str(ventana))
        
        # Cargar verificación de actividad
        check_activity = self.config.get("auto_check_activity", True)
        self.check_activity_var.set(check_activity)
        
        # Actualizar texto informativo
        self._update_info_text()
    
    def _update_info_text(self):
        ventana = int(self.ventana_var.get())
        check_activity = self.check_activity_var.get()
        
        activity_text = "✓ Verificación de actividad HABILITADA" if check_activity else "✗ Verificación de actividad DESHABILITADA"
        
        self.info_text.set(f"El fichaje automático se realizará en ventanas de tiempo:\n"
                           f"• Entrada: desde {ventana} min antes hasta la hora exacta\n"
                           f"• Salida: desde la hora exacta hasta {ventana} min después\n"
                           f"• {activity_text}\n"
                           f"{'Asegúrate de que el equipo esté activo en esos momentos.' if check_activity else 'El fichaje se realizará sin verificar si el equipo está activo.'}")
    
    def _save(self):
        try:
            # Validar horas
            entrada_hour = int(self.entrada_hour.get())
            entrada_minute = int(self.entrada_minute.get())
            salida_hour = int(self.salida_hour.get())
            salida_minute = int(self.salida_minute.get())
            
            if not (0 <= entrada_hour <= 23 and 0 <= entrada_minute <= 59 and
                   0 <= salida_hour <= 23 and 0 <= salida_minute <= 59):
                messagebox.showerror("Error", "Las horas deben estar entre 00:00 y 23:59")
                return
            
            # Validar ventana de tiempo
            try:
                ventana = int(self.ventana_var.get())
                if not (1 <= ventana <= 30):
                    messagebox.showerror("Error", "La ventana de tiempo debe estar entre 1 y 30 minutos")
                    return
            except ValueError:
                messagebox.showerror("Error", "La ventana de tiempo debe ser un número válido")
                return
            
            # Formatear horas
            entrada_str = f"{entrada_hour:02d}:{entrada_minute:02d}"
            salida_str = f"{salida_hour:02d}:{salida_minute:02d}"
            
            # Obtener verificación de actividad
            check_activity = self.check_activity_var.get()
            
            # Guardar en configuración
            self.config["auto_entrada_hora"] = entrada_str
            self.config["auto_salida_hora"] = salida_str
            self.config["auto_ventana_minutos"] = ventana
            self.config["auto_check_activity"] = check_activity
            save_config(self.config)
            
            activity_status = "habilitada" if check_activity else "deshabilitada"
            messagebox.showinfo("Éxito", f"Configuración guardada:\nEntrada: {entrada_str}\nSalida: {salida_str}\nVentana: {ventana} min\nVerificación de actividad: {activity_status}")
            self.root.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos")
    
    def _cancel(self):
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


def main():
    dialog = HoursDialog()
    dialog.run()


if __name__ == "__main__":
    main()
