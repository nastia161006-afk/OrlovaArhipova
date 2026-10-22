# Исходные проверки ЛР3

Успешных проверок: **5**. Ожидаемых падений: **13**.

Не завершены общий интерфейс, алгоритмы исполнителей и основной метод сервиса. Поэтому один незаполненный метод может вызвать несколько падений — это не несколько независимых задач.

Падения ниже связаны с конкретными требованиями [TASK.md](TASK.md). После обязательной части все они должны пройти. Бонус проверяется отдельно и не входит в эти числа.

## Новые последовательности и конфигурации

- `tests.test_progression::test_progression_conversion_does_not_change_amount`
- `tests.test_progression::test_progression_provider_success_missing_success[<lambda>]`
- `tests.test_progression::test_progression_provider_success_missing_success[FixedRateProvider]`

## Предметный контракт и общий интерфейс

- `tests.test_contract::test_abc_is_abstract`
- `tests.test_contract::test_conversion[0-0]`
- `tests.test_contract::test_conversion[10-8.50]`
- `tests.test_contract::test_conversion[100-85]`
- `tests.test_contract::test_half_up_rounding_of_result_only`
- `tests.test_contract::test_identity_and_missing_rate`
- `tests.test_contract::test_table_and_fixed_contract`
- `tests.test_contract::test_two_tables_do_not_affect_each_other`
- `tests.test_review_contract::test_review_rate_precision_not_money_precision`
- `tests.test_review_contract::test_review_service_uses_provider_in_lab3`

## Порядок проверки

Из корня проекта: `python check.py lab03`. Сначала прочитайте первый traceback и ожидаемый результат сценария. Не отключайте тесты, которые пока не проходят.

Ошибка импорта или установки не относится к заданию. Если исходный набор результатов отличается, сохраните вывод и сообщите преподавателю; не удаляйте решения и служебные файлы.
