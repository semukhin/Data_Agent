from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AnalysisResponse(BaseModel):
    """Схема ответа для результатов анализа запроса"""
    required_data: str = Field(..., description="Описание необходимых данных")
    visualization_type: str = Field(..., description="Рекомендуемый тип визуализации")
    sql_hints: str = Field(..., description="Подсказки для SQL-запроса")

class SQLResponse(BaseModel):
    """Схема ответа для результатов генерации SQL"""
    sql_query: str = Field(..., description="Сгенерированный SQL-запрос")
    query_explanation: str = Field(..., description="Объяснение запроса")

class VisualizationResponse(BaseModel):
    """Схема ответа для результатов визуализации"""
    plotly_code: str = Field(..., description="Код Plotly для визуализации")
    figure_json: Dict[str, Any] = Field(..., description="JSON-представление визуализации")
    title: str = Field(..., description="Заголовок визуализации")
    description: str = Field(..., description="Описание визуализации")

class QueryResponse(BaseModel):
    """Схема ответа для результатов обработки запроса"""
    success: bool = Field(..., description="Успешность выполнения запроса")
    data: List[Dict[str, Any]] = Field(..., description="Данные результата запроса")
    visualization: Dict[str, Any] = Field(..., description="Данные визуализации")
    sql_query: str = Field(..., description="Выполненный SQL-запрос")
    explanation: str = Field(..., description="Объяснение результатов")
    title: str = Field(..., description="Заголовок результатов")
    description: str = Field(..., description="Описание результатов")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": [{"date": "2023-01-01", "active_users": 1250}, {"date": "2023-01-08", "active_users": 1340}],
                "visualization": {"data": [{"x": ["2023-01-01", "2023-01-08"], "y": [1250, 1340], "type": "line"}], "layout": {"title": "Активные пользователи по неделям"}},
                "sql_query": "SELECT date_trunc('week', event_time) as week, COUNT(DISTINCT user_id) as active_users FROM events_view_3_2 GROUP BY week ORDER BY week",
                "explanation": "Запрос выбирает количество уникальных пользователей по неделям из таблицы событий",
                "title": "Динамика активных пользователей по неделям",
                "description": "График показывает изменение количества активных пользователей по неделям за выбранный период"
            }
        }

class MetadataResponse(BaseModel):
    """Схема ответа для метаданных базы данных"""
    tables: Dict[str, Any] = Field(..., description="Метаданные таблиц")