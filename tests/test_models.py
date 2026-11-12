from flight_tracker.models import Flight


def test_flight_from_api_normalizes_nested_response():
    flight = Flight.from_api({
        "flight_date": "2026-11-12",
        "flight_status": "active",
        "airline": {"name": "Example Air"},
        "flight": {"iata": "ea123"},
        "departure": {"airport": "Origin", "iata": "AAA", "scheduled": "2026-11-12T10:00:00+00:00"},
        "arrival": {"airport": "Destination", "iata": "BBB"},
    })
    assert flight.flight_iata == "EA123"
    assert flight.status == "active"
    assert flight.departure_iata == "AAA"
    assert flight.status_label == "Выполняется"


def test_unknown_status_is_preserved():
    flight = Flight("ZZ1", "2026-11-12", "new_provider_status")
    assert flight.status_label == "new_provider_status"
