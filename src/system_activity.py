from __future__ import annotations

import ctypes
from ctypes import byref
from ctypes.wintypes import DWORD


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", DWORD),
    ]


def _get_tick_count_ms() -> int:
    # Preferir GetTickCount64 si está disponible
    try:
        get_tick_count64 = ctypes.windll.kernel32.GetTickCount64
        get_tick_count64.restype = ctypes.c_ulonglong
        return int(get_tick_count64())
    except Exception:
        get_tick_count = ctypes.windll.kernel32.GetTickCount
        get_tick_count.restype = DWORD
        return int(get_tick_count())


def get_idle_seconds() -> int:
    """Devuelve segundos desde la última interacción de usuario (teclado/ratón)."""
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not ctypes.windll.user32.GetLastInputInfo(byref(li)):
        return 0
    now_ms = _get_tick_count_ms()
    last_input_ms = int(li.dwTime)
    idle_ms = max(0, now_ms - last_input_ms)
    return idle_ms // 1000


def is_system_active(threshold_seconds: int) -> bool:
    """True si el equipo está activo (idle por debajo del umbral)."""
    return get_idle_seconds() < max(0, int(threshold_seconds))


