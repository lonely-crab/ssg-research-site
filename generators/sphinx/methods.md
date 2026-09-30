# Методика

(data-collection)=
## Сбор замеров

Нагрузку поднимал ступеньками по RPS. В csv — среднее latency_ms и ошибки.

(processing)=
## Обработка

`scripts/run_experiment.py` считает МНК и пишет графики в `docs/generated/`.
Кэш срабатывает, если csv и скрипт не менялись.
