from typing import Dict, Any
import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .tools.db_tool import DatabaseTool
from .agents.analyzer import AnalyzerAgent
from .agents.sql_expert import SQLExpertAgent
from .agents.visualizer import VisualizerAgent
from .services.deepseek_adapter import DeepseekAdapter
# Импортируем новые сервисы (эти файлы нужно будет создать)
from .services.data_analysis_service import DataAnalysisService
from .services.dashboard_service import DashboardService

# Создание соединения с базой данных
def get_db_connection():
    """Создает соединение с базой данных PostgreSQL"""
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

# Обновленное описание представления user_metrics_dashboard_optimized
USER_METRICS_DASHBOARD_DESCRIPTION = """
Представление test_staging.user_metrics_dashboard_optimized содержит сводные данные о поведении пользователей на платформе Atlantix.
Оно сделано специально для удобного анализа пользовательской активности и метрик вовлеченности.

Столбцы представления и их назначение:
- user_id (text): Уникальный идентификатор зарегистрированного пользователя (посетитель который ещё не зарегистрировался - device_id)
- cohort_month (timestamp): Месяц, когда пользователь впервые посетил платформу (для когортного анализа), когортный период в контексте данного представления
- user_type (text): Категория пользователя: "Подписчик", "Активированный", "Заинтересованный"
- technology_views (bigint): Количество просмотров страниц "технологий"
- technology_sessions (bigint): Количество сессий с просмотром страниц "технологий"
- business_plan_clicks (bigint): Количество просмотров страницы "бизнес-планов"
- custom_business_plan_views (bigint): Количество просмотров страницы "Custom Business Plans"
- discovery_views (bigint): Количество просмотров страницы "Discover"
- collection_views (bigint): Количество просмотров "Коллекций"
- search_queries (bigint): Количество поисковых запросов
- total_sessions (bigint): Общее количество сессий зарегистрированного пользователя
- active_days (bigint): Количество дней, когда зарегистрированный пользователь был активен
- avg_session_minutes (numeric): Средняя продолжительность сессии в минутах
- total_platform_minutes (numeric): Общее время, проведенное на платформе в минутах
- total_discover_minutes (numeric): Общее время, проведенное на странице "Discover" в минутах
- minutes_to_first_tech_view (numeric): Время в минутах от первого визита до первого просмотра страницы "технологии"
- minutes_to_first_favorites (numeric): Время в минутах от первого визита до первого добавления в избранное
- avg_discover_minutes_per_session (numeric): Среднее время на странице "Discover" за сессию
- avg_discover_minutes_per_month (numeric): Среднее время на странице "Discover" в месяц
- avg_tech_views_per_session (numeric): Среднее количество просмотров страниц "технологий" за сессию
- avg_business_plan_clicks_per_session (numeric): Среднее количество просмотров страницы "бизнес-планы" за сессию
- avg_search_queries_per_session (numeric): Среднее количество поисковых запросов за сессию
- is_interested_user (integer): Флаг (1/null) - является ли пользователь "заинтересованным" из имеющихся профилей в user_type
- is_activated_user (integer): Флаг (1/null) - является ли пользователь "активированным" из имеющихся профилей в user_type
- is_subscriber (integer): Флаг (1/null) - является ли пользователь подписчиком из имеющихся профилей в user_type

Представление оптимально для:
- Анализа активности пользователей по временным периодам
- Сравнения поведения разных категорий пользователей
- Отслеживания конверсии от заинтересованных к подписчикам
- Выявления паттернов поведения, ведущих к подписке
"""

# Получение метаданных базы данных при запуске приложения
def get_db_metadata() -> Dict[str, Any]:
    """Получает и кэширует метаданные базы данных"""
    # Создание экземпляра DatabaseTool
    db_tool = DatabaseTool(get_db_connection())
    
    # Получение метаданных
    metadata = db_tool.get_metadata()
    
    # Добавляем информацию о представлении, если его нет в метаданных
    if "test_staging.user_metrics_dashboard_optimized" not in metadata:
        # Добавляем метаданные представления вручную
        metadata["test_staging.user_metrics_dashboard_optimized"] = {
            "description": USER_METRICS_DASHBOARD_DESCRIPTION,
            "columns": [
                {"name": "user_id", "type": "text", "nullable": False, 
                 "description": "Уникальный идентификатор зарегистрированного пользователя"},
                {"name": "cohort_month", "type": "timestamp", "nullable": True, 
                 "description": "Месяц, когда пользователь впервые посетил платформу (для когортного анализа), когортный период в контексте данного представления"},
                {"name": "user_type", "type": "text", "nullable": True, 
                 "description": "Категория пользователя ('Подписчик', 'Активированный', 'Заинтересованный')"},
                {"name": "technology_views", "type": "bigint", "nullable": False, 
                 "description": "Количество просмотров страниц 'технологий'"},
                {"name": "technology_sessions", "type": "bigint", "nullable": False, 
                 "description": "Количество сессий с просмотром страниц 'технологий'"},
                {"name": "business_plan_clicks", "type": "bigint", "nullable": False, 
                 "description": "Количество просмотров страницы 'бизнес-планов'"},
                {"name": "custom_business_plan_views", "type": "bigint", "nullable": False, 
                 "description": "Количество просмотров страницы 'Custom Business Plans'"},
                {"name": "discovery_views", "type": "bigint", "nullable": False, 
                 "description": "Количество просмотров страницы 'Discover'"},
                {"name": "collection_views", "type": "bigint", "nullable": False, 
                 "description": "Количество просмотров 'Коллекций'"},
                {"name": "search_queries", "type": "bigint", "nullable": False, 
                 "description": "Количество поисковых запросов"},
                {"name": "total_sessions", "type": "bigint", "nullable": False, 
                 "description": "Общее количество сессий зарегистрированного пользователя"},
                {"name": "active_days", "type": "bigint", "nullable": False, 
                 "description": "Количество дней, когда зарегистрированный пользователь был активен"},
                {"name": "avg_session_minutes", "type": "numeric", "nullable": False, 
                 "description": "Средняя продолжительность сессии в минутах"},
                {"name": "total_platform_minutes", "type": "numeric", "nullable": False, 
                 "description": "Общее время, проведенное на платформе в минутах"},
                {"name": "total_discover_minutes", "type": "numeric", "nullable": False, 
                 "description": "Общее время, проведенное на странице 'Discover' в минутах"},
                {"name": "minutes_to_first_tech_view", "type": "numeric", "nullable": True, 
                 "description": "Время в минутах от первого визита до первого просмотра страницы 'технологии'"},
                {"name": "minutes_to_first_favorites", "type": "numeric", "nullable": True, 
                 "description": "Время в минутах от первого визита до первого добавления в избранное"},
                {"name": "avg_discover_minutes_per_session", "type": "numeric", "nullable": False, 
                 "description": "Среднее время на странице 'Discover' за сессию"},
                {"name": "avg_discover_minutes_per_month", "type": "numeric", "nullable": False, 
                 "description": "Среднее время на странице 'Discover' в месяц"},
                {"name": "avg_tech_views_per_session", "type": "numeric", "nullable": True, 
                 "description": "Среднее количество просмотров страниц 'технологий' за сессию"},
                {"name": "avg_business_plan_clicks_per_session", "type": "numeric", "nullable": True, 
                 "description": "Среднее количество просмотров страницы 'бизнес-планы' за сессию"},
                {"name": "avg_search_queries_per_session", "type": "numeric", "nullable": True, 
                 "description": "Среднее количество поисковых запросов за сессию"},
                {"name": "is_interested_user", "type": "integer", "nullable": True, 
                 "description": "Флаг (1/null) - является ли пользователь 'заинтересованным' из имеющихся профилей в user_type"},
                {"name": "is_activated_user", "type": "integer", "nullable": True, 
                 "description": "Флаг (1/null) - является ли пользователь 'активированным' из имеющихся профилей в user_type"},
                {"name": "is_subscriber", "type": "integer", "nullable": True, 
                 "description": "Флаг (1/null) - является ли пользователь подписчиком из имеющихся профилей в user_type"}
            ],
            "primary_keys": ["user_id"],
            "foreign_keys": [],
            "sample_data": []  # Можно заполнить примерами данных, если нужно
        }
    
    return metadata

# Глобальная переменная для хранения метаданных
DB_METADATA = None

# Функция для инициализации метаданных
def initialize_metadata():
    """Инициализирует метаданные базы данных"""
    global DB_METADATA
    DB_METADATA = get_db_metadata()

# Зависимости для инъекции в эндпоинты
def get_db():
    """Предоставляет инструмент для работы с базой данных"""
    db_connection = get_db_connection()
    db_tool = DatabaseTool(db_connection)
    return db_tool

def get_analyzer_agent():
    """Предоставляет агента для анализа запросов"""
    global DB_METADATA
    if DB_METADATA is None:
        initialize_metadata()
    return AnalyzerAgent(DB_METADATA)

def get_sql_agent():
    """Предоставляет агента для генерации SQL-запросов"""
    global DB_METADATA
    if DB_METADATA is None:
        initialize_metadata()
    return SQLExpertAgent(DB_METADATA)

def get_viz_agent():
    """Предоставляет агента для генерации визуализаций"""
    return VisualizerAgent()

# Новые зависимости для оптимизированных сервисов
def get_deepseek_adapter():
    """Предоставляет адаптер для работы с DeepSeek API"""
    return DeepseekAdapter()

def get_dashboard_service():
    """Предоставляет сервис для работы с представлением dashboard"""
    db_connection = get_db_connection()
    return DashboardService(db_connection)

def get_data_analysis_service():
    """Предоставляет сервис для анализа данных и генерации визуализаций"""
    db_connection = get_db_connection()
    deepseek_adapter = get_deepseek_adapter()
    return DataAnalysisService(db_connection, deepseek_adapter)