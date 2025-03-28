from typing import Dict, Any
import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .tools.db_tool import DatabaseTool
from .agents.analyzer import AnalyzerAgent
from .agents.sql_expert import SQLExpertAgent
from .agents.visualizer import VisualizerAgent

# Создание соединения с базой данных
def get_db_connection():
    """Создает соединение с базой данных PostgreSQL"""
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

# Получение метаданных базы данных при запуске приложения
def get_db_metadata() -> Dict[str, Any]:
    """Получает и кэширует метаданные базы данных"""
    # Создание экземпляра DatabaseTool
    db_tool = DatabaseTool(get_db_connection())
    
    # Получение метаданных
    metadata = db_tool.get_metadata()
    
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