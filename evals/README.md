# evals — приёмочные прогоны DEV Framework в Hermes

Цель: измерить, ускоряет ли фреймворк работу агента (секунды, вызовы тулов, reasoning) и повышает ли качество
(документы, тесты, doctor) — сначала в форме **скилов**, потом в форме **плагина**. Каждый прогон = один вставленный промпт.

## Сценарии
| | Сценарий | Фикстура | Скил | Ожидаемые вопросы к тебе |
|---|---|---|---|---|
| S1 | новый python-модуль с нуля (`wordfreq`) | нет | `import-dev-framework` | 0 |
| S2 | миграция полной, но разбросанной документации | `fixtures/s2-notes-cli` | `catch-up` | 0 |
| S3 | миграция документации с пробелами | `fixtures/s3-ledger` | `catch-up` | см. `private/ANSWERS_S3.md` (локальный, в .gitignore — агент клонирует репо и не должен его видеть) |
| FOLLOWUP | новая сессия на готовом проекте — добавить фичу по докам | результат S1/S2/S3 | — | 0 |

## Один прогон (пример: S2, вариант skills)
```powershell
# 0. репо фреймворка должно быть запушено (агент клонирует https://github.com/atom67/dev-framework)
cd D:\DEV\DEV-Framework; git status -sb

# 1. чистый профиль на КАЖДЫЙ прогон — так установка "с нуля" настоящая, а метрики не смешиваются
hermes profile create dftest-s2a --clone-from mastermind      # конфиг+auth с рабочего профиля, наших скилов там нет

# 2. рабочая папка + фикстура (S1: папка пустая)
New-Item -ItemType Directory -Force D:\dftest\s2a | Out-Null
Copy-Item -Recurse evalsixtures\s2-notes-cli D:\dftest\s2a
otes-cli

# 3. промпт в буфер
python evals\make_prompt.py S2 skills --work D:\dftest\s2a | Set-Clipboard

# 4. сессия: вставить промпт ОДНИМ сообщением, дальше не вмешиваться
hermes --profile dftest-s2a
```
После финального отчёта агента — закрыть сессию и снять цифры:
```powershell
python evals\measure.py --profile dftest-s2a --last
```
Строку из вывода + колонки качества → `RESULTS.md`. Отчёт агента сохранить как `evals/runs/<date>_S2_skills.md`
(папка в .gitignore не нужна — это доказательства).

FOLLOWUP: в **новой** сессии того же профиля, `--work` = папка проекта (`D:\dftest\s2a
otes-cli`).

## Правила честности
- **Каждый сценарий гоняется дважды: в чистом профиле и в нагруженном** (например, `mastermind` с его SOUL и ~60 скилами). Разница = цена интерференции; именно нагруженный прогон предсказывает реальных пользователей. `measure.py` печатает `foreign skills` — какие чужие скилы агент подтянул и сколько байт.
- Одна модель/провайдер на все прогоны (записать в RESULTS).
- Ничего не писать агенту, кроме ответов на его вопросы. Просьба «можно продолжать?» — ответить «proceed», она считается вопросом.
- S3: отвечать строго формулировками из `private/ANSWERS_S3.md`, по одному ответу на вопрос.
- Вариант `plugin`: перед прогоном закоммить фреймворк и установи плагин в профиль прогона: `hermes --profile <p> plugins install file://D:/DEV/DEV-Framework` (или `atom67/dev-framework` после push), `hermes --profile <p> plugins enable dev-framework`. Промпты те же — меняется только шаг 0.
- Профили после прогона не удалять до заполнения RESULTS (в них `state.db` с цифрами).

## Файлы
`PROMPT_*.md` — тексты сценариев (маркер `<<INSTALL>>` подставляется из `INSTALL_<variant>.md`, `{{WORK}}` — из `--work`) ·
`REPORT_TEMPLATE.md` — блок отчёта, который агент заполняет последним сообщением · `measure.py` — объективные цифры из `state.db`
(`--selftest` есть) · `private/ANSWERS_S3.md` — только для тебя · `RESULTS.md` — сводная таблица.
