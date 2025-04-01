import hashlib
import time
import asyncio
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from ..utils.query_analyzer import preprocess_user_query, generate_optimized_sql
from ..utils.visualization_manager import create_optimized_visualization
from ..services.dashboard_service import DashboardService
from ..services.deepseek_adapter import DeepseekAdapter
from ..metadata.dashboard_schema import USER_METRICS_DASHBOARD_SCHEMA

# Оптимизированный системный промпт для DeepSeek
OPTIMIZED_SYSTEM_PROMPT = """
Ты специалист по анализу данных, работающий с представлением test_staging.user_metrics_dashboard_optimized.

ВАЖНЫЕ ПРАВИЛА:
1. ВСЕГДА используй ТОЛЬКО представление test_staging.user_metrics_dashboard_optimized. Не используй другие таблицы.
2. Все ответы СТРОГО в формате JSON с полями sql_query, title и description.
3. Все заголовки и описания на РУССКОМ языке.
4. Используй DATE_TRUNC для работы с временными данными (например, DATE_TRUNC('month', cohort_month)).
5. SQL-запросы должны быть оптимальными, без излишней сложности.
6. Избегай подзапросов, если можно обойтись без них.
7. Обязательно добавляй ORDER BY для запросов с группировкой.

Описание столбцов представления test_staging.user_metrics_dashboard_optimized:
- user_id (text): Уникальный идентификатор зарегистрированного пользователя
- cohort_month (timestamp): Месяц, когда пользователь впервые посетил платформу
- user_type (text): Категория пользователя ("Подписчик", "Активированный", "Заинтересованный")
- technology_views (bigint): Количество просмотров страниц "технологий"
- technology_sessions (bigint): Количество сессий с просмотром "технологий"
- business_plan_clicks (bigint): Количество просмотров "бизнес-планов"
- total_sessions (bigint): Общее количество сессий пользователя
- active_days (bigint): Количество дней активности пользователя
- avg_session_minutes (numeric): Средняя продолжительность сессии в минутах
- total_platform_minutes (numeric): Общее время на платформе в минутах
- is_interested_user (integer): Флаг "заинтересованного" пользователя (1/null)
- is_activated_user (integer): Флаг "активированного" пользователя (1/null)
- is_subscriber (integer): Флаг подписчика (1/null)

Примеры оптимальных SQL-запросов:
1. Для анализа активных пользователей по месяцам:
   SELECT DATE_TRUNC('month', cohort_month) AS month, COUNT(DISTINCT user_id) AS user_count
   FROM test_staging.user_metrics_dashboard_optimized
   WHERE cohort_month BETWEEN '2025-01-01' AND '2025-03-31'
   GROUP BY month
   ORDER BY month

2. Для распределения по типам пользователей:
   SELECT user_type, COUNT(DISTINCT user_id) AS user_count
   FROM test_staging.user_metrics_dashboard_optimized
   WHERE cohort_month BETWEEN '2025-01-01' AND '2025-03-31'
   GROUP BY user_type
   ORDER BY user_count DESC
"""

class DataAnalysisService:
    """
    Сервис для анализа данных и визуализации представления test_staging.user_metrics_dashboard_optimized
    """
    
    def __init__(self, db_connection, deepseek_adapter=None):
        self.dashboard_service = DashboardService(db_connection)
        self.deepseek_adapter = deepseek_adapter or DeepseekAdapter()
        self.cache = {}  # Простой встроенный кэш
    
    async def process_query(self, query_text, use_cache=True):
        """
        Обрабатывает запрос пользователя и возвращает результаты
        
        Args:
            query_text: Текстовый запрос пользователя
            use_cache: Использовать ли кэш для одинаковых запросов
            
        Returns:
            Результаты запроса с визуализацией
        """
        # Проверяем кэш
        cache_key = hashlib.md5(query_text.encode()).hexdigest()
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        start_time = time.time()
        
        try:
            # 1. Предварительный анализ запроса
            pre_analysis = preprocess_user_query(query_text)
            
            # 2. Проверка на соответствие типовым запросам
            matching_query = self.dashboard_service.find_matching_query(query_text)
            
            # 3. Выбор пути обработки: оптимизированный или с использованием DeepSeek
            if matching_query:
                # Быстрый путь: используем предопределенный шаблон запроса
                result = await self._process_matching_query(matching_query, pre_analysis)
            else:
                # Стандартный путь: используем DeepSeek для более точного анализа
                result = await self._process_with_deepseek(query_text, pre_analysis)
            
            # 4. Добавляем метрики производительности
            processing_time = time.time() - start_time
            result["performance"] = {
                "processing_time_ms": round(processing_time * 1000, 2),
                "query_type": pre_analysis["query_type"],
                "optimization_path": "fast_path" if matching_query else "deepseek_path"
            }
            
            # 5. Кэшируем результат
            if use_cache:
                self.cache[cache_key] = result
            
            return result
        
        except Exception as e:
            # Обработка ошибок с детальной информацией
            error_result = {
                "success": False,
                "error": str(e),
                "performance": {
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                    "error_source": type(e).__name__
                }
            }
            return error_result
    
    async def _process_matching_query(self, matching_query, pre_analysis):
        """Обрабатывает запрос, соответствующий предопределенному шаблону"""
        start_date, end_date = pre_analysis["time_period"]
        
        # Формируем SQL с подстановкой параметров
        sql = matching_query["sql"].format(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        # Выполняем запрос
        data = self.dashboard_service.execute_raw_query(sql)
        
        # Создаем визуализацию
        visualization = create_optimized_visualization(
            data,
            matching_query["visualization_type"],
            pre_analysis["query_type"],
            pre_analysis["object_type"],
            matching_query["name"]
        )
        
        return {
            "success": True,
            "data": data.to_dict(orient="records"),
            "visualization": visualization,
            "sql_query": sql,
            "title": matching_query["name"],
            "description": f"Данные за период {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
            "explanation": f"Запрос анализирует данные из представления test_staging.user_metrics_dashboard_optimized за период с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}."
        }
    
    async def _process_with_deepseek(self, query_text, pre_analysis):
        """Обрабатывает запрос с использованием DeepSeek для анализа"""
        # Формируем оптимизированный промпт для DeepSeek
        prompt = f"""
        Запрос пользователя: "{query_text}"
        
        Предварительный анализ:
        - Тип запроса: {pre_analysis['query_type']}
        - Тип объекта: {pre_analysis['object_type']}
        - Предпочтительная визуализация: {pre_analysis['visualization_type']}
        - Период: с {pre_analysis['time_period'][0].strftime('%d.%m.%Y')} по {pre_analysis['time_period'][1].strftime('%d.%m.%Y')}
        
        Требуется SQL-запрос к представлению test_staging.user_metrics_dashboard_optimized.
        
        Ответ ТОЛЬКО в формате JSON:
        {{
            "sql_query": "SQL-запрос к представлению",
            "title": "Заголовок для визуализации",
            "description": "Краткое описание запроса"
        }}
        """
        
        # Запрашиваем анализ от DeepSeek
        deepseek_response = await self.deepseek_adapter.generate_response_async(
            prompt=prompt,
            system_message=OPTIMIZED_SYSTEM_PROMPT,
            temperature=0.2
        )
        
        # Извлекаем JSON из ответа
        result_data = self.deepseek_adapter.extract_json_from_response(deepseek_response)
        
        if not result_data.get("sql_query"):
            # Если SQL не предоставлен, генерируем его на основе предварительного анализа
            sql_query = generate_optimized_sql(
                pre_analysis["query_type"],
                pre_analysis["object_type"],
                pre_analysis["time_period"]
            )
        else:
            sql_query = result_data["sql_query"]
        
        # Выполняем SQL-запрос
        data = self.dashboard_service.execute_raw_query(sql_query)
        
        # Создаем визуализацию
        visualization = create_optimized_visualization(
            data,
            pre_analysis["visualization_type"],
            pre_analysis["query_type"],
            pre_analysis["object_type"],
            result_data.get("title", "Анализ данных")
        )
        
        return {
            "success": True,
            "data": data.to_dict(orient="records"),
            "visualization": visualization,
            "sql_query": sql_query,
            "title": result_data.get("title", "Анализ данных"),
            "description": result_data.get("description", "Результаты анализа данных"),
            "explanation": result_data.get("description", "Анализ данных из представления test_staging.user_metrics_dashboard_optimized.")
        }