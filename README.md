# Practical Toolkit

Полезная коллекция инструментов на Python для повседневных задач.

## Что внутри

| Инструмент | Описание |
|----------|----------|
| `file_organizer.py` | Умная сортировка файлов по типу, дате и размеру |
| `bulk_rename.py` | Массовое переименование файлов с превью |
| `disk_cleaner.py` | Поиск и удаление мусора (дубликаты, временные файлы, большие логи) |
| `quick_serve.py` | Мгновенный HTTP-сервер с красивым листингом директорий |
| `system_info.py` | Красивый отчёт о системе |

## Быстрый старт

```bash
git clone https://github.com/fima4335/practical-toolkit.git
cd practical-toolkit
pip install -r requirements.txt
```

### Примеры использования

**Организовать папку Downloads:**
```bash
python file_organizer.py ~/Downloads --by type --dry-run
```

**Найти дубликаты:**
```bash
python disk_cleaner.py --find-duplicates ~/Documents
```

**Быстрый сервер:**
```bash
python quick_serve.py .
```

## Требования

- Python 3.10+
- Зависимости указаны в `requirements.txt`

---

Сделано с заботой. Можно форкать и улучшать.
