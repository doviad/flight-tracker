"""Application use cases."""

from datetime import date

from .api import AviationStackClient
from .database import FlightRepository
from .models import Flight


class FlightService:
    def __init__(self, client: AviationStackClient, repository: FlightRepository) -> None:
        self.client = client
        self.repository = repository

    def search(self, flight_iata: str, flight_date: str | None = None) -> list[Flight]:
        if not flight_iata.strip():
            raise ValueError("Номер рейса не должен быть пустым.")
        if flight_date:
            try:
                date.fromisoformat(flight_date)
            except ValueError as exc:
                raise ValueError("Дата должна иметь формат YYYY-MM-DD.") from exc
        return self.client.search(flight_iata, flight_date)

    def watch(self, flight: Flight) -> bool:
        return self.repository.save(flight)
