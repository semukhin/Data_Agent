from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from ..dependencies import get_db, get_analyzer_agent, get_sql_agent, get_viz_agent, DB_METADATA
from ..schemas.requests import QueryRequest, MetadataRequest, SQLRequest
from ..schemas.responses import QueryResponse, MetadataResponse
from ..schemas.pagination import PaginationParams, paginate
from ..services.query_processor import process_query

router = APIRouter()

@router.post("/analyze", response_model=QueryResponse)
async def analyze_query(
    request: QueryRequest,
    analyzer = Depends(get_analyzer_agent),
    sql_agent = Depends(get_sql_agent),
    viz_agent = Depends(get_viz_agent),
    db = Depends(get_db)
):
    """
    Обрабатывает запрос пользователя и возвращает результаты анализа
    
    Args:
        request: Запрос пользователя
        analyzer: Агент анализа
        sql_agent: SQL-агент
        viz_agent: Агент визуализации
        db: Инструмент базы данных
        
    Returns:
        Результаты обработки запроса
    """
    try:
        # Обеспечим наличие объекта пагинации, если он не передан
        pagination_params = request.pagination if request.pagination else PaginationParams(page=1, page_size=100)
        
        # Обработка запроса пользователя
        result = process_query(
            query=request.query,
            analyzer=analyzer,
            sql_agent=sql_agent,
            viz_agent=viz_agent,
            db=db,
            pagination=pagination_params
        )
        
        # Формирование ответа
        response = {
            "success": True,
            "data": result.get("data", []),
            "visualization": result.get("visualization", {}),
            "sql_query": result.get("sql_query", ""),
            "explanation": result.get("explanation", ""),
            "title": result.get("title", "Результаты анализа"),
            "description": result.get("description", "")
        }
        
        # Добавление информации о пагинации, если она есть в результате
        if "pagination" in result:
            response["pagination"] = result["pagination"]
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()  # Вывод полного стека ошибки для отладки
        raise HTTPException(status_code=500, detail=str(e))

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