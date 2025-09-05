import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.tray_app import TrayApp
from src.config_dialog import ConfigDialog
from src.hours_dialog import HoursDialog


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config-dialog":
            dialog = ConfigDialog()
            dialog.run()
        elif sys.argv[1] == "--hours-dialog":
            dialog = HoursDialog()
            dialog.run()
        else:
            print(f"Argumento desconocido: {sys.argv[1]}")
            print("Uso: python -m src.main [--config-dialog|--hours-dialog]")
    else:
        app = TrayApp()
        app.run()


if __name__ == "__main__":
    main()


