# Discorder — настройка и запуск

## Предварительные требования

- **Python 3.11+** (на Windows: настрой и проверь `Get-Command python` в PowerShell)
- **uv** — установщик/раннер Python-зависимостей
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```
  После установки перезапусти терминал и проверь: `uv --version`
- **FFmpeg** — для воспроизведения TTS в голосовом канале
  ```powershell
  winget install ffmpeg
  ```
  Проверь: `ffmpeg -version`
- **opus** — декодер аудиопотока Discord (ставится автоматически с зависимостями)

---

## 1. Создание бота в Discord Developer Portal

1. Открой [Discord Developer Portal](https://discord.com/developers/applications).
2. Нажми **New Application**, введи имя (например, `Discorder`), создай.
3. Слева перейди в **Bot**.
4. Нажми **Reset Token** и скопируй токен (понадобится для `.env`).
5. Включи **Privileged Gateway Intents**:
   - ✅ Message Content Intent
6. Сохрани изменения.

---

## 2. Приглашение бота на сервер

1. Слева перейди в **OAuth2** → **URL Generator**.
2. В **Scopes** отметь:
   - `bot`
   - `applications.commands`
3. В **Bot Permissions** отметь:
   - `Send Messages`
   - `Connect`
   - `Speak`
   - `Use Voice Activity`
4. Скопируй сгенерированный URL внизу, открой в браузере и выбери сервер.

---

## 3. API-ключ DeepSeek

1. Зарегистрируйся на [platform.deepseek.com](https://platform.deepseek.com).
2. Перейди в **API Keys**, создай новый ключ и скопируй его.

---

## 4. Конфигурация

1. Скопируй `.env.example` → `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Открой `.env` и заполни:
   ```
   DISCORD_TOKEN=MTIzNDU2Nzg5...    # токен из шага 1
   DEEPSEEK_API_KEY=sk-...           # ключ из шага 3
   ```
   Остальные настройки можно оставить по умолчанию.

### Доступные переменные

| Переменная         | По умолчанию              | Описание                            |
|---------------------|---------------------------|--------------------------------------|
| `DISCORD_TOKEN`     | *обязательно*             | Токен бота                         |
| `DEEPSEEK_API_KEY`  | *обязательно*             | API-ключ DeepSeek                  |
| `BOT_NAME`          | `discorder`               | Имя бота                           |
| `WAKE_WORDS`        | `discorder,дискордер,бот` | Ключевые слова (через запятую)     |
| `WHISPER_MODEL`     | `large-v3`                | Модель faster-whisper              |
| `WHISPER_DEVICE`    | `cuda`                    | Устройство: `cpu` или `cuda`       |
| `WHISPER_COMPUTE_TYPE` | `float16`             | Тип вычислений: `float16`, `int8_float16`, `float32` |
| `TTS_VOICE`         | `ru-RU-DariyaNeural`      | Голос edge-tts                     |
| `LLM_MODEL`         | `deepseek_v4_flash`       | Модель DeepSeek                    |

---

## 5. Запуск

```powershell
uv run main.py
```

> При **первом** запуске faster-whisper скачает модель `large-v3` (~3 ГБ). Это занимает пару минут. Последующие запуски будут мгновенными.

После запуска бот появится онлайн в Discord.

---

## 6. Использование

В любом текстовом канале сервера:

- `/join` — подключиться к твоему голосовому каналу
- `/join channel:#название` — подключиться к конкретному голосовому каналу
- `/leave` — отключиться

Бот слушает голосовой канал и реагирует, когда произносят ключевое слово (`discorder`, `дискордер`, `бот`).

---

## Устранение неполадок

| Проблема                            | Решение                                                     |
|--------------------------------------|-------------------------------------------------------------|
| `DISCORD_TOKEN not set`              | Создай `.env` из `.env.example` и заполни `DISCORD_TOKEN`   |
| `DEEPSEEK_API_KEY not set`           | Заполни `DEEPSEEK_API_KEY` в `.env`                        |
| Бот не слышит / не отвечает в войсе  | Убедись что `ffmpeg` установлен и доступен из PATH          |
| Транскрипция пустая                  | Проверь микрофон и громкость в Discord                     |
| `CUDA out of memory`                 | Поставь `WHISPER_DEVICE=cpu` в `.env`                      |
