from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_db, get_analyzer_agent, get_sql_agent, get_viz_agent
from ..schemas.requests import QueryRequest
from ..services.query_processor import process_query

router = APIRouter()

@router.post("/analyze")
async def analyze_query(
    request: QueryRequest,
    analyzer = Depends(get_analyzer_agent),
    sql_agent = Depends(get_sql_agent),
    viz_agent = Depends(get_viz_agent),
    db = Depends(get_db)
):
    try:
        # Обработка запроса пользователя
        result = process_query(
            query=request.query,
            analyzer=analyzer,
            sql_agent=sql_agent,
            viz_agent=viz_agent,
            db=db
        )
        
        return {
            "success": True,
            "data": result["data"],
            "visualization": result["visualization"],
            "sql_query": result["sql_query"],
            "explanation": result["explanation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))