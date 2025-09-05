import requests
from typing import Any, Dict, Optional, Tuple


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url: str, timeout_sec: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    def get_proximo_fichaje(self, employee_code: str) -> Dict[str, Any]:
        url = f"{self.base_url}/proximo-fichaje/{employee_code}"
        try:
            resp = requests.get(url, timeout=self.timeout_sec)
        except Exception as exc:
            raise ApiError(f"Error de red al consultar próximo fichaje: {exc}") from exc
        if resp.status_code >= 400:
            raise ApiError(f"Error HTTP {resp.status_code} al consultar próximo fichaje: {resp.text}")
        try:
            return resp.json()
        except Exception:
            raise ApiError(f"Respuesta no es JSON válido: {resp.text[:200]}")

    def post_fichaje(self, employee_code: str, tipo_fichaje: str) -> Dict[str, Any]:
        url = f"{self.base_url}/fichajes"
        payload = {
            "codigo_empleado": employee_code,
            "tipo_fichaje": tipo_fichaje,
        }
        try:
            resp = requests.post(url, json=payload, params={"codigo_empleado": employee_code}, timeout=self.timeout_sec)
        except Exception as exc:
            raise ApiError(f"Error de red al registrar fichaje: {exc}") from exc
        if resp.status_code >= 400:
            raise ApiError(f"Error HTTP {resp.status_code} al registrar fichaje: {resp.text}")
        try:
            return resp.json()
        except Exception:
            raise ApiError(f"Respuesta no es JSON válido: {resp.text[:200]}")


