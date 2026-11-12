from flight_tracker.database import FlightRepository
from flight_tracker.models import Flight


def test_repository_saves_only_status_changes(tmp_path):
    repository = FlightRepository(tmp_path / "test.db")
    first = Flight("AB123", "2026-11-12", "scheduled", "Air Example", departure_iata="AAA", arrival_iata="BBB")
    changed = Flight("AB123", "2026-11-12", "active", "Air Example", departure_iata="AAA", arrival_iata="BBB")
    assert repository.save(first) is True
    assert repository.save(first) is False
    assert repository.save(changed) is True
    history = repository.history("AB123")
    assert [row["status"] for row in reversed(history)] == ["scheduled", "active"]
    assert len(repository.list_watched()) == 1


def test_delete_watched_flight(tmp_path):
    repository = FlightRepository(tmp_path / "test.db")
    flight = Flight("AB123", "2026-11-12", "scheduled")
    repository.save(flight)
    assert repository.delete("AB123", "2026-11-12") is True
    assert repository.delete("AB123", "2026-11-12") is False
