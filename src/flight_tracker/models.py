"""Domain models and status presentation helpers."""

from dataclasses import dataclass

STATUS_LABELS = {
    "scheduled": "Запланирован",
    "active": "Выполняется",
    "landed": "Приземлился",
    "cancelled": "Отменён",
    "incident": "Инцидент",
    "diverted": "Изменён маршрут",
    "unknown": "Неизвестен",
}


@dataclass(frozen=True)
class Flight:
    flight_iata: str
    flight_date: str
    status: str
    airline: str = "Не указана"
    departure_airport: str = "Не указан"
    departure_iata: str = ""
    departure_scheduled: str = ""
    departure_actual: str = ""
    arrival_airport: str = "Не указан"
    arrival_iata: str = ""
    arrival_scheduled: str = ""
    arrival_actual: str = ""
    departure_terminal: str = ""
    departure_gate: str = ""
    arrival_terminal: str = ""
    arrival_gate: str = ""
    source: str = "Aviationstack"

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status.lower(), self.status or STATUS_LABELS["unknown"])

    @classmethod
    def from_api(cls, item: dict) -> "Flight":
        airline = item.get("airline") or {}
        flight = item.get("flight") or {}
        departure = item.get("departure") or {}
        arrival = item.get("arrival") or {}
        number = flight.get("iata") or flight.get("number") or "UNKNOWN"
        return cls(
            flight_iata=str(number).upper(),
            flight_date=str(item.get("flight_date") or ""),
            status=str(item.get("flight_status") or "unknown").lower(),
            airline=str(airline.get("name") or "Не указана"),
            departure_airport=str(departure.get("airport") or "Не указан"),
            departure_iata=str(departure.get("iata") or ""),
            departure_scheduled=str(departure.get("scheduled") or ""),
            departure_actual=str(departure.get("actual") or departure.get("estimated") or ""),
            arrival_airport=str(arrival.get("airport") or "Не указан"),
            arrival_iata=str(arrival.get("iata") or ""),
            arrival_scheduled=str(arrival.get("scheduled") or ""),
            arrival_actual=str(arrival.get("actual") or arrival.get("estimated") or ""),
            departure_terminal=str(departure.get("terminal") or ""),
            departure_gate=str(departure.get("gate") or ""),
            arrival_terminal=str(arrival.get("terminal") or ""),
            arrival_gate=str(arrival.get("gate") or ""),
        )
