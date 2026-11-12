"""Command-line interface."""

import argparse
import logging
import sys
from datetime import date

from .api import AviationStackClient, FlightAPIError
from .config import get_api_key, get_api_timeout, get_database_path, load_dotenv
from .database import FlightRepository
from .demo import sample_flights
from .models import Flight
from .service import FlightService


def _print_flight(flight: Flight) -> None:
    print(f"\n{flight.flight_iata} | {flight.flight_date} | {flight.status_label}")
    print(f"Авиакомпания: {flight.airline}")
    print(f"Маршрут: {flight.departure_iata or '—'} ({flight.departure_airport}) -> "
          f"{flight.arrival_iata or '—'} ({flight.arrival_airport})")
    print(f"Вылет: {flight.departure_actual or flight.departure_scheduled or 'нет данных'}")
    print(f"Прибытие: {flight.arrival_actual or flight.arrival_scheduled or 'нет данных'}")
    print(f"Терминал/выход: {flight.departure_terminal or '—'} / {flight.departure_gate or '—'}")
    print(f"Источник: {flight.source}")


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flight-tracker", description="Отслеживание статусов пассажирских авиарейсов")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Найти рейс по номеру")
    search.add_argument("flight", help="Например, BA249 или SU2134")
    search.add_argument("--date", dest="flight_date", help="Дата рейса YYYY-MM-DD (требует доступа к историческим данным)")
    search.add_argument("--demo", action="store_true", help="Использовать демонстрационные данные без API")

    watch = sub.add_parser("watch", help="Найти рейс и добавить его в список отслеживания")
    watch.add_argument("flight")
    watch.add_argument("--date", dest="flight_date")

    sub.add_parser("list", help="Показать сохранённые рейсы")

    history = sub.add_parser("history", help="Показать историю статусов рейса")
    history.add_argument("flight")
    history.add_argument("--date", dest="flight_date")

    refresh = sub.add_parser("refresh", help="Обновить статусы всех сохранённых рейсов")
    refresh.add_argument("--demo", action="store_true", help="Использовать демонстрационные данные")

    remove = sub.add_parser("remove", help="Удалить рейс из списка отслеживания")
    remove.add_argument("flight")
    remove.add_argument("--date", dest="flight_date", required=True)
    return parser


def _get_service() -> FlightService:
    key = get_api_key()
    if not key:
        raise FlightAPIError("Не задан AVIATIONSTACK_API_KEY. Создайте бесплатный ключ, добавьте его в .env или используйте режим --demo.")
    return FlightService(AviationStackClient(key, get_api_timeout()), FlightRepository(get_database_path()))


def _demo_search(number: str, flight_date: str | None) -> list[Flight]:
    wanted_date = flight_date or date.today().isoformat()
    return [f for f in sample_flights() if f.flight_iata.upper() == number.upper() and f.flight_date == wanted_date]


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        filename="flight_tracker.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )
    logging.getLogger(__name__).info("Command started")
    args = _make_parser().parse_args()
    repository = FlightRepository(get_database_path())
    try:
        if args.command == "search":
            flights = _demo_search(args.flight, args.flight_date) if args.demo else _get_service().search(args.flight, args.flight_date)
            if not flights:
                print("Рейсы не найдены. Проверьте номер, дату и доступность данных у провайдера.")
            for flight in flights:
                _print_flight(flight)
        elif args.command == "watch":
            flights = _get_service().search(args.flight, args.flight_date)
            if not flights:
                print("Рейс не найден.")
                return
            for flight in flights:
                changed = repository.save(flight)
                _print_flight(flight)
                print("Рейс добавлен/обновлён. " + ("Записано новое состояние." if changed else "Статус не изменился."))
        elif args.command == "list":
            rows = repository.list_watched()
            if not rows:
                print("Список отслеживаемых рейсов пуст.")
            for row in rows:
                print(f"{row['flight_iata']} | {row['flight_date']} | {row['departure_iata'] or '—'} -> "
                      f"{row['arrival_iata'] or '—'} | {row['current_status']} | {row['updated_at']}")
        elif args.command == "history":
            rows = repository.history(args.flight, args.flight_date)
            if not rows:
                print("История для этого рейса не найдена.")
            for row in rows:
                print(f"{row['recorded_at']} | {row['flight_date']} | {row['status']}")
        elif args.command == "refresh":
            rows = repository.list_watched()
            if not rows:
                print("Нет рейсов для обновления.")
                return
            if args.demo:
                print("Демо-режим: статусы не обновляются из интернета.")
                return
            service = _get_service()
            for row in rows:
                try:
                    found = service.search(row["flight_iata"], row["flight_date"])
                    for flight in found:
                        changed = repository.save(flight)
                        print(f"{flight.flight_iata}: {flight.status_label}" + (" (изменение)" if changed else ""))
                    if not found:
                        print(f"{row['flight_iata']}: провайдер не вернул данные")
                except FlightAPIError as exc:
                    print(f"{row['flight_iata']}: ошибка: {exc}")

                    if "недоступна на вашем тарифе" in str(exc):
                        print(
                            "Обновление остановлено: "
                            "текущий тариф Aviationstack не поддерживает "
                            "исторический поиск."
                        )
                        break
        elif args.command == "remove":
            removed = repository.delete(args.flight, args.flight_date)
            print("Рейс удалён." if removed else "Рейс не найден в списке отслеживания.")
    except (FlightAPIError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
