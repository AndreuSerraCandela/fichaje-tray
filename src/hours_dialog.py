import tkinter as tk
from tkinter import ttk, messagebox
from .config import load_config, save_config


class HoursDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configurar Horas de Fichaje Automático")
        self.root.geometry("400x700")  # Aumentar altura para los nuevos elementos (viernes y extra entrada)
        self.root.resizable(False, False)
        
        # Centrar en pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"400x700+{x}+{y}")
        
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
        
        # Salida mediodía
        ttk.Label(main_frame, text="Salida mediodía:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.mediodia_salida_var = tk.StringVar()
        salida_medio_frame = ttk.Frame(main_frame)
        salida_medio_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.mediodia_salida_hour = ttk.Spinbox(salida_medio_frame, from_=0, to=23, width=5, 
                                      textvariable=self.mediodia_salida_var, format="%02.0f")
        self.mediodia_salida_hour.grid(row=0, column=0)
        ttk.Label(salida_medio_frame, text=":").grid(row=0, column=1, padx=2)
        self.mediodia_salida_minute = ttk.Spinbox(salida_medio_frame, from_=0, to=59, width=5, format="%02.0f")
        self.mediodia_salida_minute.grid(row=0, column=2)

        # Entrada mediodía
        ttk.Label(main_frame, text="Entrada mediodía:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.mediodia_entrada_var = tk.StringVar()
        entrada_medio_frame = ttk.Frame(main_frame)
        entrada_medio_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.mediodia_entrada_hour = ttk.Spinbox(entrada_medio_frame, from_=0, to=23, width=5, 
                                       textvariable=self.mediodia_entrada_var, format="%02.0f")
        self.mediodia_entrada_hour.grid(row=0, column=0)
        ttk.Label(entrada_medio_frame, text=":").grid(row=0, column=1, padx=2)
        self.mediodia_entrada_minute = ttk.Spinbox(entrada_medio_frame, from_=0, to=59, width=5, format="%02.0f")
        self.mediodia_entrada_minute.grid(row=0, column=2)
        
        # Turno continuo
        self.turno_continuo_var = tk.BooleanVar(value=False)
        turno_check = ttk.Checkbutton(
            main_frame,
            text="Turno continuo (ignorar mediodía)",
            variable=self.turno_continuo_var,
            command=self._on_turno_continuo_toggle,
        )
        turno_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Solo mediodía
        self.solo_mediodia_var = tk.BooleanVar(value=False)
        solo_medio_check = ttk.Checkbutton(
            main_frame,
            text="Solo fichaje automático al mediodía",
            variable=self.solo_mediodia_var,
            command=self._on_solo_mediodia_toggle,
        )
        solo_medio_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Viernes - horario especial
        self.viernes_enabled_var = tk.BooleanVar(value=True)
        viernes_check = ttk.Checkbutton(
            main_frame,
            text="Activar horario especial viernes",
            variable=self.viernes_enabled_var,
            command=self._on_viernes_toggle,
        )
        viernes_check.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        ttk.Label(main_frame, text="Entrada (viernes):").grid(row=8, column=0, sticky=tk.W, pady=5)
        viernes_entrada_frame = ttk.Frame(main_frame)
        viernes_entrada_frame.grid(row=8, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.viernes_entrada_hour = ttk.Spinbox(viernes_entrada_frame, from_=0, to=23, width=5, format="%02.0f")
        self.viernes_entrada_hour.grid(row=0, column=0)
        ttk.Label(viernes_entrada_frame, text=":").grid(row=0, column=1, padx=2)
        self.viernes_entrada_minute = ttk.Spinbox(viernes_entrada_frame, from_=0, to=59, width=5, format="%02.0f")
        self.viernes_entrada_minute.grid(row=0, column=2)

        ttk.Label(main_frame, text="Salida (viernes):").grid(row=9, column=0, sticky=tk.W, pady=5)
        viernes_salida_frame = ttk.Frame(main_frame)
        viernes_salida_frame.grid(row=9, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.viernes_salida_hour = ttk.Spinbox(viernes_salida_frame, from_=0, to=23, width=5, format="%02.0f")
        self.viernes_salida_hour.grid(row=0, column=0)
        ttk.Label(viernes_salida_frame, text=":").grid(row=0, column=1, padx=2)
        self.viernes_salida_minute = ttk.Spinbox(viernes_salida_frame, from_=0, to=59, width=5, format="%02.0f")
        self.viernes_salida_minute.grid(row=0, column=2)

        self.viernes_turno_continuo_var = tk.BooleanVar(value=True)
        self.viernes_turno_check = ttk.Checkbutton(
            main_frame,
            text="Viernes turno continuo (ignorar mediodía)",
            variable=self.viernes_turno_continuo_var,
            command=self._update_info_text,
        )
        self.viernes_turno_check.grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Ventana de tiempo
        ttk.Label(main_frame, text="Ventana de tiempo (min):").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.ventana_var = tk.StringVar(value="2")  # Valor por defecto
        self.ventana_spinbox = ttk.Spinbox(main_frame, from_=1, to=30, width=10, 
                                          textvariable=self.ventana_var, format="%d",
                                          command=self._update_info_text)
        self.ventana_spinbox.grid(row=11, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Extra ventana de entrada
        ttk.Label(main_frame, text="Extra ventana entrada (min):").grid(row=12, column=0, sticky=tk.W, pady=5)
        self.ventana_entrada_extra_var = tk.StringVar(value="0")
        self.ventana_entrada_extra_spinbox = ttk.Spinbox(main_frame, from_=0, to=60, width=10,
                                                         textvariable=self.ventana_entrada_extra_var, format="%d",
                                                         command=self._update_info_text)
        self.ventana_entrada_extra_spinbox.grid(row=12, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Verificar actividad del sistema
        self.check_activity_var = tk.BooleanVar(value=True)
        check_activity_checkbox = ttk.Checkbutton(main_frame, text="Verificar actividad del sistema", 
                                                variable=self.check_activity_var,
                                                command=self._update_info_text)
        check_activity_checkbox.grid(row=13, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Información
        self.info_text = tk.StringVar()
        info_label = ttk.Label(main_frame, textvariable=self.info_text, wraplength=350, 
                              foreground="gray", justify=tk.CENTER)
        info_label.grid(row=14, column=0, columnspan=2, pady=20)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=15, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Guardar", command=self._save).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", command=self._cancel).grid(row=0, column=1)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
    def _load_current_values(self):
        # Cargar hora de entrada
        entrada_str = self.config.get("auto_entrada_hora", "08:30")
        try:
            hour, minute = map(int, entrada_str.split(":"))
            self.entrada_hour.set(hour)
            self.entrada_minute.set(minute)
        except ValueError:
            self.entrada_hour.set(8)
            self.entrada_minute.set(30)
            
        # Cargar hora de salida
        salida_str = self.config.get("auto_salida_hora", "16:30")
        try:
            hour, minute = map(int, salida_str.split(":"))
            self.salida_hour.set(hour)
            self.salida_minute.set(minute)
        except ValueError:
            self.salida_hour.set(16)
            self.salida_minute.set(30)
        
        # Cargar ventana de tiempo
        ventana = self.config.get("auto_ventana_minutos", 2)
        self.ventana_var.set(str(ventana))
        # Cargar extra ventana entrada
        ventana_extra = self.config.get("auto_ventana_minutos_entrada", 0)
        self.ventana_entrada_extra_var.set(str(ventana_extra))
        
        # Cargar mediodía salida
        medio_salida_str = self.config.get("auto_mediodia_salida", "14:00")
        try:
            hour, minute = map(int, medio_salida_str.split(":"))
            self.mediodia_salida_hour.set(hour)
            self.mediodia_salida_minute.set(minute)
        except ValueError:
            self.mediodia_salida_hour.set(14)
            self.mediodia_salida_minute.set(0)

        # Cargar mediodía entrada
        medio_entrada_str = self.config.get("auto_mediodia_entrada", "14:45")
        try:
            hour, minute = map(int, medio_entrada_str.split(":"))
            self.mediodia_entrada_hour.set(hour)
            self.mediodia_entrada_minute.set(minute)
        except ValueError:
            self.mediodia_entrada_hour.set(14)
            self.mediodia_entrada_minute.set(45)
        
        # Cargar verificación de actividad
        check_activity = self.config.get("auto_check_activity", True)
        self.check_activity_var.set(check_activity)
        
        # Cargar turno continuo
        turno_continuo = bool(self.config.get("auto_turno_continuo", False))
        self.turno_continuo_var.set(turno_continuo)
        # Cargar solo mediodía
        solo_mediodia = bool(self.config.get("auto_solo_mediodia", False))
        self.solo_mediodia_var.set(solo_mediodia)
        # Cargar viernes
        self.viernes_enabled_var.set(bool(self.config.get("auto_viernes_enabled", True)))
        v_ent = self.config.get("auto_viernes_entrada_hora", "08:30")
        v_sal = self.config.get("auto_viernes_salida_hora", "14:30")
        try:
            vh, vm = map(int, v_ent.split(":"))
            self.viernes_entrada_hour.set(vh)
            self.viernes_entrada_minute.set(vm)
        except Exception:
            self.viernes_entrada_hour.set(8)
            self.viernes_entrada_minute.set(30)
        try:
            sh, sm = map(int, v_sal.split(":"))
            self.viernes_salida_hour.set(sh)
            self.viernes_salida_minute.set(sm)
        except Exception:
            self.viernes_salida_hour.set(14)
            self.viernes_salida_minute.set(30)
        self.viernes_turno_continuo_var.set(bool(self.config.get("auto_viernes_turno_continuo", True)))
        # Forzar exclusividad: si ambos vienen activos, priorizar turno continuo
        if self.turno_continuo_var.get() and self.solo_mediodia_var.get():
            self.solo_mediodia_var.set(False)
        # Aplicar estados iniciales
        self._apply_state_toggles()
        
        # Actualizar texto informativo
        self._update_info_text()
    
    def _update_info_text(self):
        ventana = int(self.ventana_var.get())
        try:
            ventana_extra = int(self.ventana_entrada_extra_var.get())
        except Exception:
            ventana_extra = 0
        check_activity = self.check_activity_var.get()
        
        activity_text = "✓ Verificación de actividad HABILITADA" if check_activity else "✗ Verificación de actividad DESHABILITADA"
        
        if self.turno_continuo_var.get():
            medio_text = "(mediodía desactivado por turno continuo)"
            self.info_text.set(
                f"El fichaje automático se realizará en ventanas de tiempo:\n"
                f"• Entrada: desde {ventana} min antes hasta la hora exacta (+{ventana_extra} min)\n"
                f"• Salida: desde la hora exacta hasta {ventana} min después\n"
                f"• {medio_text}\n"
                f"• {activity_text}\n"
                f"{'Asegúrate de que el equipo esté activo para ENTRADAS.' if check_activity else 'El fichaje se realizará sin verificar actividad.'}"
            )
        elif self.solo_mediodia_var.get():
            self.info_text.set(
                f"El fichaje automático se realizará SOLO al mediodía:\n"
                f"• Salida mediodía: desde la hora exacta hasta {ventana} min después\n"
                f"• Entrada mediodía: desde {ventana} min antes hasta la hora exacta\n"
                f"• {activity_text}\n"
                f"{'Asegúrate de que el equipo esté activo para ENTRADAS.' if check_activity else 'El fichaje se realizará sin verificar actividad.'}"
            )
        else:
            self.info_text.set(
                f"El fichaje automático se realizará en ventanas de tiempo:\n"
                f"• Entrada: desde {ventana} min antes hasta la hora exacta\n"
                f"• Salida: desde la hora exacta hasta {ventana} min después\n"
                f"• Entrada mediodía: desde {ventana} min antes hasta la hora exacta\n"
                f"• Salida mediodía: desde la hora exacta hasta {ventana} min después\n"
                f"• {activity_text}\n"
                f"{'Asegúrate de que el equipo esté activo para ENTRADAS.' if check_activity else 'El fichaje se realizará sin verificar actividad.'}"
            )
        # Apéndice información viernes
        try:
            v_on = self.viernes_enabled_var.get()
            v_turno = self.viernes_turno_continuo_var.get()
            from datetime import time
            v_ent = f"{int(self.viernes_entrada_hour.get()):02d}:{int(self.viernes_entrada_minute.get()):02d}"
            v_sal = f"{int(self.viernes_salida_hour.get()):02d}:{int(self.viernes_salida_minute.get()):02d}"
            base = self.info_text.get()
            self.info_text.set(base + f"\n\nViernes: {'ON' if v_on else 'OFF'} ({v_ent}-{v_sal}{', turno continuo' if v_turno else ''})")
        except Exception:
            pass
    
    def _save(self):
        try:
            # Validar horas
            entrada_hour = int(self.entrada_hour.get())
            entrada_minute = int(self.entrada_minute.get())
            salida_hour = int(self.salida_hour.get())
            salida_minute = int(self.salida_minute.get())
            medio_salida_hour = int(self.mediodia_salida_hour.get())
            medio_salida_minute = int(self.mediodia_salida_minute.get())
            medio_entrada_hour = int(self.mediodia_entrada_hour.get())
            medio_entrada_minute = int(self.mediodia_entrada_minute.get())
            
            if not (0 <= entrada_hour <= 23 and 0 <= entrada_minute <= 59 and
                   0 <= salida_hour <= 23 and 0 <= salida_minute <= 59 and
                   0 <= medio_salida_hour <= 23 and 0 <= medio_salida_minute <= 59 and
                   0 <= medio_entrada_hour <= 23 and 0 <= medio_entrada_minute <= 59):
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
            # Validar ventana extra entrada
            try:
                ventana_extra = int(self.ventana_entrada_extra_var.get())
                if not (0 <= ventana_extra <= 60):
                    messagebox.showerror("Error", "El extra de entrada debe estar entre 0 y 60 minutos")
                    return
            except ValueError:
                messagebox.showerror("Error", "El extra de entrada debe ser un número válido")
                return
            
            # Formatear horas
            entrada_str = f"{entrada_hour:02d}:{entrada_minute:02d}"
            salida_str = f"{salida_hour:02d}:{salida_minute:02d}"
            medio_salida_str = f"{medio_salida_hour:02d}:{medio_salida_minute:02d}"
            medio_entrada_str = f"{medio_entrada_hour:02d}:{medio_entrada_minute:02d}"
            
            # Obtener verificación de actividad
            check_activity = self.check_activity_var.get()
            turno_continuo = self.turno_continuo_var.get()
            solo_mediodia = self.solo_mediodia_var.get()
            # Exclusividad por seguridad
            if turno_continuo and solo_mediodia:
                solo_mediodia = False
            
            # Guardar en configuración
            self.config["auto_entrada_hora"] = entrada_str
            self.config["auto_salida_hora"] = salida_str
            self.config["auto_mediodia_salida"] = medio_salida_str
            self.config["auto_mediodia_entrada"] = medio_entrada_str
            self.config["auto_ventana_minutos"] = ventana
            self.config["auto_ventana_minutos_entrada"] = ventana_extra
            self.config["auto_check_activity"] = check_activity
            self.config["auto_turno_continuo"] = turno_continuo
            self.config["auto_solo_mediodia"] = solo_mediodia
            # Guardar viernes
            self.config["auto_viernes_enabled"] = bool(self.viernes_enabled_var.get())
            v_ent_str = f"{int(self.viernes_entrada_hour.get()):02d}:{int(self.viernes_entrada_minute.get()):02d}"
            v_sal_str = f"{int(self.viernes_salida_hour.get()):02d}:{int(self.viernes_salida_minute.get()):02d}"
            self.config["auto_viernes_entrada_hora"] = v_ent_str
            self.config["auto_viernes_salida_hora"] = v_sal_str
            self.config["auto_viernes_turno_continuo"] = bool(self.viernes_turno_continuo_var.get())
            # Eliminar clave mal escrita si existe
            try:
                self.config.pop("autp_mediodia_salida", None)
            except Exception:
                pass
            save_config(self.config)
            
            activity_status = "habilitada" if check_activity else "deshabilitada"
            turno_text = "Sí" if turno_continuo else "No"
            solo_text = "Sí" if solo_mediodia else "No"
            messagebox.showinfo("Éxito", f"Configuración guardada:\n"
                                         f"Entrada: {entrada_str}\n"
                                         f"Salida: {salida_str}\n"
                                         f"Salida mediodía: {medio_salida_str}\n"
                                         f"Entrada mediodía: {medio_entrada_str}\n"
                                         f"Ventana: {ventana} min\n"
                                         f"Extra entrada: {ventana_extra} min\n"
                                         f"Verificación de actividad: {activity_status}\n"
                                         f"Turno continuo: {turno_text}\n"
                                         f"Solo mediodía: {solo_text}\n"
                                         f"Viernes: {'ON' if self.config['auto_viernes_enabled'] else 'OFF'} ({self.config['auto_viernes_entrada_hora']}-{self.config['auto_viernes_salida_hora']}{', turno continuo' if self.config['auto_viernes_turno_continuo'] else ''})")
            self.root.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos")
    
    def _cancel(self):
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

    def _on_turno_continuo_toggle(self) -> None:
        estado = "disabled" if self.turno_continuo_var.get() else "normal"
        try:
            self.mediodia_salida_hour.configure(state=estado)
            self.mediodia_salida_minute.configure(state=estado)
            self.mediodia_entrada_hour.configure(state=estado)
            self.mediodia_entrada_minute.configure(state=estado)
        except Exception:
            pass
        if self.turno_continuo_var.get():
            # Forzar exclusividad
            self.solo_mediodia_var.set(False)
        self._update_info_text()

    def _on_solo_mediodia_toggle(self) -> None:
        if self.solo_mediodia_var.get():
            # Forzar exclusividad
            self.turno_continuo_var.set(False)
        # Opcional: deshabilitar entrada/salida jornada si solo mediodía
        estado = "disabled" if self.solo_mediodia_var.get() else "normal"
        try:
            self.entrada_hour.configure(state=estado)
            self.entrada_minute.configure(state=estado)
            self.salida_hour.configure(state=estado)
            self.salida_minute.configure(state=estado)
        except Exception:
            pass
        self._update_info_text()

    def _on_viernes_toggle(self) -> None:
        estado = "normal" if self.viernes_enabled_var.get() else "disabled"
        try:
            self.viernes_entrada_hour.configure(state=estado)
            self.viernes_entrada_minute.configure(state=estado)
            self.viernes_salida_hour.configure(state=estado)
            self.viernes_salida_minute.configure(state=estado)
            self.viernes_turno_check.configure(state=estado)
        except Exception:
            pass
        self._update_info_text()

    def _apply_state_toggles(self) -> None:
        # Aplicar estados iniciales coherentes
        if self.turno_continuo_var.get():
            self._on_turno_continuo_toggle()
        if self.solo_mediodia_var.get():
            self._on_solo_mediodia_toggle()


def main():
    dialog = HoursDialog()
    dialog.run()


if __name__ == "__main__":
    main()
