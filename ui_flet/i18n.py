"""
Internationalization (i18n) module for the Restaurant Management System.

Provides translations for Bulgarian (default), English, French, and Russian.
"""

import json
import os
from typing import Dict, Optional

# Language codes and their display labels
# Using text labels for clarity (EN instead of GB flag for English)
LANGUAGES = {
    "bg": "🇧🇬",  # Bulgarian
    "en": "EN",   # English (using text as there's no EN flag)
    "fr": "🇫🇷",  # French
    "ru": "🇷🇺",  # Russian
}

# Default language
DEFAULT_LANGUAGE = "bg"

# Settings file path for persistence
SETTINGS_FILE = "settings.json"


# ==========================================
# Translations Dictionary
# ==========================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App title
    "app_title": {
        "bg": "Ресторант Хъшове",
        "en": "Restaurant Hashove",
        "fr": "Restaurant Hachové",
        "ru": "Ресторан Хъшове",
    },
    
    # Navigation / Screens
    "reservations": {
        "bg": "Резервации",
        "en": "Reservations",
        "fr": "Réservations",
        "ru": "Резервации",
    },
    "table_layout": {
        "bg": "Разпределение на масите",
        "en": "Table Layout",
        "fr": "Disposition des tables",
        "ru": "Расположение столов",
    },
    "admin_panel": {
        "bg": "Администраторски панел",
        "en": "Admin Panel",
        "fr": "Panneau d'administration",
        "ru": "Панель администратора",
    },
    
    # Admin Login
    "admin_login": {
        "bg": "Вход за администратор",
        "en": "Administrator Login",
        "fr": "Connexion administrateur",
        "ru": "Вход администратора",
    },
    "username": {
        "bg": "Потребителско име",
        "en": "Username",
        "fr": "Nom d'utilisateur",
        "ru": "Имя пользователя",
    },
    "password": {
        "bg": "Парола",
        "en": "Password",
        "fr": "Mot de passe",
        "ru": "Пароль",
    },
    "login": {
        "bg": "Вход",
        "en": "Login",
        "fr": "Connexion",
        "ru": "Войти",
    },
    "cancel": {
        "bg": "Отказ",
        "en": "Cancel",
        "fr": "Annuler",
        "ru": "Отмена",
    },
    "welcome_admin": {
        "bg": "Добре дошли, Администратор!",
        "en": "Welcome, Administrator!",
        "fr": "Bienvenue, Administrateur!",
        "ru": "Добро пожаловать, Администратор!",
    },
    "invalid_credentials": {
        "bg": "Невалидни администраторски данни",
        "en": "Invalid administrator credentials",
        "fr": "Identifiants administrateur invalides",
        "ru": "Неверные данные администратора",
    },
    "logout_admin": {
        "bg": "Изход от админ режим",
        "en": "Exit admin mode",
        "fr": "Quitter le mode admin",
        "ru": "Выйти из режима администратора",
    },
    "admin": {
        "bg": "Админ",
        "en": "Admin",
        "fr": "Admin",
        "ru": "Админ",
    },
    
    # Admin Tabs
    "waiters": {
        "bg": "Сервитьори",
        "en": "Waiters",
        "fr": "Serveurs",
        "ru": "Официанты",
    },
    "sections": {
        "bg": "Секции",
        "en": "Sections",
        "fr": "Sections",
        "ru": "Секции",
    },
    "tables": {
        "bg": "Маси",
        "en": "Tables",
        "fr": "Tables",
        "ru": "Столы",
    },
    "backup": {
        "bg": "Архивиране",
        "en": "Backup",
        "fr": "Sauvegarde",
        "ru": "Резервное копирование",
    },
    "reports": {
        "bg": "Отчети",
        "en": "Reports",
        "fr": "Rapports",
        "ru": "Отчеты",
    },
    
    # Waiters Management
    "new_waiter": {
        "bg": "Нов сервитьор",
        "en": "New Waiter",
        "fr": "Nouveau serveur",
        "ru": "Новый официант",
    },
    "manage_waiters_desc": {
        "bg": "Управлявайте сервитьорите на ресторанта.",
        "en": "Manage the restaurant's waiters.",
        "fr": "Gérez les serveurs du restaurant.",
        "ru": "Управляйте официантами ресторана.",
    },
    "waiter_name": {
        "bg": "Име на сервитьор",
        "en": "Waiter Name",
        "fr": "Nom du serveur",
        "ru": "Имя официанта",
    },
    "create_waiter": {
        "bg": "Създай сервитьор",
        "en": "Create Waiter",
        "fr": "Créer un serveur",
        "ru": "Создать официанта",
    },
    "edit_waiter": {
        "bg": "Редактирай сервитьор",
        "en": "Edit Waiter",
        "fr": "Modifier le serveur",
        "ru": "Редактировать официанта",
    },
    "delete_waiter": {
        "bg": "Изтрий сервитьор",
        "en": "Delete Waiter",
        "fr": "Supprimer le serveur",
        "ru": "Удалить официанта",
    },
    "delete_waiter_confirm": {
        "bg": "Сигурни ли сте, че искате да изтриете този сервитьор?",
        "en": "Are you sure you want to delete this waiter?",
        "fr": "Êtes-vous sûr de vouloir supprimer ce serveur?",
        "ru": "Вы уверены, что хотите удалить этого официанта?",
    },
    
    # Sections Management
    "new_section": {
        "bg": "Нова секция",
        "en": "New Section",
        "fr": "Nouvelle section",
        "ru": "Новая секция",
    },
    "sections_desc": {
        "bg": "Секциите групират масите в зони.",
        "en": "Sections group tables into zones.",
        "fr": "Les sections regroupent les tables en zones.",
        "ru": "Секции группируют столы в зоны.",
    },
    "section_name": {
        "bg": "Име на секция",
        "en": "Section Name",
        "fr": "Nom de la section",
        "ru": "Название секции",
    },
    "no_tables": {
        "bg": "Няма маси",
        "en": "No tables",
        "fr": "Pas de tables",
        "ru": "Нет столов",
    },
    "rename": {
        "bg": "Преименувай",
        "en": "Rename",
        "fr": "Renommer",
        "ru": "Переименовать",
    },
    "change_tables": {
        "bg": "Промени маси",
        "en": "Change Tables",
        "fr": "Changer les tables",
        "ru": "Изменить столы",
    },
    "select_tables_for_section": {
        "bg": "Изберете маси за секцията",
        "en": "Select tables for section",
        "fr": "Sélectionner les tables pour la section",
        "ru": "Выберите столы для секции",
    },
    "create_section": {
        "bg": "Създай секция",
        "en": "Create Section",
        "fr": "Créer une section",
        "ru": "Создать секцию",
    },
    "edit_section": {
        "bg": "Редактирай секция",
        "en": "Edit Section",
        "fr": "Modifier la section",
        "ru": "Редактировать секцию",
    },
    "delete_section": {
        "bg": "Изтрий секция",
        "en": "Delete Section",
        "fr": "Supprimer la section",
        "ru": "Удалить секцию",
    },
    "delete_section_confirm": {
        "bg": "Сигурни ли сте, че искате да изтриете тази секция?",
        "en": "Are you sure you want to delete this section?",
        "fr": "Êtes-vous sûr de vouloir supprimer cette section?",
        "ru": "Вы уверены, что хотите удалить эту секцию?",
    },
    
    # Tables Management
    "add_table": {
        "bg": "Добави маса",
        "en": "Add Table",
        "fr": "Ajouter une table",
        "ru": "Добавить стол",
    },
    "manage_tables_desc": {
        "bg": "Управлявайте масите и техните форми.",
        "en": "Manage tables and their shapes.",
        "fr": "Gérez les tables et leurs formes.",
        "ru": "Управляйте столами и их формами.",
    },
    "table_number": {
        "bg": "Номер на маса",
        "en": "Table Number",
        "fr": "Numéro de table",
        "ru": "Номер стола",
    },
    "table_shape": {
        "bg": "Форма на маса",
        "en": "Table Shape",
        "fr": "Forme de la table",
        "ru": "Форма стола",
    },
    "shape_square": {
        "bg": "Квадратна",
        "en": "Square",
        "fr": "Carré",
        "ru": "Квадратный",
    },
    "shape_rectangle": {
        "bg": "Правоъгълна",
        "en": "Rectangle",
        "fr": "Rectangle",
        "ru": "Прямоугольный",
    },
    "shape_round": {
        "bg": "Кръгла",
        "en": "Round",
        "fr": "Rond",
        "ru": "Круглый",
    },
    "change_shape": {
        "bg": "Промени форма",
        "en": "Change Shape",
        "fr": "Changer la forme",
        "ru": "Изменить форму",
    },
    "create_table": {
        "bg": "Създай маса",
        "en": "Create Table",
        "fr": "Créer une table",
        "ru": "Создать стол",
    },
    "edit_table": {
        "bg": "Редактирай маса",
        "en": "Edit Table",
        "fr": "Modifier la table",
        "ru": "Редактировать стол",
    },
    "delete_table": {
        "bg": "Изтрий маса",
        "en": "Delete Table",
        "fr": "Supprimer la table",
        "ru": "Удалить стол",
    },
    "delete_table_confirm": {
        "bg": "Сигурни ли сте, че искате да изтриете тази маса?",
        "en": "Are you sure you want to delete this table?",
        "fr": "Êtes-vous sûr de vouloir supprimer cette table?",
        "ru": "Вы уверены, что хотите удалить этот стол?",
    },
    
    # Backup Management
    "backup_database": {
        "bg": "Архивирай базата",
        "en": "Backup Database",
        "fr": "Sauvegarder la base",
        "ru": "Создать резервную копию",
    },
    "backup_desc": {
        "bg": "Създавайте и възстановявайте архиви на базата данни.",
        "en": "Create and restore database backups.",
        "fr": "Créez et restaurez des sauvegardes de base de données.",
        "ru": "Создавайте и восстанавливайте резервные копии базы данных.",
    },
    "no_backups": {
        "bg": "Няма налични архиви",
        "en": "No backups available",
        "fr": "Aucune sauvegarde disponible",
        "ru": "Нет доступных резервных копий",
    },
    "size": {
        "bg": "Размер",
        "en": "Size",
        "fr": "Taille",
        "ru": "Размер",
    },
    "restore": {
        "bg": "Възстанови",
        "en": "Restore",
        "fr": "Restaurer",
        "ru": "Восстановить",
    },
    "backup_created": {
        "bg": "Архивът е създаден успешно",
        "en": "Backup created successfully",
        "fr": "Sauvegarde créée avec succès",
        "ru": "Резервная копия создана успешно",
    },
    "backup_error": {
        "bg": "Грешка при създаване на архив",
        "en": "Error creating backup",
        "fr": "Erreur lors de la création de la sauvegarde",
        "ru": "Ошибка при создании резервной копии",
    },
    "delete_backup": {
        "bg": "Изтриване на архив",
        "en": "Delete Backup",
        "fr": "Supprimer la sauvegarde",
        "ru": "Удалить резервную копию",
    },
    "delete_backup_confirm": {
        "bg": "Сигурни ли сте, че искате да изтриете този архив?",
        "en": "Are you sure you want to delete this backup?",
        "fr": "Êtes-vous sûr de vouloir supprimer cette sauvegarde?",
        "ru": "Вы уверены, что хотите удалить эту резервную копию?",
    },
    "restore_backup": {
        "bg": "Възстановяване",
        "en": "Restore Backup",
        "fr": "Restaurer la sauvegarde",
        "ru": "Восстановить резервную копию",
    },
    "restore_warning": {
        "bg": "Това ще върне базата към състояние от избрания архив. Текущите данни ще бъдат заменени!",
        "en": "This will restore the database to the selected backup state. Current data will be replaced!",
        "fr": "Cela restaurera la base de données à l'état de la sauvegarde sélectionnée. Les données actuelles seront remplacées!",
        "ru": "Это восстановит базу данных до состояния выбранной резервной копии. Текущие данные будут заменены!",
    },
    "backup_deleted": {
        "bg": "Архивът е изтрит успешно",
        "en": "Backup deleted successfully",
        "fr": "Sauvegarde supprimée avec succès",
        "ru": "Резервная копия удалена успешно",
    },
    "backup_restored": {
        "bg": "Базата данни е възстановена успешно!",
        "en": "Database restored successfully!",
        "fr": "Base de données restaurée avec succès!",
        "ru": "База данных успешно восстановлена!",
    },
    
    # Reports
    "reports_coming_soon": {
        "bg": "Отчети ще бъдат добавени скоро",
        "en": "Reports coming soon",
        "fr": "Rapports bientôt disponibles",
        "ru": "Отчеты скоро будут добавлены",
    },
    
    # Filters
    "filters": {
        "bg": "Филтри",
        "en": "Filters",
        "fr": "Filtres",
        "ru": "Фильтры",
    },
    "date": {
        "bg": "Дата",
        "en": "Date",
        "fr": "Date",
        "ru": "Дата",
    },
    "hour": {
        "bg": "Час",
        "en": "Hour",
        "fr": "Heure",
        "ru": "Час",
    },
    "minutes": {
        "bg": "Минути",
        "en": "Minutes",
        "fr": "Minutes",
        "ru": "Минуты",
    },
    "status": {
        "bg": "Статус",
        "en": "Status",
        "fr": "Statut",
        "ru": "Статус",
    },
    "table": {
        "bg": "Маса",
        "en": "Table",
        "fr": "Table",
        "ru": "Стол",
    },
    "all": {
        "bg": "Всички",
        "en": "All",
        "fr": "Tous",
        "ru": "Все",
    },
    "reserved": {
        "bg": "Резервирана",
        "en": "Reserved",
        "fr": "Réservé",
        "ru": "Забронировано",
    },
    "cancelled": {
        "bg": "Отменена",
        "en": "Cancelled",
        "fr": "Annulé",
        "ru": "Отменено",
    },
    
    # Reservations
    "create_reservation": {
        "bg": "Създай резервация",
        "en": "Create Reservation",
        "fr": "Créer une réservation",
        "ru": "Создать резервацию",
    },
    "edit_reservation": {
        "bg": "Редактирай резервация",
        "en": "Edit Reservation",
        "fr": "Modifier la réservation",
        "ru": "Редактировать резервацию",
    },
    "delete_reservation": {
        "bg": "Изтрий резервация",
        "en": "Delete Reservation",
        "fr": "Supprimer la réservation",
        "ru": "Удалить резервацию",
    },
    "delete_reservation_confirm": {
        "bg": "Сигурни ли сте, че искате да изтриете тази резервация?",
        "en": "Are you sure you want to delete this reservation?",
        "fr": "Êtes-vous sûr de vouloir supprimer cette réservation?",
        "ru": "Вы уверены, что хотите удалить эту резервацию?",
    },
    "no_reservations": {
        "bg": "Няма резервации за избраните филтри",
        "en": "No reservations for selected filters",
        "fr": "Aucune réservation pour les filtres sélectionnés",
        "ru": "Нет резерваций для выбранных фильтров",
    },
    "time": {
        "bg": "Час",
        "en": "Time",
        "fr": "Heure",
        "ru": "Время",
    },
    "customer": {
        "bg": "Клиент",
        "en": "Customer",
        "fr": "Client",
        "ru": "Клиент",
    },
    "customer_name": {
        "bg": "Име на клиент",
        "en": "Customer Name",
        "fr": "Nom du client",
        "ru": "Имя клиента",
    },
    "phone": {
        "bg": "Телефон",
        "en": "Phone",
        "fr": "Téléphone",
        "ru": "Телефон",
    },
    "waiter": {
        "bg": "Сервитьор",
        "en": "Waiter",
        "fr": "Serveur",
        "ru": "Официант",
    },
    "notes": {
        "bg": "Бележки",
        "en": "Notes",
        "fr": "Notes",
        "ru": "Заметки",
    },
    "select_date": {
        "bg": "Изберете дата",
        "en": "Select date",
        "fr": "Sélectionner une date",
        "ru": "Выберите дату",
    },
    "reservation_created": {
        "bg": "Резервацията е създадена",
        "en": "Reservation created",
        "fr": "Réservation créée",
        "ru": "Резервация создана",
    },
    "reservation_updated": {
        "bg": "Резервацията е обновена",
        "en": "Reservation updated",
        "fr": "Réservation mise à jour",
        "ru": "Резервация обновлена",
    },
    "reservation_cancelled": {
        "bg": "Резервацията е отменена",
        "en": "Reservation cancelled",
        "fr": "Réservation annulée",
        "ru": "Резервация отменена",
    },
    "error_overlap": {
        "bg": "Грешка: Препокриване с друга резервация",
        "en": "Error: Overlaps with another reservation",
        "fr": "Erreur: Chevauche une autre réservation",
        "ru": "Ошибка: Пересечение с другой резервацией",
    },
    
    # Table Layout
    "layout": {
        "bg": "Разпределение",
        "en": "Layout",
        "fr": "Disposition",
        "ru": "Расположение",
    },
    "date_and_time": {
        "bg": "Дата и час",
        "en": "Date and Time",
        "fr": "Date et heure",
        "ru": "Дата и время",
    },
    "section": {
        "bg": "Секция",
        "en": "Section",
        "fr": "Section",
        "ru": "Секция",
    },
    "legend": {
        "bg": "Легенда",
        "en": "Legend",
        "fr": "Légende",
        "ru": "Легенда",
    },
    "free": {
        "bg": "Свободна",
        "en": "Free",
        "fr": "Libre",
        "ru": "Свободно",
    },
    "occupied": {
        "bg": "Заета",
        "en": "Occupied",
        "fr": "Occupé",
        "ru": "Занято",
    },
    "occupied_soon": {
        "bg": "Заета скоро",
        "en": "Occupied Soon",
        "fr": "Bientôt occupé",
        "ru": "Скоро занято",
    },
    "back_to_reservations": {
        "bg": "← Резервации",
        "en": "← Reservations",
        "fr": "← Réservations",
        "ru": "← Резервации",
    },
    "to_layout": {
        "bg": "Разпределение →",
        "en": "Layout →",
        "fr": "Disposition →",
        "ru": "Расположение →",
    },
    "all_days": {
        "bg": "Всички дни",
        "en": "All days",
        "fr": "Tous les jours",
        "ru": "Все дни",
    },
    
    # Common Actions
    "save": {
        "bg": "Запази",
        "en": "Save",
        "fr": "Enregistrer",
        "ru": "Сохранить",
    },
    "delete": {
        "bg": "Изтрий",
        "en": "Delete",
        "fr": "Supprimer",
        "ru": "Удалить",
    },
    "edit": {
        "bg": "Редактирай",
        "en": "Edit",
        "fr": "Modifier",
        "ru": "Редактировать",
    },
    "close": {
        "bg": "Затвори",
        "en": "Close",
        "fr": "Fermer",
        "ru": "Закрыть",
    },
    "error": {
        "bg": "Грешка",
        "en": "Error",
        "fr": "Erreur",
        "ru": "Ошибка",
    },
    "warning": {
        "bg": "ВНИМАНИЕ!",
        "en": "WARNING!",
        "fr": "ATTENTION!",
        "ru": "ВНИМАНИЕ!",
    },
    "action_cannot_be_undone": {
        "bg": "Това действие не може да бъде отменено.",
        "en": "This action cannot be undone.",
        "fr": "Cette action ne peut pas être annulée.",
        "ru": "Это действие нельзя отменить.",
    },
    
    # Validation
    "please_select_table": {
        "bg": "Моля, изберете маса",
        "en": "Please select a table",
        "fr": "Veuillez sélectionner une table",
        "ru": "Пожалуйста, выберите стол",
    },
    "please_select_date": {
        "bg": "Моля, изберете дата",
        "en": "Please select a date",
        "fr": "Veuillez sélectionner une date",
        "ru": "Пожалуйста, выберите дату",
    },
    "please_select_time": {
        "bg": "Моля, изберете час и минути",
        "en": "Please select hour and minutes",
        "fr": "Veuillez sélectionner l'heure et les minutes",
        "ru": "Пожалуйста, выберите час и минуты",
    },
    "please_enter_name": {
        "bg": "Моля, въведете име на клиент",
        "en": "Please enter customer name",
        "fr": "Veuillez entrer le nom du client",
        "ru": "Пожалуйста, введите имя клиента",
    },
    "invalid_date_time": {
        "bg": "Невалидна дата или час",
        "en": "Invalid date or time",
        "fr": "Date ou heure invalide",
        "ru": "Неверная дата или время",
    },
    "name_required": {
        "bg": "Името е задължително",
        "en": "Name is required",
        "fr": "Le nom est requis",
        "ru": "Имя обязательно",
    },
    
    # Reservation Details (read-only panel)
    "reservation_details": {
        "bg": "Детайли за резервацията",
        "en": "Reservation Details",
        "fr": "Détails de la réservation",
        "ru": "Детали резервации",
    },
    "duration": {
        "bg": "Продължителност",
        "en": "Duration",
        "fr": "Durée",
        "ru": "Продолжительность",
    },
    "minutes_abbr": {
        "bg": "мин.",
        "en": "min.",
        "fr": "min.",
        "ru": "мин.",
    },
}

# Month names for each language
MONTH_NAMES = {
    "bg": ["Януари", "Февруари", "Март", "Април", "Май", "Юни",
           "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "fr": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
           "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
    "ru": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
}


class I18n:
    """
    Internationalization manager.
    
    Handles language switching and translation lookups.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_language = cls._instance._load_language()
        return cls._instance
    
    def _load_language(self) -> str:
        """Load saved language from settings file."""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    lang = settings.get('language', DEFAULT_LANGUAGE)
                    if lang in LANGUAGES:
                        return lang
        except Exception:
            pass
        return DEFAULT_LANGUAGE
    
    def _save_language(self):
        """Save current language to settings file."""
        try:
            settings = {}
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            settings['language'] = self._current_language
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    @property
    def current_language(self) -> str:
        """Get current language code."""
        return self._current_language
    
    @current_language.setter
    def current_language(self, lang: str):
        """Set current language and save to settings."""
        if lang in LANGUAGES:
            self._current_language = lang
            self._save_language()
    
    def t(self, key: str) -> str:
        """
        Get translation for a key in current language.
        
        Args:
            key: Translation key
            
        Returns:
            Translated string, or key if not found
        """
        if key in TRANSLATIONS:
            return TRANSLATIONS[key].get(self._current_language, TRANSLATIONS[key].get(DEFAULT_LANGUAGE, key))
        return key
    
    def get_flag(self, lang: Optional[str] = None) -> str:
        """Get flag emoji for a language."""
        if lang is None:
            lang = self._current_language
        return LANGUAGES.get(lang, "🏳️")
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their flags."""
        return LANGUAGES.copy()


# Global instance
_i18n = I18n()


def t(key: str) -> str:
    """
    Get translation for a key in current language.
    
    Args:
        key: Translation key
        
    Returns:
        Translated string
    """
    return _i18n.t(key)


def get_current_language() -> str:
    """Get current language code."""
    return _i18n.current_language


def set_language(lang: str):
    """Set current language."""
    _i18n.current_language = lang


def get_flag(lang: Optional[str] = None) -> str:
    """Get flag emoji for a language."""
    return _i18n.get_flag(lang)


def get_available_languages() -> Dict[str, str]:
    """Get available languages with their flags."""
    return _i18n.get_available_languages()


def get_month_name(month: int, lang: Optional[str] = None) -> str:
    """
    Get localized month name.
    
    Args:
        month: Month number (1-12)
        lang: Language code (uses current language if None)
        
    Returns:
        Localized month name
    """
    if lang is None:
        lang = get_current_language()
    
    month_names = MONTH_NAMES.get(lang, MONTH_NAMES[DEFAULT_LANGUAGE])
    if 1 <= month <= 12:
        return month_names[month - 1]
    return ""

