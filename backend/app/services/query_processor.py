import pandas as pd
import json
from typing import Dict, Any
from ..tools.db_tool import DatabaseTool
from ..tools.viz_tool import VisualizationTool

def process_query(query: str, analyzer, sql_agent, viz_agent, db: DatabaseTool) -> Dict[str, Any]:
    """
    Обрабатывает запрос пользователя и возвращает результаты
    
    Args:
        query: Текстовый запрос пользователя
        analyzer: Агент для анализа запроса
        sql_agent: Агент для генерации SQL-запроса
        viz_agent: Агент для генерации визуализации
        db: Инструмент для выполнения запросов к базе данных
        
    Returns:
        Dictionary с результатами обработки запроса
    """
    # Шаг 1: Анализ запроса пользователя
    analysis = analyzer.process_query(query)
    
    # Шаг 2: Генерация SQL-запроса
    sql_result = sql_agent.generate_sql(analysis)
    
    # Проверка наличия SQL-запроса
    if not sql_result.get("sql_query"):
        raise Exception("Не удалось сгенерировать SQL-запрос")
    
    # Шаг 3: Выполнение SQL-запроса
    db_result = db.execute_query(sql_result["sql_query"])
    
    if not db_result["success"]:
        raise Exception(f"Ошибка базы данных: {db_result['error']}")
    
    # Получение данных из результата запроса
    data = db_result["data"]
    
    # Шаг 4: Генерация визуализации
    viz_result = viz_agent.generate_visualization_code(
        data=data,
        visualization_type=analysis["visualization_type"],
        user_query=query
    )
    
    # Создание визуализации с помощью инструмента
    viz_tool = VisualizationTool()
    viz_data = viz_tool.create_visualization({
        "data": data,
        "type": analysis["visualization_type"],
        "config": {
            "title": viz_result.get("title", "Визуализация данных"),
            "xaxis_title": viz_result.get("x_axis_title"),
            "yaxis_title": viz_result.get("y_axis_title")
        }
    })
    
    # Формирование итогового результата
    return {
        "data": data.to_dict(orient="records"),
        "visualization": viz_data.get("figure", {}),
        "sql_query": sql_result["sql_query"],
        "explanation": sql_result.get("query_explanation", ""),
        "analysis": analysis,
        "title": viz_result.get("title", "Результаты анализа"),
        "description": viz_result.get("description", "")
    }