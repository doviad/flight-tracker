"""SQLite persistence for watched flights and status history."""

import sqlite3
from pathlib import Path

from .models import Flight


class FlightRepository:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS watched_flights (
                    flight_iata TEXT NOT NULL,
                    flight_date TEXT NOT NULL,
                    airline TEXT NOT NULL,
                    departure_iata TEXT,
                    arrival_iata TEXT,
                    current_status TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (flight_iata, flight_date)
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flight_iata TEXT NOT NULL,
                    flight_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save(self, flight: Flight) -> bool:
        """Save a flight; return True only when its status changed or it is new."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT current_status FROM watched_flights WHERE flight_iata=? AND flight_date=?",
                (flight.flight_iata, flight.flight_date),
            ).fetchone()
            changed = row is None or row["current_status"] != flight.status
            connection.execute("""
                INSERT INTO watched_flights
                (flight_iata, flight_date, airline, departure_iata, arrival_iata, current_status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(flight_iata, flight_date) DO UPDATE SET
                    airline=excluded.airline,
                    departure_iata=excluded.departure_iata,
                    arrival_iata=excluded.arrival_iata,
                    current_status=excluded.current_status,
                    updated_at=CURRENT_TIMESTAMP
            """, (flight.flight_iata, flight.flight_date, flight.airline,
                  flight.departure_iata, flight.arrival_iata, flight.status))
            if changed:
                connection.execute(
                    "INSERT INTO status_history (flight_iata, flight_date, status) VALUES (?, ?, ?)",
                    (flight.flight_iata, flight.flight_date, flight.status),
                )
            return changed

    def list_watched(self) -> list[sqlite3.Row]:
        with self._connect() as connection:
            return connection.execute(
                "SELECT * FROM watched_flights ORDER BY flight_date DESC, flight_iata"
            ).fetchall()

    def history(self, flight_iata: str, flight_date: str | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM status_history WHERE upper(flight_iata)=upper(?)"
        params: list[str] = [flight_iata]
        if flight_date:
            query += " AND flight_date=?"
            params.append(flight_date)
        query += " ORDER BY recorded_at DESC, id DESC"
        with self._connect() as connection:
            return connection.execute(query, params).fetchall()

    def delete(self, flight_iata: str, flight_date: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM watched_flights WHERE upper(flight_iata)=upper(?) AND flight_date=?",
                (flight_iata, flight_date),
            )
            return cursor.rowcount > 0
