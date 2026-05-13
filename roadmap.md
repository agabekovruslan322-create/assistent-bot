# SYNORA — ROADMAP

## 🟢 ЭТАП 1: ФУНДАМЕНТ (БАЗА)

### Статус: Почти завершён

### Backend / Core

* [x] Telegram-бот на Python
* [x] Async handlers (`python-telegram-bot`)
* [x] Главное меню
* [x] Callback buttons
* [x] ConversationHandler
* [x] PostgreSQL на Railway
* [x] Работа с SQL
* [x] Разделение проекта на файлы

### Security / Infrastructure

* [x] `.env`
* [x] `.gitignore`
* [x] Скрытие токенов
* [x] Очистка Git history
* [x] `requirements.txt`
* [x] Deploy

### Architecture Cleanup

* [x] Удаление глобального `handle_message`
* [x] Начало нормального Access Control
* [x] `require_vow()`
* [x] Полностью встроить `require_vow()` во все handlers
* [x] Почистить лишние imports
* [x] Перейти с `print()` на `logging`
* [x] Нормализовать структуру проекта

---

# 🟡 ЭТАП 2: УМНАЯ ДИСЦИПЛИНА

### Статус: Текущий этап

## Goals System

* [x] Создание целей
* [x] История
* [x] Статистика
* [x] Выполнение задач
* [x] Удаление задач

## Smart Entry

* [x] Система клятвы
* [x] Фиксация пользователя в БД

## Parsing

* [x] Regex для времени
* [ ] Нормальная валидация времени
* [ ] Parsing "Йога 19:30"
* [ ] Автоматическое извлечение времени задачи

## Reliability

* [ ] Починить flow ConversationHandler
* [ ] Убрать баги двойного нажатия
* [ ] Нормализовать states
* [ ] Сделать cleaner handler architecture

## Database Cleanup

* [ ] Context manager для БД
* [ ] Убрать повторяющийся connect()
* [ ] Добавить indexes
* [ ] Перейти с TEXT date на TIMESTAMP
* [ ] Нормализовать SQL layer

---

# 🟠 ЭТАП 3: МАЯКИ И СУДНЫЙ ВЕЧЕР

## Smart Reminders

* [ ] Автоматические уведомления
* [ ] Напоминания по времени задачи
* [ ] Scheduler logic
* [ ] Job queue architecture

## Судный Вечер

* [ ] Проверка невыполненных задач
* [ ] Давление на дисциплину
* [ ] Daily summary
* [ ] User-specific judgement time

## Архивация

* [ ] Статус "Провалено"
* [ ] Авто-перенос в историю
* [ ] Daily archive system

---

# 🔴 ЭТАП 4: ПСИХОЛОГИЯ И ПРИВЯЗАННОСТЬ

## Psychological Layer

* [ ] Глубокие вопросы
* [ ] Reflection system
* [ ] "Почему ты это делаешь?"
* [ ] Эффект давления/осознания

## Gamification

* [ ] Уровни
* [ ] Ранги
* [ ] Reputation system
* [ ] Discipline score

## BINARY Analytics

* [ ] Визуализация прогресса
* [ ] Графики
* [ ] Time investment tracking
* [ ] Аналитика привычек

---

# 🔵 ЭТАП 5: ЭКОСИСТЕМА

## Brand

* [ ] Запуск бренда одежды
* [ ] BINARY identity
* [ ] Интеграция Synora + merch
* [ ] Closed club system

## Advanced AI

* [ ] AI-анализ целей
* [ ] AI-рекомендации
* [ ] Personal mentor logic
* [ ] Поведенческий анализ

## Scaling

* [ ] Docker
* [ ] Redis
* [ ] Async PostgreSQL
* [ ] SQLAlchemy
* [ ] Migrations
* [ ] Production architecture

---

# 🧠 ПАРАЛЛЕЛЬНЫЙ SECURITY / REVERSE ROADMAP

## Python / Backend

* [ ] Углубление Python
* [ ] Asyncio
* [ ] Architecture
* [ ] APIs
* [ ] Automation tools

## Low-Level

* [ ] C basics
* [ ] Memory
* [ ] Stack / Heap
* [ ] Registers
* [ ] Calling conventions

## Reverse Engineering

* [ ] x86/x64 Assembly
* [ ] PE structure
* [ ] x64dbg
* [ ] IDA basics
* [ ] Static analysis
* [ ] Dynamic analysis

## Malware Analysis

* [ ] Windows internals
* [ ] Procmon
* [ ] Wireshark
* [ ] Registry
* [ ] Process injection theory
* [ ] Persistence techniques

## Long-Term Goal

* [ ] Kaspersky Academy
* [ ] Security portfolio
* [ ] Reverse engineering specialization
* [ ] International cybersecurity career
* [ ] Переезд в Miami

---

# ГЛАВНАЯ ИДЕЯ ПРОЕКТА

Synora / BINARY — это не просто Telegram-бот.

Это:

* система дисциплины;
* digital identity;
* cyber/self-improvement ecosystem;
* сочетание:

  * programming,
  * psychology,
  * discipline,
  * branding,
  * security mindset.

---

# ГЛАВНОЕ ПРАВИЛО

Не спешить.

Цель:
не "выучить всё быстро",
а:

* строить;
* понимать;
* улучшать;
* становиться сильнее каждый месяц.

Горизонт: 3–5 лет.
