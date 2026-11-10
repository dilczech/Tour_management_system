import os
from factories.factories import (
    BeachTourFactory,
    ExcursionTourFactory,
    TourFactoryRegistry,
)
from ui.menu import (
    AddTourCommand,
    CloneTourCommand,
    CloseDbCommand,
    ExitCommand,
    MenuBuilder,
    SearchEgyptCommand,
    ShowToursCommand,
)
from storage.storage import DbMode, JsonCountryProvider, LazyJsonTourRepository
from core.validators import (
    BeachTypeValidator,
    CountryValidator,
    ExcursionsCountValidator,
    NonEmptyStringValidator,
    PositiveIntegerValidator,
)


def choose_database_mode() -> LazyJsonTourRepository:
    """Интерактивно запрашивает режим БД с автопоиском файлов в папке data/."""
    print("=" * 55)
    print("   СИСТЕМА УЧЕТА ТУРОВ (ПОРОЖДАЮЩИЕ ПАТТЕРНЫ)")
    print("=" * 55)
    
    # Автоматически создаем папку data, если её нет
    os.makedirs("data", exist_ok=True)
    
    # Сканируем папку data/ на предмет существующих файлов БД (кроме стран)
    existing_files = [
        f for f in os.listdir("data") 
        if f.endswith(".json") and f != "countries.json"
    ]

    print("Выберите режим работы с базой данных:")
    print(" [1] Создать новую БД")
    print(" [2] Открыть существующую БД")
    print(" [3] Работать в памяти без файла (старый режим)")

    while True:
        choice = input("\nВаш выбор [1/2/3]: ").strip()
        if choice == "1":
            name = input("Имя нового файла БД [tours.json]: ").strip() or "tours.json"
            # Жестко принуждаем сохранять в папку data/
            filename = os.path.join("data", os.path.basename(name))
            return LazyJsonTourRepository(DbMode.NEW, filename)

        elif choice == "2":
            print("\nДоступные файлы в папке data/:")
            if existing_files:
                for idx, fname in enumerate(existing_files, 1):
                    print(f"   [{idx}] {fname}")
            else:
                print("   (Пока нет сохраненных файлов туров в папке data/)")

            name = input("Введите имя файла или его номер: ").strip() or "tours.json"
            
            # Если ввели цифру-номер из списка
            if name.isdigit() and 1 <= int(name) <= len(existing_files):
                name = existing_files[int(name) - 1]

            filename = os.path.join("data", os.path.basename(name))
            return LazyJsonTourRepository(DbMode.OPEN_EXISTING, filename)

        elif choice == "3":
            print("-> Выбран режим работы в оперативной памяти (без сохранения в файл).")
            return LazyJsonTourRepository(DbMode.IN_MEMORY)
        else:
            print("[Ошибка] Введите 1, 2 или 3.")


def main():
    """Точка входа и сборки приложения."""
    repository = choose_database_mode()

    country_provider = JsonCountryProvider("data/countries.json")
    name_val = NonEmptyStringValidator("Название тура")
    country_val = CountryValidator(country_provider)
    days_val = PositiveIntegerValidator("Количество дней")
    beach_val = BeachTypeValidator()
    exc_val = ExcursionsCountValidator()

    registry = TourFactoryRegistry()
    beach_factory = BeachTourFactory()
    excursion_factory = ExcursionTourFactory()

    registry.register("1", beach_factory)
    registry.register("пляжный", beach_factory)
    registry.register("п", beach_factory)

    registry.register("2", excursion_factory)
    registry.register("экскурсионный", excursion_factory)
    registry.register("э", excursion_factory)

    add_cmd = AddTourCommand(
        repository, registry, name_val, country_val, days_val
    )
    show_cmd = ShowToursCommand(repository)
    search_cmd = SearchEgyptCommand(repository)
    clone_cmd = CloneTourCommand(
        repository, name_val, country_val, days_val, beach_val, exc_val
    )
    close_db_cmd = CloseDbCommand(repository)
    exit_cmd = ExitCommand(repository)

    menu = (
        MenuBuilder()
        .set_title("ГЛАВНОЕ МЕНЮ СИСТЕМЫ ТУРОВ")
        .add_item("1", "Добавить новый тур", add_cmd)
        .add_item("2", "Показать все туры", show_cmd)
        .add_item("3", "Поиск туров со словом 'Египет'", search_cmd)
        .add_item("4", "Клонировать и редактировать тур (Прототип)", clone_cmd)
        .add_item("5", "Закрыть файл базы данных", close_db_cmd)
        .add_item("0", "Выход из программы", exit_cmd)
        .build()
    )

    menu.run()


if __name__ == "__main__":
    main()