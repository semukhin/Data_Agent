def process_query(query, analyzer, sql_agent, viz_agent, db):
    # Шаг 1: Анализ запроса пользователя
    analysis = analyzer.process_query(query)
    
    # Шаг 2: Генерация SQL-запроса
    sql_result = sql_agent.generate_sql(analysis)
    
    # Шаг 3: Выполнение SQL-запроса
    db_result = db.execute_query(sql_result["sql_query"])
    
    if not db_result["success"]:
        raise Exception(f"Database error: {db_result['error']}")
    
    # Шаг 4: Генерация визуализации
    viz_result = viz_agent.generate_visualization_code(
        data=db_result["data"],
        visualization_type=analysis["visualization_type"],
        user_query=query
    )
    
    return {
        "data": db_result["data"].to_dict(orient="records"),
        "visualization": viz_result["plotly_code"],
        "sql_query": sql_result["sql_query"],
        "explanation": sql_result["query_explanation"]
    }