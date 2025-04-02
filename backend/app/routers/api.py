from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from ..dependencies import get_db, get_analyzer_agent, get_sql_agent, get_viz_agent, DB_METADATA
from ..schemas.requests import QueryRequest, MetadataRequest, SQLRequest
from ..schemas.responses import QueryResponse, MetadataResponse
from ..schemas.pagination import PaginationParams, paginate
from ..dependencies import get_data_analysis_service
from ..services.data_analysis_service import DataAnalysisService

router = APIRouter()

@router.post("/analyze", response_model=QueryResponse)
async def analyze_query(
    request: QueryRequest,
    data_analysis_service: DataAnalysisService = Depends(get_data_analysis_service)
):
    """
    Обрабатывает запрос пользователя на анализ данных
    """
    try:
        # Обрабатываем запрос через оптимизированный сервис
        result = await data_analysis_service.process_query(request.query, use_cache=True)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Ошибка обработки запроса"))
        
        # Применяем пагинацию, если она запрошена
        if request.pagination:
            paginated_data = paginate(result["data"], request.pagination)
            result["data"] = paginated_data["items"]
            result["pagination"] = {
                "total": paginated_data["total"],
                "page": paginated_data["page"],
                "page_size": paginated_data["page_size"],
                "total_pages": paginated_data["total_pages"]
            }
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Rest of the router remains the same as in your original file

@router.get("/metadata", response_model=MetadataResponse)
async def get_metadata(
    table_name: Optional[str] = Query(None, description="Имя таблицы для получения метаданных")
):
    """
    Возвращает метаданные базы данных
    
    Args:
        table_name: Имя таблицы для получения метаданных
        
    Returns:
        Метаданные таблиц
    """
    global DB_METADATA
    
    if DB_METADATA is None:
        raise HTTPException(status_code=500, detail="Метаданные базы данных не инициализированы")
    
    # Если указано имя таблицы, возвращаем только её метаданные
    if table_name:
        if table_name in DB_METADATA:
            return {"tables": {table_name: DB_METADATA[table_name]}}
        else:
            raise HTTPException(status_code=404, detail=f"Таблица {table_name} не найдена")
    
    return {"tables": DB_METADATA}

@router.post("/execute-sql")
async def execute_sql(
    request: SQLRequest,
    pagination: PaginationParams = Depends(),
    db = Depends(get_db)
):
    """
    Выполняет произвольный SQL-запрос
    
    Args:
        request: Запрос на выполнение SQL
        pagination: Параметры пагинации
        db: Инструмент базы данных
        
    Returns:
        Результаты выполнения SQL-запроса
    """
    result = db.execute_query(request.sql_query)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Применяем пагинацию к результатам
    data = result["data"].to_dict(orient="records")
    paginated_data = paginate(data, pagination)
    
    return {
        "success": True,
        "data": paginated_data["items"],
        "pagination": {
            "total": paginated_data["total"],
            "page": paginated_data["page"],
            "page_size": paginated_data["page_size"],
            "total_pages": paginated_data["total_pages"]
        }
    }