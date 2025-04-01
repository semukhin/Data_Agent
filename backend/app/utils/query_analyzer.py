import re
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

from ..services.dashboard_service import DashboardService
from ..services.deepseek_adapter import deepseek_adapter
from ..utils.visualization_manager import create_optimized_visualization


def extract_time_period(query_text: str) -> Tuple[datetime, datetime]:
    """Определяет временной период из запроса пользователя"""
    today = datetime.now()
    last_month = today - timedelta(days=30)
    last_6_months = today - timedelta(days=180)
    
    # Определяем упоминания временных периодов в запросе
    if "прошлый месяц" in query_text.lower() or "предыдущий месяц" in query_text.lower():
        return last_month.replace(day=1), today.replace(day=1) - timedelta(days=1)
    elif "последние 6 месяцев" in query_text.lower() or "за 6 месяцев" in query_text.lower():
        return last_6_months, today
    elif "этот год" in query_text.lower() or "текущий год" in query_text.lower():
        return datetime(today.year, 1, 1), today
    
    # Ищем упоминание конкретных месяцев и годов
    month_pattern = r'(январ[ьея]|феврал[ьея]|март[ае]?|апрел[ьея]|ма[йея]|июн[ьея]|июл[ьея]|август[ае]?|сентябр[ьея]|октябр[ьея]|ноябр[ьея]|декабр[ьея]) (\d{4})'
    matches = re.findall(month_pattern, query_text.lower())
    
    if matches:
        month_dict = {
            'январ': 1, 'феврал': 2, 'март': 3, 'апрел': 4, 'ма': 5, 'июн': 6,
            'июл': 7, 'август': 8, 'сентябр': 9, 'октябр': 10, 'ноябр': 11, 'декабр': 12
        }
        
        for month_str, year_str in matches:
            for month_key, month_num in month_dict.items():
                if month_str.startswith(month_key):
                    month = month_num
                    year = int(year_str)
                    start_date = datetime(year, month, 1)
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                    return start_date, end_date
    
    # По умолчанию возвращаем последние 30 дней
    return last_month, today

def preprocess_user_query(query: str) -> Dict[str, Any]:
    """
    Предварительно анализирует запрос пользователя для определения 
    ключевых параметров без обращения к DeepSeek
    """
    query_lower = query.lower()
    
    # Определение типа запроса
    query_type = None
    if any(word in query_lower for word in ["сколько", "количество", "число"]):
        query_type = "count"
    elif any(word in query_lower for word in ["время", "минут", "долго"]):
        query_type = "time"
    elif any(word in query_lower for word in ["доля", "процент", "распределение"]):
        query_type = "distribution"
    elif any(word in query_lower for word in ["сравни", "сравнение", "динамика"]):
        query_type = "comparison"
    else:
        query_type = "general"
    
    # Определение временного периода
    time_pattern = extract_time_period(query)
    
    # Определение объекта запроса
    object_type = None
    if "пользовател" in query_lower:
        object_type = "users"
    elif "сесси" in query_lower:
        object_type = "sessions"
    elif "технолог" in query_lower:
        object_type = "technologies"
    elif "бизнес" in query_lower or "план" in query_lower:
        object_type = "business_plans"
    else:
        object_type = "users"  # По умолчанию
    
    # Определение типа визуализации
    viz_type = None
    if query_type == "distribution":
        viz_type = "pie"
    elif query_type == "comparison" or query_type == "time":
        viz_type = "line"
    elif query_type == "count":
        if "по месяцам" in query_lower or "по неделям" in query_lower:
            viz_type = "line"
        else:
            viz_type = "bar"
    else:
        viz_type = "line"  # По умолчанию
    
    return {
        "query_type": query_type,
        "time_period": time_pattern,
        "object_type": object_type,
        "visualization_type": viz_type
    }

def generate_optimized_sql(query_type, object_type, time_period, sql_hints=None):
    """
    Генерирует оптимизированный SQL-запрос на основе типа запроса и объекта
    """
    start_date, end_date = time_period if time_period else (None, None)
    
    # Форматируем даты для SQL
    start_date_str = start_date.strftime('%Y-%m-%d') if start_date else '2024-01-01'
    end_date_str = end_date.strftime('%Y-%m-%d') if end_date else '2025-12-31'
    
    # Шаблоны SQL-запросов для разных типов запросов
    if query_type == "count" and object_type == "users":
        return f"""
            SELECT DATE_TRUNC('month', cohort_month) AS month,
                   COUNT(DISTINCT user_id) AS user_count
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'
            GROUP BY month
            ORDER BY month
        """
    
    elif query_type == "distribution" and object_type == "users":
        return f"""
            SELECT user_type, COUNT(DISTINCT user_id) AS user_count
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'
            GROUP BY user_type
            ORDER BY user_count DESC
        """
    
    elif query_type == "time" and object_type == "users":
        return f"""
            SELECT DATE_TRUNC('month', cohort_month) AS month,
                   AVG(avg_session_minutes) AS avg_time
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'
            GROUP BY month
            ORDER BY month
        """
    
    elif query_type == "time" and object_type == "technologies":
        return f"""
            SELECT DATE_TRUNC('month', cohort_month) AS month,
                   AVG(avg_tech_views_per_session) AS avg_tech_views,
                   SUM(technology_views) AS total_tech_views
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'
            GROUP BY month
            ORDER BY month
        """
    
    elif query_type == "comparison":
        return f"""
            SELECT user_type,
                   AVG(avg_session_minutes) AS avg_session_time,
                   AVG(total_sessions) AS avg_sessions,
                   AVG(active_days) AS avg_active_days
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'
            GROUP BY user_type
            ORDER BY user_type
        """
    
    # Если запрос не соответствует ни одному шаблону, используем подсказки SQL или создаем базовый запрос
    if sql_hints:
        # Применяем подсказки, убедившись, что запрос соответствует представлению и периоду
        sql = sql_hints
        if "FROM" not in sql.upper():
            sql += f" FROM test_staging.user_metrics_dashboard_optimized"
        
        if "WHERE" not in sql.upper():
            sql += f" WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'"
        elif "cohort_month" not in sql:
            sql = sql.replace("WHERE", f"WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}' AND")
        
        if "ORDER BY" not in sql.upper() and "GROUP BY" in sql.upper():
            # Добавляем сортировку по группировке
            group_match = re.search(r'GROUP BY\s+([^\s,;]+)', sql)
            if group_match:
                sql += f" ORDER BY {group_match.group(1)}"
        
        return sql
    
    # Базовый запрос по умолчанию
    return f"""
        SELECT DATE_TRUNC('month', cohort_month) AS month,
               COUNT(DISTINCT user_id) AS user_count
        FROM test_staging.user_metrics_dashboard_optimized
        WHERE cohort_month BETWEEN '{start_date_str}' AND '{end_date_str}'
        GROUP BY month
        ORDER BY month
    """

def generate_title_from_analysis(analysis: Dict[str, Any], query: str) -> str:
    """Генерирует заголовок на основе анализа запроса"""
    query_type = analysis.get("query_type", "general")
    object_type = analysis.get("object_type", "users")
    
    titles = {
        "count": f"Количество {object_type}",
        "time": f"Временные показатели {object_type}",
        "distribution": f"Распределение {object_type}",
        "comparison": f"Сравнение показателей {object_type}",
        "general": f"Анализ {object_type}"
    }
    
    return titles.get(query_type, f"Анализ {object_type}")

def extract_sql_hints_from_response(response: str) -> str:
    """Извлекает SQL-подсказки из ответа DeepSeek"""
    # Ищем SQL-запрос между маркерами
    sql_match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    return None

async def optimized_process_query(query: str, db_service: DashboardService) -> Dict[str, Any]:
    """
    Оптимизированная обработка запроса с минимальным использованием DeepSeek
    """
    # Шаг 1: Предварительный анализ запроса
    pre_analysis = preprocess_user_query(query)
    
    # Шаг 2: Проверка на соответствие типовым запросам
    matching_query = db_service.find_matching_query(query)
    
    if matching_query:
        # Если запрос соответствует типовому, выполняем его напрямую
        start_date, end_date = pre_analysis["time_period"]
        result = db_service.execute_optimized_query(query)
        
        # Дополним результат информацией из предварительного анализа
        result["visualization_type"] = pre_analysis["visualization_type"]
        return result
    
    # Шаг 3: Если запрос не типовой, используем DeepSeek только для уточнения
    # Создаем упрощенный промпт для DeepSeek
    simplified_prompt = f"""
    Анализ запроса: "{query}"
    
    Определено:
    - Тип запроса: {pre_analysis['query_type']}
    - Объект запроса: {pre_analysis['object_type']}
    - Визуализация: {pre_analysis['visualization_type']}
    
    Уточните SQL-запрос для получения данных из представления test_staging.user_metrics_dashboard_optimized.
    Какие именно поля нужно выбрать и как их агрегировать?
    """
    
    # Вызываем DeepSeek с упрощенным промптом
    deepseek_response = await deepseek_adapter.generate_response_async(
        prompt=simplified_prompt,
        temperature=0.3
    )
    
    # Извлекаем информацию из ответа DeepSeek
    sql_hints = extract_sql_hints_from_response(deepseek_response)
    
    # Шаг 4: Генерируем оптимизированный SQL-запрос на основе подсказок
    sql_query = generate_optimized_sql(
        pre_analysis["query_type"],
        pre_analysis["object_type"],
        pre_analysis["time_period"],
        sql_hints
    )
    
    # Шаг 5: Выполняем SQL-запрос
    data = db_service.execute_raw_query(sql_query)
    
    # Шаг 6: Создаем оптимизированную визуализацию
    visualization = create_optimized_visualization(
        data,
        pre_analysis["visualization_type"],
        pre_analysis["query_type"],
        pre_analysis["object_type"]
    )
    
    return {
        "success": True,
        "data": data.to_dict(orient="records"),
        "visualization": visualization,
        "sql_query": sql_query,
        "visualization_type": pre_analysis["visualization_type"],
        "title": generate_title_from_analysis(pre_analysis, query)
    }

def execute_raw_query(self, sql_query):
    """Выполняет произвольный SQL-запрос и возвращает результаты в DataFrame"""
    return pd.read_sql(sql_query, self.db_connection)