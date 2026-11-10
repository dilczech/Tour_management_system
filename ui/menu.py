from typing import List, Optional
from factories.factories import TourFactoryRegistry
from core.interfaces import (
    ICommand,
    ITour,
    ITourFilter,
    ITourRepository,
    IValidator,
)
from core.models import BeachTour, ExcursionTour


class KeywordTourFilter(ITourFilter):
    """Фильтр поиска по ключевому слову в названии или стране."""

    def __init__(self, keyword: str):
        self._keyword = keyword.strip().lower()

    def matches(self, tour: ITour) -> bool:
        in_name = self._keyword in tour.get_name().lower()
        in_country = self._keyword in tour.get_country().lower()
        return in_name or in_country


class AddTourCommand(ICommand):
    """Команда интерактивного добавления тура через Абстрактную фабрику."""

    def __init__(
        self,
        repository: ITourRepository,
        registry: TourFactoryRegistry,
        name_val: IValidator,
        country_val: IValidator,
        days_val: IValidator,
    ):
        self._repo = repository
        self._registry = registry
        self._name_val = name_val
        self._country_val = country_val
        self._days_val = days_val

    def execute(self) -> None:
        print("\n--- СОЗДАНИЕ НОВОГО ТУРА ---")
        try:
            name = input("Введите название тура: ").strip()
            self._name_val.validate(name)

            country = (
                input("Введите страну тура [Египет]: ").strip() or "Египет"
            )
            self._country_val.validate(country)

            days_str = input("Количество дней [7]: ").strip() or "7"
            try:
                days = int(days_str)
            except ValueError:
                raise ValueError("Количество дней должно быть целым числом.")
            self._days_val.validate(days)

            types = self._registry.get_available_types()
            type_choice = (
                input(
                    "Тип тура (1 - пляжный [по умолчанию], 2 - экскурсионный): "
                ).strip()
                or "1"
            )

            factory = self._registry.get_factory(type_choice)
            if not factory:
                raise ValueError(
                    f"Неизвестный тип тура. Доступны: {', '.join(types)}"
                )

            spec_val = factory.create_specific_validator()

            if factory.get_type_name() == "пляжный":
                beach_choice = (
                    input(
                        "Тип пляжа (1 - песок [по умолчанию], 2 - галечный): "
                    ).strip()
                    or "1"
                )
                beach = (
                    "галечный"
                    if beach_choice in ("2", "галечный", "г")
                    else "песок"
                )
                spec_val.validate(beach)
                tour = factory.create_tour(name, country, days, beach)
            else:
                exc_str = input("Количество экскурсий [3]: ").strip() or "3"
                try:
                    excursions = int(exc_str)
                except ValueError:
                    raise ValueError(
                        "Число экскурсий должно быть целым числом."
                    )
                spec_val.validate(excursions)
                tour = factory.create_tour(name, country, days, excursions)

            self._repo.add(tour)
            print(f"-> Тур успешно добавлен: {tour}")

        except (ValueError, FileNotFoundError) as e:
            print(f"[Ошибка] {e}")


class ShowToursCommand(ICommand):
    """Команда отображения всех зарегистрированных туров."""

    def __init__(self, repository: ITourRepository):
        self._repo = repository

    def execute(self) -> None:
        try:
            tours = self._repo.get_all()
            print("\n" + "=" * 60)
            print(" СПИСОК ВСЕХ ТУРОВ")
            print("=" * 60)
            if not tours:
                print("База данных туров пуста.")
                return

            for idx, tour in enumerate(tours, start=1):
                print(
                    f"[{idx}] {tour.get_name()} | Страна: {tour.get_country()}"
                )
                print(f"    Дней: {tour.get_days()} | {tour.get_details()}")
        except FileNotFoundError as e:
            print(f"[Ошибка БД] {e}")


class SearchEgyptCommand(ICommand):
    """Команда поиска туров, содержащих слово 'Египет'."""

    def __init__(self, repository: ITourRepository):
        self._repo = repository

    def execute(self) -> None:
        try:
            tours = self._repo.get_all()
            egypt_filter = KeywordTourFilter("египет")
            matched = [t for t in tours if egypt_filter.matches(t)]

            print("\n" + "=" * 60)
            print(" РЕЗУЛЬТАТЫ ПОИСКА: ТУРЫ СО СЛОВОМ 'ЕГИПЕТ'")
            print("=" * 60)
            if not matched:
                print("Туров со словом 'Египет' не найдено.")
                return

            for idx, tour in enumerate(matched, start=1):
                print(f"[{idx}] {tour}")
        except FileNotFoundError as e:
            print(f"[Ошибка БД] {e}")


class CloneTourCommand(ICommand):
    """Команда клонирования тура с редактированием полей."""

    def __init__(
        self,
        repository: ITourRepository,
        name_val: IValidator,
        country_val: IValidator,
        days_val: IValidator,
        beach_val: IValidator,
        exc_val: IValidator,
    ):
        self._repo = repository
        self._name_val = name_val
        self._country_val = country_val
        self._days_val = days_val
        self._beach_val = beach_val
        self._exc_val = exc_val

    def execute(self) -> None:
        try:
            tours = self._repo.get_all()
        except FileNotFoundError as e:
            print(f"[Ошибка БД] {e}")
            return

        if not tours:
            print("\nБаза пуста. Нечего клонировать.")
            return

        print("\n--- КЛОНИРОВАНИЕ ТУРА (ПАТТЕРН ПРОТОТИП) ---")
        for idx, t in enumerate(tours, start=1):
            print(f"[{idx}] {t}")

        idx_str = input("\nВыберите номер тура для клонирования: ").strip()
        try:
            choice_idx = int(idx_str) - 1
            if choice_idx < 0 or choice_idx >= len(tours):
                raise ValueError("Неверный номер тура.")
        except ValueError:
            print("[Ошибка] Введите корректный номер тура.")
            return

        original_tour = tours[choice_idx]
        cloned_tour = original_tour.clone()

        print(
            "\nРедактирование полей клона (нажмите Enter, чтобы оставить старое значение):"
        )
        try:
            new_name = (
                input(f"Название [{cloned_tour.get_name()}]: ").strip()
                or cloned_tour.get_name()
            )
            self._name_val.validate(new_name)

            new_country = (
                input(f"Страна [{cloned_tour.get_country()}]: ").strip()
                or cloned_tour.get_country()
            )
            self._country_val.validate(new_country)

            new_days_str = (
                input(f"Количество дней [{cloned_tour.get_days()}]: ").strip()
                or str(cloned_tour.get_days())
            )
            try:
                new_days = int(new_days_str)
            except ValueError:
                raise ValueError("Количество дней должно быть числом.")
            self._days_val.validate(new_days)

            if isinstance(cloned_tour, BeachTour):
                old_beach = cloned_tour.get_specific_raw()
                new_beach = (
                    input(
                        f"Тип пляжа (песок/галечный) [{old_beach}]: "
                    ).strip()
                    or old_beach
                )
                self._beach_val.validate(new_beach)
                final_tour = BeachTour(
                    new_name, new_country, new_days, new_beach
                )
            elif isinstance(cloned_tour, ExcursionTour):
                old_exc = cloned_tour.get_specific_raw()
                new_exc_str = input(
                    f"Количество экскурсий [{old_exc}]: "
                ).strip() or str(old_exc)
                try:
                    new_exc = int(new_exc_str)
                except ValueError:
                    raise ValueError("Число экскурсий должно быть числом.")
                self._exc_val.validate(new_exc)
                final_tour = ExcursionTour(
                    new_name, new_country, new_days, new_exc
                )
            else:
                final_tour = cloned_tour

            self._repo.add(final_tour)
            print(f"-> Клон успешно сохранен как новый тур: {final_tour}")

        except ValueError as e:
            print(f"[Ошибка при редактировании клона] {e}")


class CloseDbCommand(ICommand):
    """Команда явного сохранения и закрытия файла базы данных."""

    def __init__(self, repository: ITourRepository):
        self._repo = repository

    def execute(self) -> None:
        self._repo.close_db()
        print("\n-> Файл базы данных успешно сохранен и закрыт.")


class ExitCommand(ICommand):
    """Команда выхода из программы с автоматическим закрытием базы."""

    def __init__(self, repository: ITourRepository):
        self._repo = repository
        self.should_exit = False

    def execute(self) -> None:
        self._repo.close_db()
        print("\nЗавершение работы программы. До свидания!")
        self.should_exit = True


class MenuItem:
    """Элемент меню с ключом, описанием и связанной командой."""

    def __init__(self, key: str, label: str, command: ICommand):
        self.key = key
        self.label = label
        self.command = command


class Menu:
    """Класс отображения и выполнения интерактивного меню."""

    def __init__(self, title: str, items: List[MenuItem], exit_cmd: ExitCommand):
        self._title = title
        self._items = items
        self._exit_cmd = exit_cmd

    def run(self) -> None:
        while not self._exit_cmd.should_exit:
            print("\n" + "=" * 50)
            print(f" {self._title}")
            print("=" * 50)
            for item in self._items:
                print(f" [{item.key}] {item.label}")

            choice = input("\nВыберите действие: ").strip()
            matched = False
            for item in self._items:
                if item.key == choice:
                    item.command.execute()
                    matched = True
                    break

            if not matched:
                print("[Ошибка] Неверный пункт меню. Попробуйте снова.")


class MenuBuilder:
    """Строитель для пошаговой сборки интерактивного меню."""

    def __init__(self):
        self._title = "МЕНЮ"
        self._items: List[MenuItem] = []
        self._exit_cmd: Optional[ExitCommand] = None

    def set_title(self, title: str) -> "MenuBuilder":
        self._title = title
        return self

    def add_item(self, key: str, label: str, command: ICommand) -> "MenuBuilder":
        if isinstance(command, ExitCommand):
            self._exit_cmd = command
        self._items.append(MenuItem(key, label, command))
        return self

    def build(self) -> Menu:
        if not self._exit_cmd:
            raise ValueError("Меню должно содержать команду ExitCommand.")
        return Menu(self._title, self._items, self._exit_cmd)