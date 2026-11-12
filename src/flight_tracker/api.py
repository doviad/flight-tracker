
"""Aviationstack API client."""

from typing import Any

import requests

from .models import Flight

BASE_URL = "https://api.aviationstack.com/v1/flights"


class FlightAPIError(Exception):
    """Raised when the flight data provider cannot return usable data."""


class AviationStackClient:
    def __init__(self, api_key: str, timeout: int = 20) -> None:
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.timeout = timeout

    def _handle_api_error(self, error: Any) -> None:
        if isinstance(error, dict):
            code = error.get("code", "")
            message = error.get("message", "Неизвестная ошибка API")
        else:
            code = ""
            message = str(error)

        errors = {
            "invalid_access_key": "Неверный API-ключ Aviationstack.",
            "missing_access_key": "Не указан API-ключ Aviationstack.",
            "function_access_restricted": (
                "Эта функция недоступна на вашем тарифе Aviationstack. "
                "Проверьте ограничения подписки."
            ),
            "usage_limit_reached": (
                "Исчерпана месячная квота запросов Aviationstack. "
                "Дождитесь её обновления или измените тариф."
            ),
            "rate_limit_reached": (
                "Превышена частота запросов к Aviationstack. "
                "Подождите немного и попробуйте снова."
            ),
            "inactive_user": "Аккаунт Aviationstack неактивен.",
        }

        if code in errors:
            raise FlightAPIError(errors[code])

        raise FlightAPIError(f"Ошибка Aviationstack: {message}")

    def search(
        self,
        flight_iata: str,
        flight_date: str | None = None,
    ) -> list[Flight]:
        params: dict[str, Any] = {
            "access_key": self.api_key,
            "flight_iata": flight_iata.strip().upper(),
            "limit": 100,
        }

        if flight_date:
            params["flight_date"] = flight_date

        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise FlightAPIError(
                "Истекло время ожидания ответа API."
            ) from exc
        except requests.RequestException as exc:
            raise FlightAPIError(
                f"Ошибка HTTP-запроса: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            if not response.ok:
                raise FlightAPIError(
                    f"Ошибка HTTP {response.status_code}: {response.reason}"
                ) from exc

            raise FlightAPIError(
                "API вернул некорректный JSON."
            ) from exc

        if isinstance(payload, dict) and payload.get("error"):
            self._handle_api_error(payload["error"])

        if not response.ok:
            raise FlightAPIError(
                f"Ошибка HTTP {response.status_code}: {response.reason}"
            )

        if not isinstance(payload, dict):
            raise FlightAPIError(
                "Неожиданный формат ответа API."
            )

        data = payload.get("data")

        if not isinstance(data, list):
            raise FlightAPIError(
                "Неожиданный формат ответа API: отсутствует список data."
            )

        return [
            Flight.from_api(item)
            for item in data
            if isinstance(item, dict)
        ]
