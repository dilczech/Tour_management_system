from typing import Any, Dict, List, Optional
from core.interfaces import ITour, ITourAbstractFactory, IValidator
from core.models import BeachTour, ExcursionTour
from core.validators import BeachTypeValidator, ExcursionsCountValidator


class BeachTourFactory(ITourAbstractFactory):
    """Фабрика компонентов пляжного отдыха."""

    def get_type_name(self) -> str:
        return "пляжный"

    def create_tour(
        self, name: str, country: str, days: int, specific_value: Any
    ) -> ITour:
        return BeachTour(name, country, days, str(specific_value))

    def create_specific_validator(self) -> IValidator:
        return BeachTypeValidator()


class ExcursionTourFactory(ITourAbstractFactory):
    """Фабрика компонентов экскурсионного отдыха."""

    def get_type_name(self) -> str:
        return "экскурсионный"

    def create_tour(
        self, name: str, country: str, days: int, specific_value: Any
    ) -> ITour:
        return ExcursionTour(name, country, days, int(specific_value))

    def create_specific_validator(self) -> IValidator:
        return ExcursionsCountValidator()

#Абстрактная фабрика
class TourFactoryRegistry:
    """Реестр фабрик создания туров."""

    def __init__(self):
        self._factories: Dict[str, ITourAbstractFactory] = {}

    def register(self, key: str, factory: ITourAbstractFactory) -> None:
        self._factories[key.lower()] = factory

    def get_factory(self, key: str) -> Optional[ITourAbstractFactory]:
        return self._factories.get(key.strip().lower())

    def get_available_types(self) -> List[str]:
        unique = {f.get_type_name() for f in self._factories.values()}
        return sorted(list(unique))