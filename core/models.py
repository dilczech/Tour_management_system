from core.interfaces import ITour


class BeachTour(ITour):
    """Сущность пляжного тура."""

    def __init__(self, name: str, country: str, days: int, beach_type: str):
        self._name = name
        self._country = country
        self._days = days
        self._beach_type = beach_type

    def get_name(self) -> str:
        return self._name

    def get_country(self) -> str:
        return self._country

    def get_days(self) -> int:
        return self._days

    def get_details(self) -> str:
        return f"Тип пляжа: {self._beach_type}"

    def get_specific_raw(self) -> str:
        return self._beach_type

    def clone(self) -> ITour:
        return BeachTour(
            self._name, self._country, self._days, self._beach_type
        )

    def to_dict(self) -> dict:
        return {
            "type": "beach",
            "name": self._name,
            "country": self._country,
            "days": self._days,
            "beach_type": self._beach_type,
        }

    def __str__(self) -> str:
        return f"Пляжный тур '{self._name}' в {self._country} ({self._days} дн., пляж: {self._beach_type})"


class ExcursionTour(ITour):
    """Сущность экскурсионного тура."""

    def __init__(self, name: str, country: str, days: int, excursions: int):
        self._name = name
        self._country = country
        self._days = days
        self._excursions = excursions

    def get_name(self) -> str:
        return self._name

    def get_country(self) -> str:
        return self._country

    def get_days(self) -> int:
        return self._days

    def get_details(self) -> str:
        return f"Количество экскурсий: {self._excursions}"

    def get_specific_raw(self) -> int:
        return self._excursions

    def clone(self) -> ITour:
        return ExcursionTour(
            self._name, self._country, self._days, self._excursions
        )

    def to_dict(self) -> dict:
        return {
            "type": "excursion",
            "name": self._name,
            "country": self._country,
            "days": self._days,
            "excursions": self._excursions,
        }

    def __str__(self) -> str:
        return f"Экскурсионный тур '{self._name}' в {self._country} ({self._days} дн., экскурсий: {self._excursions})"