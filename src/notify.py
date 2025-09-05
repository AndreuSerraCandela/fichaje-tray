from typing import Optional

try:
    from win10toast import ToastNotifier
except Exception:  # pragma: no cover - entorno no Windows
    ToastNotifier = None  # type: ignore


class Notifier:
    def __init__(self, app_name: str = "FichajeTray") -> None:
        self.app_name = app_name
        self._toaster = ToastNotifier() if ToastNotifier else None

    def show(self, title: str, msg: str, duration: int = 5) -> None:
        if self._toaster:
            try:
                self._toaster.show_toast(title, msg, duration=duration, threaded=True)
            except Exception:
                pass


