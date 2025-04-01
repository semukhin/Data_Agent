from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import re
import hashlib
import time

from ..metadata.dashboard_schema import USER_METRICS_DASHBOARD_SCHEMA

class DashboardService:
    """Сервис для работы с представлением test_staging.user_metrics_dashboard_optimized"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.metadata = USER_METRICS_DASHBOARD_SCHEMA
    
    def get_active_users_by_period(self, period: str = 'month', start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Получает количество активных пользователей по периодам"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=180)  # По умолчанию последние 6 месяцев
        if not end_date:
            end_date = datetime.now()
            
        period_format = 'week' if period.lower() == 'week' else 'month'
        
        query = f"""
            SELECT DATE_TRUNC('{period_format}', cohort_month) AS time_period,
                  COUNT(DISTINCT user_id) AS active_users
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            GROUP BY time_period
            ORDER BY time_period
        """
        
        return pd.read_sql(query, self.db_connection)
    
    def get_user_type_distribution(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Получает распределение пользователей по типам"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)  # По умолчанию последний месяц
        if not end_date:
            end_date = datetime.now()
            
        query = """
            SELECT user_type, COUNT(DISTINCT user_id) AS user_count
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{0}' AND '{1}'
            GROUP BY user_type
            ORDER BY user_count DESC
        """.format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        return pd.read_sql(query, self.db_connection)
    
    def get_user_engagement_metrics(self, metric_name: str, group_by: str = 'month', start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Получает метрики вовлеченности пользователей"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)  # По умолчанию последние 3 месяца
        if not end_date:
            end_date = datetime.now()
            
        allowed_metrics = [
            'avg_session_minutes', 'total_platform_minutes', 'total_discover_minutes',
            'avg_discover_minutes_per_session', 'avg_tech_views_per_session', 
            'avg_business_plan_clicks_per_session', 'avg_search_queries_per_session'
        ]
        
        if metric_name not in allowed_metrics:
            metric_name = 'avg_session_minutes'  # Метрика по умолчанию
            
        period_format = 'week' if group_by.lower() == 'week' else 'month'
        
        query = f"""
            SELECT DATE_TRUNC('{period_format}', cohort_month) AS time_period,
                   AVG({metric_name}) AS average_value
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            GROUP BY time_period
            ORDER BY time_period
        """
        
        return pd.read_sql(query, self.db_connection)
    
    def find_matching_query(self, user_query: str) -> Optional[Dict[str, Any]]:
        """Находит подходящий предопределенный запрос на основе запроса пользователя"""
        user_query_lower = user_query.lower()
        
        # Проверяем каждый предопределенный запрос на соответствие
        for query_template in self.metadata["common_queries"]:
            match_score = 0
            
            # Проверяем каждое ключевое слово
            for keyword in query_template["keywords"]:
                if keyword.lower() in user_query_lower:
                    match_score += 1
            
            # Если найдено достаточное совпадение, возвращаем запрос
            if match_score >= 2:  # Минимум 2 ключевых слова должны совпадать
                return query_template
                
        return None
    
    def execute_optimized_query(self, user_query: str) -> Dict[str, Any]:
        """Выполняет оптимизированный запрос на основе запроса пользователя"""
        # Извлекаем временной период из запроса
        start_date, end_date = self._extract_time_period(user_query)
        
        # Ищем соответствующий шаблон запроса
        matching_query = self.find_matching_query(user_query)
        
        # Если найден подходящий шаблон, используем его
        if matching_query:
            sql = matching_query["sql"].format(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            # Выполняем SQL-запрос
            data = pd.read_sql(sql, self.db_connection)
            
            return {
                "success": True,
                "data": data,
                "visualization_type": matching_query["visualization_type"],
                "title": matching_query["name"],
                "sql_query": sql
            }
        
        # Если шаблон не найден, пытаемся определить, что нужно пользователю
        if "тип" in user_query.lower() and "пользовател" in user_query.lower():
            # Запрос о распределении пользователей по типам
            data = self.get_user_type_distribution(start_date, end_date)
            return {
                "success": True,
                "data": data,
                "visualization_type": "pie",
                "title": "Распределение пользователей по типам",
                "sql_query": "-- Запрос на распределение пользователей по типам"
            }
        elif "врем" in user_query.lower() or "минут" in user_query.lower():
            # Запрос о времени на платформе
            data = self.get_user_engagement_metrics('avg_session_minutes', 'month', start_date, end_date)
            return {
                "success": True,
                "data": data,
                "visualization_type": "line",
                "title": "Среднее время сессии по месяцам",
                "sql_query": "-- Запрос на среднее время сессии по месяцам"
            }
        else:
            # По умолчанию возвращаем активных пользователей
            data = self.get_active_users_by_period('month', start_date, end_date)
            return {
                "success": True,
                "data": data,
                "visualization_type": "line",
                "title": "Активные пользователи по месяцам",
                "sql_query": "-- Запрос на активных пользователей по месяцам"
            }
    
    def _extract_time_period(self, query_text: str) -> tuple:
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