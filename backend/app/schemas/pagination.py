from typing import Optional, Generic, TypeVar, List, Dict, Any
from pydantic import BaseModel, Field

# Типовая переменная для обобщенного типа
T = TypeVar('T')

class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page_size: int = Field(100, ge=1, le=1000, description="Количество записей на странице")
    page: int = Field(1, ge=1, description="Номер страницы")

class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией"""
    total: int = Field(..., description="Общее количество записей")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Размер страницы")
    total_pages: int = Field(..., description="Общее количество страниц")
    items: List[T] = Field(..., description="Список элементов на текущей странице")

    class Config:
        schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 50,
                "total_pages": 3,
                "items": [{"id": 1, "name": "Example"}]
            }
        }

def paginate(items: List[Any], params: PaginationParams) -> Dict[str, Any]:
    """
    Пагинирует список элементов
    
    Args:
        items: Список элементов для пагинации
        params: Параметры пагинации
        
    Returns:
        Dict с пагинированными данными
    """
    total = len(items)
    total_pages = (total + params.page_size - 1) // params.page_size
    
    # Ограничение страницы до максимального значения
    page = min(params.page, total_pages) if total_pages > 0 else 1
    
    # Расчет индексов для среза
    start_idx = (page - 1) * params.page_size
    end_idx = min(start_idx + params.page_size, total)
    
    # Срез данных для текущей страницы
    paginated_items = items[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "page_size": params.page_size,
        "total_pages": total_pages,
        "items": paginated_items
    }