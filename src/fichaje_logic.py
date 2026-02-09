from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Literal, Optional, Tuple

from .api_client import ApiClient, ApiError


TipoFichaje = Literal["ENTRADA", "SALIDA"]


@dataclass
class ProximoFichajeInfo:
    proximo_fichaje: TipoFichaje
    hora_proximo_fichaje: str  # formato "HH:mm" según backend
    es_festivo: bool
    en_vacaciones: bool
    tiene_incidencia: bool


def parse_proximo_fichaje(data: Dict[str, Any]) -> ProximoFichajeInfo:
    return ProximoFichajeInfo(
        proximo_fichaje=(data.get("proximo_fichaje") or "").upper() or "ENTRADA",
        hora_proximo_fichaje=data.get("hora_proximo_fichaje") or "00:00",
        es_festivo=bool(data.get("es_festivo")),
        en_vacaciones=bool(data.get("en_vacaciones")),
        tiene_incidencia=bool(data.get("tiene_incidencia")),
    )


def minutos_diferencia_ahora(hora_hhmm: str) -> int:
    # diferencia = ahora - hora_objetivo en minutos (puede ser negativa)
    ahora = datetime.now()
    try:
        h, m ,s = map(int, hora_hhmm.split(":"))
    except Exception:
        h, m ,s= 0, 0 ,0
    objetivo = ahora.replace(hour=h, minute=m, second=0, microsecond=0)
    delta = ahora - objetivo
    return int(delta.total_seconds() // 60)


def validar_manual(info: ProximoFichajeInfo) -> str:
    if info.es_festivo:
        raise ValueError("Es festivo")
    if info.en_vacaciones:
        raise ValueError("Tiene vacaciones")
    if info.tiene_incidencia:
        raise ValueError("Tiene incidencia")

    # if info.proximo_fichaje.lower() != tipo_solicitado.lower():
    #     raise ValueError(
    #         f"No puede fichar {tipo_solicitado.lower()}, el próximo fichaje es de {info.proximo_fichaje.lower()}"
    #     )

    dif = abs(minutos_diferencia_ahora(info.hora_proximo_fichaje))
    if dif > 15:
        raise ValueError(
            f"No puede fichar. La diferencia con la hora del próximo fichaje ({info.hora_proximo_fichaje}) es mayor a 15 minutos"
        )
    return info.proximo_fichaje.lower()


def ventana_auto_permitida(info: ProximoFichajeInfo) -> bool:
    # Reglas: ENTRADA: -3..+15; SALIDA: +5..+10
    dif = minutos_diferencia_ahora(info.hora_proximo_fichaje)
    if info.proximo_fichaje == "ENTRADA":
        if dif < -3:
            return False
        if dif > 15:
            return False
        return True
    else:
        if dif < 2:
            return False
        if dif > 10:
            return False
        return True


def realizar_fichaje(api: ApiClient, employee_code: str, tipo: TipoFichaje) -> Dict[str, Any]:
    return api.post_fichaje(employee_code=employee_code, tipo_fichaje=tipo)


def flujo_manual(api: ApiClient, employee_code: str, tipo: TipoFichaje) -> Dict[str, Any]:
    info = parse_proximo_fichaje(api.get_proximo_fichaje(employee_code))
    tipo=validar_manual(tipo, info)
    res = realizar_fichaje(api, employee_code, tipo)
    if not isinstance(res, dict) or (res.get("message") is None and res.get("fichaje") is None and res.get("error") is None):
        raise ApiError("Respuesta inesperada del servidor de fichajes")
    return res


def flujo_automatico(api: ApiClient, employee_code: str, tipo: TipoFichaje) -> Optional[Dict[str, Any]]:
    info = parse_proximo_fichaje(api.get_proximo_fichaje(employee_code))
    if info.es_festivo or info.en_vacaciones: #or info.tiene_incidencia:
        return None
    #if not ventana_auto_permitida(info):
    #    return None
    res = realizar_fichaje(api, employee_code, tipo)
    if not isinstance(res, dict):
        return None
    return res


def flujo_forzado(api: ApiClient, employee_code: str, tipo: TipoFichaje) -> Dict[str, Any]:
    # Sin validaciones previas; útil para pruebas o emergencias
    res = realizar_fichaje(api, employee_code, tipo)
    if not isinstance(res, dict):
        raise ApiError("Respuesta inesperada del servidor de fichajes")
    return res


