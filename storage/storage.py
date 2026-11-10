from enum import Enum
import json
import os
from typing import Dict, List, Optional
from core.interfaces import ICountryProvider, ITour, ITourRepository
from core.models import BeachTour, ExcursionTour


class DbMode(Enum):
    """Режимы работы базы данных."""

    NEW = "new"
    OPEN_EXISTING = "open"
    IN_MEMORY = "memory"


class JsonCountryProvider(ICountryProvider):
    """Провайдер справочника стран на базе JSON-файла."""

    def __init__(self, filepath: str = "data/countries.json"):
        self._countries: Dict[str, str] = self._load(filepath)

    def _load(self, filepath: str) -> Dict[str, str]:
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        if not os.path.exists(filepath):
            return {"Египет": "Egypt", "Россия": "Russia", "Турция": "Turkey"}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"Египет": "Egypt"}

    def is_valid_country(self, country_name: str) -> bool:
        c = country_name.strip().lower()
        for ru, en in self._countries.items():
            if c == ru.strip().lower() or c == en.strip().lower():
                return True
        return False


class LazyJsonTourRepository(ITourRepository):
    """Репозиторий с ленивой инициализацией файлового дескриптора."""

    def __init__(self, mode: DbMode, filepath: Optional[str] = None):
        if mode != DbMode.IN_MEMORY and not filepath:
            raise ValueError("Для файлового режима требуется указать имя файла.")

        self._mode = mode
        self._filepath = filepath
        self._tours: List[ITour] = []
        self._is_initialized = False
        self._file_handle = None

    def _ensure_initialized(self) -> None:
        if self._is_initialized:
            return

        if self._mode == DbMode.IN_MEMORY:
            self._is_initialized = True
            return

        dirname = os.path.dirname(self._filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        if self._mode == DbMode.NEW:
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump([], f)
            self._file_handle = open(self._filepath, "r+", encoding="utf-8")
            self._tours = []

        elif self._mode == DbMode.OPEN_EXISTING:
            if not os.path.exists(self._filepath):
                raise FileNotFoundError(
                    f"Файл базы данных '{self._filepath}' не найден."
                )
            self._file_handle = open(self._filepath, "r+", encoding="utf-8")
            content = self._file_handle.read().strip()
            if content:
                try:
                    raw_data = json.loads(content)
                    self._tours = [self._deserialize_tour(item) for item in raw_data]
                except json.JSONDecodeError:
                    self._tours = []
            else:
                self._tours = []

        self._is_initialized = True

    def _deserialize_tour(self, data: dict) -> ITour:
        tour_type = data.get("type")
        if tour_type == "beach":
            return BeachTour(
                data["name"], data["country"], data["days"], data["beach_type"]
            )
        elif tour_type == "excursion":
            return ExcursionTour(
                data["name"], data["country"], data["days"], data["excursions"]
            )
        raise ValueError(f"Неизвестный тип тура в базе данных: {tour_type}")

    def _sync_to_disk(self) -> None:
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.seek(0)
            self._file_handle.truncate(0)
            data = [t.to_dict() for t in self._tours]
            json.dump(data, self._file_handle, ensure_ascii=False, indent=2)
            self._file_handle.flush()

    def add(self, tour: ITour) -> None:
        if tour is None:
            raise ValueError("Невозможно добавить пустой тур (None).")
        self._ensure_initialized()
        self._tours.append(tour)
        self._sync_to_disk()

    def get_all(self) -> List[ITour]:
        self._ensure_initialized()
        return list(self._tours)

    def close_db(self) -> None:
        if self._file_handle and not self._file_handle.closed:
            self._sync_to_disk()
            self._file_handle.close()
            self._file_handle = None
            self._is_initialized = False

    def is_file_open(self) -> bool:
        return self._file_handle is not None and not self._file_handle.closed