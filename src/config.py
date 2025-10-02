import json
import os
from pathlib import Path
from typing import Any, Dict

APP_NAME = "FichajeTray"
CONFIG_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "employee_code": "",
    "auto_enabled": False,
    "interval_minutes": 1,
    "base_url": "http://192.168.10.226:8002/api",
    "notify_enabled": True,
    "auto_active_idle_seconds": 1200,
    "auto_entrada_hora": "08:30",
    "auto_salida_hora": "16:30",
    "auto_mediodia_entrada": "14:45",
    "auto_mediodia_salida": "14:00",
    "auto_turno_continuo": False,
    "auto_solo_mediodia": False,
    "auto_ventana_minutos": 2,
    "auto_ventana_minutos_entrada": 0,
    "auto_viernes_enabled": True,
    "auto_viernes_entrada_hora": "08:30",
    "auto_viernes_salida_hora": "14:30",
    "auto_viernes_turno_continuo": True,
    "update_shared_dir": r"\\\\192.168.10.212\escaner GREPSA\FichajeTray\Output",
    "update_installer_pattern": "FichajeTray_Setup*.exe",
    "update_silent": True,
    "update_force_by_mtime": True,
    "last_installer_mtime": 0,
    "last_installer_name": "",
}

def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # Migración de claves antiguas mal escritas
            try:
                if "autp_mediodia_salida" in data and "auto_mediodia_salida" not in data:
                    data["auto_mediodia_salida"] = data.pop("autp_mediodia_salida")
            except Exception:
                pass
            return {**DEFAULT_CONFIG, **data}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    ensure_config_dir()
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
