from typing import Any
from core.interfaces import ICountryProvider, IValidator


class NonEmptyStringValidator(IValidator):
    """Валидатор проверки непустой строки."""

    def __init__(self, field_name: str):
        self._field_name = field_name

    def validate(self, value: Any) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Поле '{self._field_name}' не может быть пустым.")


class PositiveIntegerValidator(IValidator):
    """Валидатор положительного целого числа."""

    def __init__(self, field_name: str):
        self._field_name = field_name

    def validate(self, value: Any) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError(
                f"Поле '{self._field_name}' должно быть целым числом больше 0."
            )


class CountryValidator(IValidator):
    """Валидатор страны через провайдер данных."""

    def __init__(self, provider: ICountryProvider):
        self._provider = provider

    def validate(self, value: Any) -> None:
        if not self._provider.is_valid_country(str(value)):
            raise ValueError(f"Страна '{value}' не найдена в списке стран.")


class BeachTypeValidator(IValidator):
    """Валидатор допустимого типа пляжа."""

    ALLOWED = ("песок", "галечный")

    def validate(self, value: Any) -> None:
        if str(value).strip().lower() not in self.ALLOWED:
            raise ValueError(
                f"Неверный тип пляжа. Допустимо: {', '.join(self.ALLOWED)}."
            )


class ExcursionsCountValidator(IValidator):
    """Валидатор количества экскурсий."""

    def validate(self, value: Any) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError("Количество экскурсий должно быть не меньше 1.")