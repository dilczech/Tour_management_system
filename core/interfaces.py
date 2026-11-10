from abc import ABC, abstractmethod
from typing import Any, List


class INamedEntity(ABC):
    """Интерфейс сущности с наименованием."""

    @abstractmethod
    def get_name(self) -> str:
        pass


class ILocatable(ABC):
    """Интерфейс сущности с географической локацией."""

    @abstractmethod
    def get_country(self) -> str:
        pass


class IDetailedEntity(ABC):
    """Интерфейс сущности с характеристиками длительности и описания."""

    @abstractmethod
    def get_days(self) -> int:
        pass

    @abstractmethod
    def get_details(self) -> str:
        pass


class ITour(INamedEntity, ILocatable, IDetailedEntity, ABC):
    """Интерфейс тура с поддержкой клонирования и сериализации."""

    @abstractmethod
    def clone(self) -> "ITour":
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass


class ICountryProvider(ABC):
    """Интерфейс поставщика справочных данных о странах."""

    @abstractmethod
    def is_valid_country(self, country_name: str) -> bool:
        pass


class IValidator(ABC):
    """Интерфейс для валидации значения."""

    @abstractmethod
    def validate(self, value: Any) -> None:
        pass


class ITourReader(ABC):
    """Интерфейс для чтения туров из хранилища."""

    @abstractmethod
    def get_all(self) -> List[ITour]:
        pass


class ITourWriter(ABC):
    """Интерфейс для добавления туров в хранилище."""

    @abstractmethod
    def add(self, tour: ITour) -> None:
        pass


class ITourRepository(ITourReader, ITourWriter, ABC):
    """Интерфейс репозитория с возможностью закрытия базы данных."""

    @abstractmethod
    def close_db(self) -> None:
        pass


class ITourFilter(ABC):
    """Интерфейс фильтрации туров."""

    @abstractmethod
    def matches(self, tour: ITour) -> bool:
        pass


class ITourAbstractFactory(ABC):
    """Абстрактная фабрика для семейства компонентов тура."""

    @abstractmethod
    def get_type_name(self) -> str:
        pass

    @abstractmethod
    def create_tour(
        self, name: str, country: str, days: int, specific_value: Any
    ) -> ITour:
        pass

    @abstractmethod
    def create_specific_validator(self) -> IValidator:
        pass


class ICommand(ABC):
    """Интерфейс команды для пунктов меню."""

    @abstractmethod
    def execute(self) -> None:
        pass