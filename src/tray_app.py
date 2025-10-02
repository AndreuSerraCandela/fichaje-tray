import threading
from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw
from apscheduler.schedulers.background import BackgroundScheduler

from .config import load_config, save_config, APP_NAME
from .api_client import ApiClient, ApiError
from .fichaje_logic import flujo_manual, flujo_automatico, flujo_forzado
from .notify import Notifier
from .system_activity import is_system_active
from .version import __version__ as APP_VERSION


def create_image(width: int = 64, height: int = 64, color=(0, 122, 204)) -> Image.Image:
    # Intentar localizar un .ico en distintos contextos (dev, frozen, dist)
    from pathlib import Path
    import sys

    def find_icon_file() -> Optional[Path]:
        candidates: list[Path] = []
        here = Path(__file__).resolve()
        project_assets = here.parent.parent / "assets"
        cwd_assets = Path("assets")
        candidates += [project_assets / "icon.ico", project_assets / "Icon.ico"]
        candidates += [cwd_assets / "icon.ico", cwd_assets / "Icon.ico"]

        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).parent
            candidates += [exe_dir / "assets" / "icon.ico", exe_dir / "assets" / "Icon.ico"]
            meipass = Path(getattr(sys, "_MEIPASS", exe_dir))
            candidates += [meipass / "assets" / "icon.ico", meipass / "assets" / "Icon.ico"]

        # Añadir cualquier .ico encontrado en assets conocidos
        for base in {project_assets, cwd_assets}:
            if base.exists():
                candidates.extend(base.glob("*.ico"))

        for path in candidates:
            try:
                if path.exists():
                    return path
            except Exception:
                continue
        return None

    icon_path = find_icon_file()
    if icon_path is not None:
        try:
            im = Image.open(icon_path)
            # ICO puede contener múltiples tamaños; seleccionamos y normalizamos a 64x64 RGBA
            target_size = (64, 64)
            sizes = im.info.get("sizes") or []
            if sizes:
                # elegir el más grande disponible
                best = max(sizes, key=lambda s: s[0] * s[1])
                im = im.copy()
                im = im.resize(target_size, Image.LANCZOS).convert("RGBA")
            else:
                im = im.convert("RGBA").resize(target_size, Image.LANCZOS)
            return im
        except Exception:
            pass
    image = Image.new("RGB", (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle([(0, 0), (width, height)], fill=(255, 255, 255))
    dc.ellipse([(8, 8), (width - 8, height - 8)], fill=color)
    return image


class TrayApp:
    def __init__(self) -> None:
        self.config = load_config()
        self.notifier = Notifier(APP_NAME)
        self.icon: Optional[pystray.Icon] = None
        self.scheduler = BackgroundScheduler(daemon=True)
        self.api = ApiClient(self.config.get("base_url", ""))
        self._update_check_running = False

    # ----- Actions -----
    def _notify(self, msg: str) -> None:
        if self.config.get("notify_enabled", True):
            self.notifier.show(APP_NAME, msg)
        try:
            if self.icon:
                # Notificación adicional por el propio icono de bandeja
                self.icon.notify(msg)
        except Exception:
            pass

    def _with_employee(self) -> Optional[str]:
        code = (self.config.get("employee_code") or "").strip()
        if not code:
            self._notify("Configure el código de empleado desde el menú")
            return None
        return code

    def action_fichar(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        code = self._with_employee()
        if not code:
            return
        try:
            data = flujo_manual(self.api, code)
            message = data.get("message") or "Fichaje realizado"
            self._notify(f"Entrada: {message}")
        except (ApiError, ValueError) as exc:
            self._notify(str(exc))
        except Exception as exc:
            self._notify(f"Error inesperado: {exc}")

    # def action_fichar_salida(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
    #     code = self._with_employee()
    #     if not code:
    #         return
    #     try:
    #         data = flujo_manual(self.api, code, "SALIDA")
    #         message = data.get("message") or "Fichaje realizado"
    #         self._notify(f"Salida: {message}")
    #     except (ApiError, ValueError) as exc:
    #         self._notify(str(exc))
    #     except Exception as exc:
    #         self._notify(f"Error inesperado: {exc}")

    def action_fichar_forzado_entrada(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        code = self._with_employee()
        if not code:
            return
        try:
            data = flujo_forzado(self.api, code, "ENTRADA")
            message = data.get("message") or "Fichaje forzado realizado"
            self._notify(f"Entrada (forzado): {message}")
        except ApiError as exc:
            self._notify(str(exc))
        except Exception as exc:
            self._notify(f"Error inesperado: {exc}")

    def action_fichar_forzado_salida(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        code = self._with_employee()
        if not code:
            return
        try:
            data = flujo_forzado(self.api, code, "SALIDA")
            message = data.get("message") or "Fichaje forzado realizado"
            self._notify(f"Salida (forzado): {message}")
        except ApiError as exc:
            self._notify(str(exc))
        except Exception as exc:
            self._notify(f"Error inesperado: {exc}")

    def action_toggle_auto(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        enabled = not bool(self.config.get("auto_enabled", False))
        self.config["auto_enabled"] = enabled
        save_config(self.config)
        if enabled:
            self._start_scheduler()
            self._notify("Modo automático activado")
        else:
            self._stop_scheduler()
            self._notify("Modo automático desactivado")

    def action_set_employee(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        # Abrir diálogo de configuración sin crear un segundo icono en bandeja
        import subprocess
        import sys
        try:
            if getattr(sys, "frozen", False):
                # Ejecutable empaquetado: invocar a sí mismo con bandera
                subprocess.run([sys.executable, "--config-dialog"], check=False)
            else:
                # Entorno desarrollo: usar módulo
                subprocess.run([sys.executable, "-m", "src.main", "--config-dialog"], check=False)
            # Recargar config tras cerrar el diálogo
            self.config = load_config()
            if self.config.get("employee_code"):
                self._notify(f"Código de empleado guardado: {self.config['employee_code']}")
            else:
                self._notify("Código no cambiado")
        except Exception as exc:
            self._notify(f"No se pudo abrir el diálogo: {exc}")

    def action_toggle_turno_continuo(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        enabled = not bool(self.config.get("auto_turno_continuo", False))
        self.config["auto_turno_continuo"] = enabled
        if enabled:
            # Exclusividad: apaga solo_mediodia
            self.config["auto_solo_mediodia"] = False
        save_config(self.config)
        if enabled:
            self._notify("Turno continuo activado (mediodía ignorado)")
        else:
            self._notify("Turno continuo desactivado")

    def action_toggle_solo_mediodia(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        enabled = not bool(self.config.get("auto_solo_mediodia", False))
        self.config["auto_solo_mediodia"] = enabled
        if enabled:
            # Exclusividad: apaga turno continuo
            self.config["auto_turno_continuo"] = False
        save_config(self.config)
        if enabled:
            self._notify("Modo solo mediodía activado")
        else:
            self._notify("Modo solo mediodía desactivado")

    def action_set_hours(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        # Abrir diálogo de configuración de horas
        import subprocess
        import sys
        try:
            if getattr(sys, "frozen", False):
                # Ejecutable empaquetado: invocar a sí mismo con bandera
                subprocess.run([sys.executable, "--hours-dialog"], check=False)
            else:
                # Entorno desarrollo: usar módulo
                subprocess.run([sys.executable, "-m", "src.main", "--hours-dialog"], check=False)
            # Recargar config tras cerrar el diálogo
            self.config = load_config()
            entrada = self.config.get("auto_entrada_hora", "08:30")
            salida = self.config.get("auto_salida_hora", "16:30")
            medio_salida = self.config.get("auto_mediodia_salida", "14:00")
            medio_entrada = self.config.get("auto_mediodia_entrada", "14:45")
            turno_continuo = bool(self.config.get("auto_turno_continuo", False))
            solo_mediodia = bool(self.config.get("auto_solo_mediodia", False))
            # Datos de viernes
            viernes_enabled = bool(self.config.get("auto_viernes_enabled", True))
            v_entrada = self.config.get("auto_viernes_entrada_hora", "08:30")
            v_salida = self.config.get("auto_viernes_salida_hora", "14:30")
            v_turno = bool(self.config.get("auto_viernes_turno_continuo", True))
            if turno_continuo:
                self._notify(
                    (
                        f"Horas configuradas: Entrada {entrada}, Salida {salida} | Turno continuo ACTIVADO (mediodía ignorado)"
                        + (f" | Viernes: {'ON' if viernes_enabled else 'OFF'} ({v_entrada}-{v_salida}{', turno continuo' if v_turno else ''})" )
                    )
                )
            elif solo_mediodia:
                self._notify(
                    (
                        f"Horas configuradas: Solo mediodía ACTIVADO | Mediodía: salida {medio_salida}, entrada {medio_entrada}"
                        + (f" | Viernes: {'ON' if viernes_enabled else 'OFF'} ({v_entrada}-{v_salida}{', turno continuo' if v_turno else ''})" )
                    )
                )
            else:
                self._notify(
                    (
                        f"Horas configuradas: Entrada {entrada}, Salida {salida} | Mediodía: salida {medio_salida}, entrada {medio_entrada}"
                        + (f" | Viernes: {'ON' if viernes_enabled else 'OFF'} ({v_entrada}-{v_salida}{', turno continuo' if v_turno else ''})" )
                    )
                )
        except Exception as exc:
            self._notify(f"No se pudo abrir el diálogo: {exc}")

    def action_salir(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:  # noqa: ARG002
        self._stop_scheduler()
        if self.icon:
            self.icon.stop()

    # ----- Update check -----
    def _parse_version(self, s: str) -> tuple:
        try:
            parts = [int(p) for p in s.strip().split('.')]
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts[:3])
        except Exception:
            return (0, 0, 0)

    def _check_and_run_installer(self) -> None:
        if self._update_check_running:
            return
        self._update_check_running = True
        try:
            import os, glob
            import subprocess

            # Normalizar UNC: debe comenzar por \\\\ y usar backslashes
            raw = str(self.config.get("update_shared_dir") or r"\\\\192.168.10.212\\escaner GREPSA\\FichajeTray\\Output").strip()
            unc = "\\\\" + raw.lstrip("\\/").replace("/", "\\")  # fuerza prefijo UNC
            if not os.path.isdir(unc):
                self._notify(f"Ruta de actualización no accesible: {unc}")
                return

            pattern = self.config.get("update_installer_pattern") or "FichajeTray_Setup*.exe"
            installers =  sorted(glob.glob(os.path.join(unc, pattern)))
            if not installers:
                self._notify(f"No se encontró ningún instalador en {unc}")
                return

            latest = max(installers, key=os.path.getmtime)
            # extraer versión del nombre si es posible
            latest_name = os.path.basename(latest)
            latest_ver = (0, 0, 0)
            import re
            m = re.search(r"(\d+)\.(\d+)\.(\d+)", latest_name)
            if m:
                latest_ver = (int(m.group(1)), int(m.group(2)), int(m.group(3)))

            current_ver = self._parse_version(APP_VERSION)
            force_by_mtime = bool(self.config.get("update_force_by_mtime", True))
            
            # EVITAR BUCLE: Si la versión es la misma, no actualizar
            if latest_ver <= current_ver:
                self._notify(f"La versión {latest_ver} es la misma o más antigua que la actual {current_ver}")
                return
               

            # Evitar relanzar el mismo instalador en bucle
            try:
                last_mtime = float(self.config.get("last_installer_mtime", 0))
            except Exception:
                last_mtime = 0.0
            last_name = self.config.get("last_installer_name") or ""
            mt = os.path.getmtime(latest)
            if last_name == latest_name and abs(mt - last_mtime) < 1:
                self._notify(f"El instalador {latest_name} ya se ha ejecutado recientemente")
                return

            # Ejecutar instalador silencioso si permitido
            silent = False
            args = [str(latest)]
            if silent:
                # switches comunes para Inno Setup
                args.append("/VERYSILENT")
                args.append("/NORESTART")

            # Notificar y ejecutar
            self._notify(f"Actualización disponible {latest_ver}, iniciando instalador...")
            try:
                subprocess.Popen(args, shell=False)
                # Guardar marca para no relanzar
                self.config["last_installer_mtime"] = mt
                self.config["last_installer_name"] = latest_name
                save_config(self.config)
            except Exception as e:
                self._notify(f"No se pudo lanzar el instalador: {e}")
        finally:
            self._update_check_running = False
    # ----- Scheduler -----
    def _auto_job(self) -> None:
        code = self._with_employee()
        if not code:
            return
        
        # Comprobar si estamos en una ventana de tiempo válida para fichaje automático
        from datetime import datetime, time, timedelta
        now = datetime.now()
        current_time = now.time()
        
        # Obtener horas configuradas
        entrada_str = self.config.get("auto_entrada_hora", "08:30")
        salida_str = self.config.get("auto_salida_hora", "16:30")
        medio_salida_str = self.config.get("auto_mediodia_salida", "14:00")
        medio_entrada_str = self.config.get("auto_mediodia_entrada", "14:45")
        turno_continuo = bool(self.config.get("auto_turno_continuo", False))
        solo_mediodia = bool(self.config.get("auto_solo_mediodia", False))
        # Reglas especiales de viernes (por defecto activadas)
        try:
            is_friday = now.weekday() == 4  # 0=lunes .. 4=viernes
        except Exception:
            is_friday = False
        if is_friday and bool(self.config.get("auto_viernes_enabled", True)):
            # Si hay horario especial de viernes, aplicar
            entrada_str = self.config.get("auto_viernes_entrada_hora", entrada_str)
            salida_str = self.config.get("auto_viernes_salida_hora", salida_str)
            # Permitir marcar viernes como turno continuo aunque globalmente no lo sea
            if bool(self.config.get("auto_viernes_turno_continuo", True)):
                turno_continuo = True
        
        try:
            entrada_time = datetime.strptime(entrada_str, "%H:%M").time()
        except ValueError:
            entrada_time = time(8, 30)
        try:
            salida_time = datetime.strptime(salida_str, "%H:%M").time()
        except ValueError:
            salida_time = time(16, 30)
        try:
            medio_salida_time = datetime.strptime(medio_salida_str, "%H:%M").time()
        except ValueError:
            medio_salida_time = time(14, 0)
        try:
            medio_entrada_time = datetime.strptime(medio_entrada_str, "%H:%M").time()
        except ValueError:
            medio_entrada_time = time(14, 45)
        
        # Definir ventanas de tiempo (configurable)
        ventana_minutos = int(self.config.get("auto_ventana_minutos", 2) or 2)
        ventana_minutos_entrada_extra = int(self.config.get("auto_ventana_minutos_entrada", 0) or 0)
        
        # Crear objetos datetime para poder hacer cálculos
        entrada_dt = datetime.combine(now.date(), entrada_time)
        salida_dt = datetime.combine(now.date(), salida_time)
        medio_salida_dt = datetime.combine(now.date(), medio_salida_time)
        medio_entrada_dt = datetime.combine(now.date(), medio_entrada_time)
        
        # Ventana de entrada: desde X minutos antes hasta la hora exacta (+extra configurable)
        ventana_entrada_inicio = entrada_dt - timedelta(minutes=ventana_minutos)
        ventana_entrada_fin = entrada_dt + timedelta(minutes=ventana_minutos_entrada_extra)
        # Ventana de salida: desde la hora exacta hasta X minutos después
        ventana_salida_inicio = salida_dt
        ventana_salida_fin = salida_dt + timedelta(minutes=ventana_minutos)
        # Ventana de salida mediodía: desde la hora exacta hasta X minutos después
        ventana_medio_salida_inicio = medio_salida_dt
        ventana_medio_salida_fin = medio_salida_dt + timedelta(minutes=ventana_minutos)
        # Ventana de entrada mediodía: desde X minutos antes hasta la hora exacta
        ventana_medio_entrada_inicio = medio_entrada_dt - timedelta(minutes=ventana_minutos)
        ventana_medio_entrada_fin = medio_entrada_dt+ timedelta(minutes=ventana_minutos_entrada_extra)
        
        # Comprobar si estamos en alguna ventana válida
        en_ventana_entrada = ventana_entrada_inicio.time() <= current_time <= ventana_entrada_fin.time()
        en_ventana_salida = ventana_salida_inicio.time() <= current_time <= ventana_salida_fin.time()
        en_ventana_medio_entrada = ventana_medio_entrada_inicio.time() <= current_time <= ventana_medio_entrada_fin.time()
        en_ventana_medio_salida = ventana_medio_salida_inicio.time() <= current_time <= ventana_medio_salida_fin.time()

        if turno_continuo:
            en_ventana_entrada_total = en_ventana_entrada
            en_ventana_salida_total = en_ventana_salida
        elif solo_mediodia:
            en_ventana_entrada_total = en_ventana_medio_entrada
            en_ventana_salida_total = en_ventana_medio_salida
        else:
            en_ventana_entrada_total = en_ventana_entrada or en_ventana_medio_entrada
            en_ventana_salida_total = en_ventana_salida or en_ventana_medio_salida
        
        if not (en_ventana_entrada_total or en_ventana_salida_total):
            # No estamos en ninguna ventana de fichaje automático
            return
        
        # Comprobar actividad del sistema (Windows)
        idle_threshold = 1200#int(self.config.get("auto_active_idle_seconds", 1200) or 1200)
        check_activity = bool(self.config.get("auto_check_activity", True))
        if check_activity:
            try:
                if (not is_system_active(idle_threshold)) and (en_ventana_entrada_total):
                    self._notify("Equipo inactivo: no se intenta fichaje automático")
                    return
            except Exception:
                # Si falla la detección, continuamos para no bloquear el fichaje por error ajeno
                pass
        
        try:
            # Usar flujo automático (que ya tiene su propia lógica de validación)
            if en_ventana_entrada_total:
                res = flujo_automatico(self.api, code, "ENTRADA")
            else:
                res = flujo_automatico(self.api, code, "SALIDA")
            if res and isinstance(res, dict):
                message = res.get("message") or "Fichaje automático realizado"
                self._notify(message)
            else:
                self._notify("No se cumplen condiciones para fichaje automático ahora")
        except ApiError as exc:
            self._notify(str(exc))
        except Exception as exc:
            self._notify(f"Error inesperado: {exc}")

    def _start_scheduler(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
        self.scheduler.remove_all_jobs()
        interval = int(self.config.get("interval_minutes", 1) or 1)
        self.scheduler.add_job(self._auto_job, "interval", minutes=interval, id="auto_fichaje", replace_existing=True)

    def _stop_scheduler(self) -> None:
        if self.scheduler.running:
            self.scheduler.remove_all_jobs()

    # ----- Run -----
    def run(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("Fichar", self.action_fichar),
            pystray.MenuItem(
                "Salida Temporal/reincorporación",
                pystray.Menu(
                    pystray.MenuItem("Entrada", self.action_fichar_forzado_entrada),
                    pystray.MenuItem("Salida", self.action_fichar_forzado_salida),
                )
            ),
            pystray.MenuItem(
                lambda item: "Desactivar automático" if self.config.get("auto_enabled") else "Activar automático",
                self.action_toggle_auto,
            ),
            pystray.MenuItem(
                lambda item: "Desactivar turno continuo" if self.config.get("auto_turno_continuo") else "Activar turno continuo",
                self.action_toggle_turno_continuo,
            ),
            pystray.MenuItem(
                lambda item: "Desactivar solo mediodía" if self.config.get("auto_solo_mediodia") else "Activar solo mediodía",
                self.action_toggle_solo_mediodia,
            ),
            pystray.MenuItem("Buscar actualización", lambda i, it: threading.Thread(target=self._check_and_run_installer, daemon=True).start()),
            pystray.MenuItem(
                "Configuración",
                pystray.Menu(
                    pystray.MenuItem("Configurar código empleado", self.action_set_employee),
                    pystray.MenuItem("Configurar horas de fichaje", self.action_set_hours),
                )
            ),
            pystray.MenuItem("Salir", self.action_salir),
        )

        image = create_image()
        self.icon = pystray.Icon("fichaje_tray", image, APP_NAME, menu)

        if self.config.get("auto_enabled", False):
            self._start_scheduler()
        # Comprobar actualización al iniciar (en hilo)
        threading.Thread(target=self._check_and_run_installer, daemon=True).start()

        self.icon.run()


