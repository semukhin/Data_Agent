from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .pagination import PaginationParams

class QueryRequest(BaseModel):
    """Схема запроса для анализа данных"""
    query: str = Field(..., description="Текстовый запрос пользователя")
    visualization_type: Optional[str] = Field(None, description="Предпочтительный тип визуализации")
    filters: Optional[Dict[str, Any]] = Field(None, description="Дополнительные фильтры для запроса")
    pagination: Optional[PaginationParams] = Field(None, description="Параметры пагинации")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Покажи динамику активных пользователей по неделям за последние 3 месяца",
                "visualization_type": "line",
                "filters": None,
                "pagination": {
                    "page_size": 100,
                    "page": 1
                }
            }
        }

class MetadataRequest(BaseModel):
    """Схема запроса для получения метаданных"""
    table_name: Optional[str] = Field(None, description="Имя таблицы для получения метаданных")

class SQLRequest(BaseModel):
    """Схема запроса для выполнения произвольного SQL"""
    sql_query: str = Field(..., description="SQL-запрос для выполнения")
    pagination: Optional[PaginationParams] = Field(None, description="Параметры пагинации")
    
    class Config:
        schema_extra = {
            "example": {
                "sql_query": "SELECT * FROM events_view_3_2 LIMIT 100",
                "pagination": {
                    "page_size": 100,
                    "page": 1
                }
            }
        }