# Исходные проверки ЛР5

Успешных проверок: **9**. Ожидаемых падений: **14**.

Не завершены использование переданных зависимостей, сборка и основной путь операции. Проверки вызывают разные конфигурации и ошибающегося исполнителя; ошибка не должна превращаться в успешный результат или повторную операцию.

Падения ниже связаны с конкретными требованиями [TASK.md](TASK.md). После обязательной части все они должны пройти. Бонус проверяется отдельно и не входит в эти числа.

## Новые последовательности и конфигурации

- `tests.test_progression::test_progression_conversion_does_not_change_amount`
- `tests.test_progression::test_progression_extra_lab05`
- `tests.test_progression::test_progression_false_provider_error_then_success`

## Предметный контракт и общий интерфейс

- `tests.test_contract::test_conversion[0-0]`
- `tests.test_contract::test_conversion[10-8.50]`
- `tests.test_contract::test_conversion[100-85]`
- `tests.test_contract::test_half_up_rounding_of_result_only`
- `tests.test_contract::test_identity_and_missing_rate`
- `tests.test_contract::test_injected_provider_and_identity_without_calls`
- `tests.test_contract::test_provider_errors_and_wrong_pair`
- `tests.test_contract::test_table_is_a_snapshot`
- `tests.test_contract::test_two_tables_do_not_affect_each_other`
- `tests.test_review_contract::test_review_none_is_not_a_valid_rate`
- `tests.test_review_contract::test_review_rate_precision_not_money_precision`

## Порядок проверки

Из корня проекта: `python check.py lab05`. Сначала прочитайте первый traceback и ожидаемый результат сценария. Не отключайте тесты, которые пока не проходят.

Ошибка импорта или установки не относится к заданию. Если исходный набор результатов отличается, сохраните вывод и сообщите преподавателю; не удаляйте решения и служебные файлы.
