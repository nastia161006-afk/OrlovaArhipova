# FX: справка для ЛР5

Объект курса содержит направление обмена и точный коэффициент. Источник ищет курс, сервис рассчитывает денежный результат.

Здесь перечислены типы текущей работы. Что требуется реализовать и какие файлы можно менять, указано в [TASK.md](TASK.md).

## Предметные объекты и исполнители

| Тип и конструктор | Публичные действия и свойства | Файл |
|---|---|---|
| `LegacyRatesAdapter(legacy)` | `get_rate(source, target)` | `app/domain/adapters.py` |
| `ExchangeRate(source, target, rate)` | `source`, `target`, `rate`, `matches(source, target)` | `app/domain/fx.py` |
| `ExchangeRateProvider()` | `get_rate(source, target)` | `app/domain/providers.py` |
| `TableRateProvider(rates)` | `get_rate(source, target)` | `app/domain/providers.py` |
| `FixedRateProvider(exchange_rate)` | `get_rate(source, target)` | `app/domain/providers.py` |

Свойства читаются без скобок. Поля объекта-значения не меняются присваиванием; результат операции создаётся отдельно. Для наследника без собственного конструктора показаны аргументы конструктора базового класса.

## Вызов сервиса

| Метод | Сигнатура |
|---|---|
| `__init__` | `FxService(provider)` |
| `convert` | `convert(amount, target_currency)` |
| `convert_many` | `convert_many(amount, target_currencies)` |
| `available_quotes` | `available_quotes(amount, target_currencies)` |

`app/api.py` — готовая внешняя граница; не изменяйте её. Вызов попадает в сервис из указанного модуля. Подробные примеры создания входных объектов находятся в открытых тестах текущей папки.

В `app/services/assembly.py` находятся стандартные конфигурации. Переданный объект сохраняется, а отсутствие обозначается `None`. Пустой список или словарь не равен отсутствию настройки. Копия контейнера не означает копирования исполнителей.

Сигнатура сборки: `build_service(provider=None, rates=None)`.

## Готовые результаты и ошибки

`DomainError` находится в `app/support/errors.py`; код доступен через `error.code`. В разрешённых методах используйте готовые проверки, а не новую иерархию исключений.

`Money` хранит `Decimal` и валюту. Для учебных данных используются EUR и USD. Заданная сумма создаётся готовой `money("10", "EUR")`; арифметика выполняется готовыми методами Money. Курс и коэффициент не округляются как денежная сумма. В Account денежный модуль — `app/domain/money.py`, в остальных вариантах он предоставлен в `app/support/`.

## Проверка поведения

`tests/test_contract.py` и `tests/test_review_contract.py` проверяют предметные правила. `tests/test_progression.py` проверяет последовательности обращений и настройки текущей работы. Ни один результат теста не является командой менять защищённый API или тесты.

Ожидаемый стартовый результат — в [STARTER-STATE.md](STARTER-STATE.md). Проверка из корня проекта: `python check.py lab05`.
