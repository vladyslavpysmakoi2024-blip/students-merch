# Інструкція з роботи з Alembic

## Що таке Alembic?

Alembic — це інструмент для управління версіями схеми бази даних в Python. Він дозволяє:
- Відстежувати зміни структури БД
- Створювати міграції (scripts) для оновлення БД
- Откатувати зміни до попередніх версій
- Синхронізувати схему БД між різними оточеннями

---

## 1. Установка та ініціалізація

### 1.1 Встановлення пакету

```bash
pip install alembic
```

### 1.2 Ініціалізація проекту

У корневій папці проекту виконайте:

```bash
alembic init alembic
```

Це створить папку `alembic/` з структурою:
```
alembic/
├── versions/          # Папка з файлами міграцій
├── env.py            # Конфігурація оточення
├── script.py.mako    # Шаблон для нових міграцій
└── alembic.ini       # Основний файл конфігурації
```

### 1.3 Конфігурація

Відредагуйте `alembic.ini`:

```ini
# Рядок з'єднання з БД
sqlalchemy.url = postgresql://user:password@localhost:5432/dbname

# Для розробки можна використовувати змінні оточення
sqlalchemy.url = driver://%(DB_USER)s:%(DB_PASSWORD)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s
```

Або в `env.py` встановіть конфігурацію динамічно:
```python
import os
from sqlalchemy import engine_from_config, pool

# Отримуємо URL з змінної оточення
database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
config.set_main_option("sqlalchemy.url", database_url)
```

---

## 2. Основні команди

### 2.1 Перегляд поточної версії

```bash
alembic current
```

Показує, на якій міграції зараз база даних.

### 2.2 Перегляд історії міграцій

```bash
alembic history --oneline
```

Виведе список всіх міграцій.

### 2.3 Перегляд статусу

```bash
alembic branches
```

Показує гілки міграцій (якщо вони розходилися).

---

## 3. Робота з міграціями

### 3.1 Створення нової міграції (автоматична)

Якщо ви використовуєте SQLAlchemy ORM моделі:

```bash
alembic revision --autogenerate -m "Add user table"
```

Alembic автоматично порівняє вашу модель з поточною схемою БД і створить міграцію.

### 3.2 Створення пустої міграції (вручну)

```bash
alembic revision -m "Create users table"
```

Це створить порожній файл, який потрібно заповнити вручну.

### 3.3 Редагування міграції

Файли міграцій розташовані в `alembic/versions/`. Кожен файл має функції:
- `upgrade()` — що робити при застосуванні міграції
- `downgrade()` — як откатити міграцію

Приклад:

```python
"""Create users table

Revision ID: abc123def456
Revises:
Create Date: 2024-01-15 10:30:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "abc123def456"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"])


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
```

### 3.4 Застосування міграцій

```bash
# Застосувати всі нові міграції
alembic upgrade head

# Застосувати N міграцій
alembic upgrade +2

# Застосувати до конкретної міграції
alembic upgrade abc123def456
```

### 3.5 Відкат міграцій

```bash
# Відкат на 1 версію назад
alembic downgrade -1

# Відкат на 2 версії назад
alembic downgrade -2

# Відкат до конкретної міграції
alembic downgrade abc123def456
```

---

## 4. Кращі практики для команди

### 4.1 Назви файлів міграцій

Використовуйте описові назви на англійійській мові:
```
✅ 2024_01_15_001_create_users_table.py
✅ 2024_01_15_002_add_email_column_to_users.py
❌ migration1.py
❌ update.py
```

### 4.2 Структура коміту

```bash
git add alembic/versions/XXXX_*.py
git commit -m "Migration: Add user authentication fields"
```

Тримайте міграції в окремому коміті від оновлення коду.

### 4.3 Правила для команди

1. **Ніколи не редагуйте** уже застосовані міграції
2. **Кожна міграція** повинна мати як `upgrade()`, так і `downgrade()`
3. **Тестуйте** обидві операції перед коммітом
4. **Синхронізуйтеся** з основною гілкою перед створенням нової міграції
5. **Документуйте** складні міграції коментарями

### 4.4 Конвенція для роботи з декількома розробниками

Якщо у вас розходяться міграції:

```bash
# Перегляньте гілки
alembic branches

# Об'єднайте зміни (встановіть залежність)
# У новій міграції встановіть down_revision на останню спільну версію
# та залежність на другу гілку
```

---

## 5. Практичні приклади

### 5.1 Додавання колони до таблиці

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(20)))


def downgrade() -> None:
    op.drop_column("users", "phone")
```

### 5.2 Створення індексу

```python
def upgrade() -> None:
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
```

### 5.3 Зміна типу колони

```python
def upgrade() -> None:
    op.alter_column("users", "age", existing_type=sa.Integer(), type_=sa.String(50))


def downgrade() -> None:
    op.alter_column("users", "age", existing_type=sa.String(50), type_=sa.Integer())
```

### 5.4 Дата-міграція (заповнення даних)

```python
def upgrade() -> None:
    # Додаємо колону
    op.add_column("posts", sa.Column("status", sa.String(20), nullable=True))

    # Оновлюємо існуючі дані
    op.execute("UPDATE posts SET status = 'published' WHERE created_at IS NOT NULL")

    # Встановлюємо NOT NULL
    op.alter_column("posts", "status", nullable=False)


def downgrade() -> None:
    op.drop_column("posts", "status")
```

---

## 6. Робота з різними оточеннями

### 6.1 Конфігурація для dev/staging/prod

Творіть різні файли конфігурації або використовуйте змінні оточення:

```bash
# Development
export DATABASE_URL="postgresql://user:pass@localhost/dev_db"
alembic upgrade head

# Production
export DATABASE_URL="postgresql://user:pass@prod-server/prod_db"
alembic upgrade head
```

### 6.2 Перевірка перед розгортанням

```bash
# Переглядаємо, які міграції будуть застосовані
alembic upgrade head --sql

# Це покаже SQL без його виконання
```

---

## 7. Розв'язання проблем

### 7.1 "Can't locate revision identified by 'XXX'"

**Проблема**: Міграція не знайдена.

**Розв'язок**:
```bash
# Переконайтеся, що файл існує в alembic/versions/
ls alembic/versions/

# Перевірте поточний revision
alembic current
```

### 7.2 Конфлікт міграцій у git

Якщо у вас розходяться міграції:

```bash
# 1. Оновіть до останньої версії з main
git fetch origin
git merge origin/main

# 2. Перегляньте стан
alembic current
alembic history --oneline

# 3. Створіть нову міграцію, яка вирішує конфлікт
alembic revision -m "Resolve migration conflict"
```

### 7.3 "ERROR: Can't find migration for the specified branch label"

Перевірте залежності міграцій у файлі:
```python
down_revision = "correct_previous_migration_id"
```

### 7.4 Відновлення після помилки

```bash
# Откатіться до стабільної версії
alembic downgrade -N

# Перевірте стан БД
alembic current

# Виправте проблему та спробуйте знову
```

---

## 8. Інтеграція з CI/CD

### 8.1 GitHub Actions приклад

```yaml
name: Database Migration

on: [push]

jobs:
  migrate:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: test_db

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:password@localhost:5432/test_db
        run: |
          alembic upgrade head
```

### 8.2 Валідація міграцій

```bash
# Перед деплоєм перевірте синтаксис
alembic upgrade head --sql > migrations.sql

# Переглядаємо SQL перед виконанням
cat migrations.sql
```

---

## 9. Корисні ресурси

- [Офіційна документація Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Types](https://docs.sqlalchemy.org/en/20/core/types.html)
- [Alembic API Reference](https://alembic.sqlalchemy.org/en/latest/api/operations.html)

---