"""Clearly labelled sample data for offline demonstrations."""

from datetime import date

from .models import Flight


def sample_flights() -> list[Flight]:
    today = date.today().isoformat()
    return [
        Flight("SU2134", today, "active", "Aeroflot", "Sheremetyevo International Airport", "SVO",
               "2026-11-12T09:30:00+00:00", "2026-11-12T09:42:00+00:00",
               "Istanbul Airport", "IST", "2026-11-12T13:15:00+00:00", "",
               source="DEMO — не реальные данные"),
        Flight("LH400", today, "scheduled", "Lufthansa", "Frankfurt Airport", "FRA",
               "2026-11-12T17:00:00+00:00", "", "John F. Kennedy International Airport", "JFK",
               "2026-11-12T20:05:00+00:00", "", source="DEMO — не реальные данные"),
        Flight("BA249", today, "cancelled", "British Airways", "London Heathrow Airport", "LHR",
               "2026-11-12T11:00:00+00:00", "", "Rio de Janeiro/Galeao International Airport", "GIG",
               "2026-11-12T19:45:00+00:00", "", source="DEMO — не реальные данные"),
    ]
