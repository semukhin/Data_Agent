import hashlib
import time
import asyncio
import pandas as pd
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..tools.db_tool import DatabaseTool
from ..tools.viz_tool import VisualizationTool
from ..agents.analyzer import AnalyzerAgent
from ..agents.sql_expert import SQLExpertAgent
from ..agents.visualizer import VisualizerAgent
from ..schemas.pagination import PaginationParams, paginate
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
        self.db_connection = db_connection
        self.db_tool = DatabaseTool(db_connection)
        self.dashboard_service = DashboardService(db_connection)
        self.deepseek_adapter = deepseek_adapter or DeepseekAdapter()
        
        # Инициализация агентов
        self.analyzer_agent = None
        self.sql_agent = None
        self.viz_agent = None
        
        # Кэш для запросов
        self.cache = {}  # Простой встроенный кэш
    
    def _ensure_agents_initialized(self, db_metadata=None):
        """
        Убеждается, что все агенты инициализированы
        """
        if not self.analyzer_agent and db_metadata:
            self.analyzer_agent = AnalyzerAgent(db_metadata)
        
        if not self.sql_agent and db_metadata:
            self.sql_agent = SQLExpertAgent(db_metadata)
            
        if not self.viz_agent:
            self.viz_agent = VisualizerAgent()
    
    async def process_query(self, query_text: str, db_metadata=None, use_cache=True, 
                            pagination: Optional[PaginationParams] = None):
        """
        Обрабатывает запрос пользователя и возвращает результаты
        
        Args:
            query_text: Текстовый запрос пользователя
            db_metadata: Метаданные базы данных
            use_cache: Использовать ли кэш для одинаковых запросов
            pagination: Параметры пагинации
            
        Returns:
            Результаты запроса с визуализацией
        """
        # Проверяем кэш
        cache_key = hashlib.md5(query_text.encode()).hexdigest()
        if use_cache and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            
            # Если запрошена пагинация, применяем её к кэшированным данным
            if pagination and 'data' in cached_result:
                data_records = cached_result['data']
                paginated_data = paginate(data_records, pagination)
                
                result = {**cached_result}
                result['data'] = paginated_data['items']
                result['pagination'] = {
                    'total': paginated_data['total'],
                    'page': paginated_data['page'],
                    'page_size': paginated_data['page_size'],
                    'total_pages': paginated_data['total_pages']
                }
                return result
            
            return cached_result
        
        start_time = time.time()
        
        try:
            # Убеждаемся, что агенты инициализированы
            self._ensure_agents_initialized(db_metadata)
            
            # Решаем, какой путь обработки использовать
            if self.dashboard_service and hasattr(self.dashboard_service, 'find_matching_query'):
                # Сначала проверяем, соответствует ли запрос типовым шаблонам
                matching_query = self.dashboard_service.find_matching_query(query_text)
                
                if matching_query:
                    # Быстрый путь: используем предопределенный шаблон запроса
                    result = await self._process_with_dashboard_service(query_text, matching_query)
                elif self.analyzer_agent and self.sql_agent and self.viz_agent:
                    # Полный путь с агентами: анализ → SQL → визуализация
                    result = await self._process_with_agents(query_text)
                else:
                    # Стандартный путь: используем DeepSeek для анализа
                    result = await self._process_with_deepseek(query_text)
            elif self.analyzer_agent and self.sql_agent and self.viz_agent:
                # Полный путь с агентами: анализ → SQL → визуализация
                result = await self._process_with_agents(query_text)
            else:
                # Стандартный путь: используем DeepSeek для анализа
                result = await self._process_with_deepseek(query_text)
            
            # Применяем пагинацию, если она указана
            if pagination and 'data' in result:
                data_records = result['data']
                paginated_data = paginate(data_records, pagination)
                
                result['data'] = paginated_data['items']
                result['pagination'] = {
                    'total': paginated_data['total'],
                    'page': paginated_data['page'],
                    'page_size': paginated_data['page_size'],
                    'total_pages': paginated_data['total_pages']
                }
            
            # 4. Добавляем метрики производительности
            processing_time = time.time() - start_time
            result["performance"] = {
                "processing_time_ms": round(processing_time * 1000, 2),
            }
            
            # 5. Кэшируем результат (сохраняем оригинальные данные без пагинации)
            if use_cache:
                # Если была применена пагинация, сохраняем в кэш версию без пагинации
                if 'pagination' in result:
                    cache_result = {**result}
                    del cache_result['pagination']
                    # Восстанавливаем полный набор данных из оригинального запроса
                    if hasattr(self, '_original_data') and self._original_data is not None:
                        cache_result['data'] = self._original_data
                    self.cache[cache_key] = cache_result
                else:
                    self.cache[cache_key] = result
            
            return result
        
        except Exception as e:
            # Обработка ошибок с детальной информацией
            import traceback
            error_result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "performance": {
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                    "error_source": type(e).__name__
                }
            }
            return error_result
    
    async def _process_with_dashboard_service(self, query_text, matching_query):
        """
        Обрабатывает запрос с использованием сервиса Dashboard для типовых запросов
        """
        # Выполняем оптимизированный запрос через Dashboard Service
        result = await asyncio.to_thread(
            self.dashboard_service.execute_optimized_query, 
            query_text
        )
        
        # Проверяем успешность запроса
        if not result.get("success", False):
            raise Exception(f"Ошибка при выполнении запроса: {result.get('error', 'Неизвестная ошибка')}")
        
        # Получаем данные из результата
        data = result.get("data")
        if isinstance(data, pd.DataFrame):
            self._original_data = data.to_dict(orient="records")
        else:
            self._original_data = data
        
        # Обеспечиваем наличие всех необходимых полей в результате
        if "visualization" not in result:
            # Создаем визуализацию с помощью VisualizationTool
            viz_tool = VisualizationTool()
            viz_data = await asyncio.to_thread(
                viz_tool.create_visualization,
                {
                    "data": data,
                    "type": result.get("visualization_type", "line"),
                    "config": {
                        "title": result.get("title", "Визуализация данных")
                    }
                }
            )
            result["visualization"] = viz_data.get("figure", {})
        
        # Добавляем отсутствующие поля, если их нет
        if "explanation" not in result:
            result["explanation"] = f"Запрос выполнен на основе предопределенного шаблона '{matching_query.get('name')}'"
        
        if "success" not in result:
            result["success"] = True
        
        return result
    
    async def _process_with_agents(self, query_text):
        """
        Обрабатывает запрос с использованием цепочки агентов (Analyzer → SQL → Visualizer)
        """
        # Шаг 1: Анализ запроса пользователя
        analysis = await self.analyzer_agent.process_query_async(query_text)
        
        # Шаг 2: Генерация SQL-запроса
        sql_result = await self.sql_agent.generate_sql_async(analysis)
        
        # Проверка наличия SQL-запроса
        if not sql_result.get("sql_query"):
            raise Exception("Не удалось сгенерировать SQL-запрос")
        
        # Шаг 3: Выполнение SQL-запроса
        db_result = await asyncio.to_thread(self.db_tool.execute_query, sql_result["sql_query"])
        
        if not db_result["success"]:
            raise Exception(f"Ошибка базы данных: {db_result['error']}")
        
        # Получение данных из результата запроса
        data = db_result["data"]
        self._original_data = data.to_dict(orient="records")
        
        # Шаг 4: Генерация визуализации
        viz_result = await self.viz_agent.generate_visualization_code_async(
            data=data,
            visualization_type=analysis["visualization_type"],
            user_query=query_text
        )
        
        # Создание визуализации с помощью инструмента
        viz_tool = VisualizationTool()
        viz_data = await asyncio.to_thread(
            viz_tool.create_visualization,
            {
                "data": data,
                "type": analysis["visualization_type"],
                "config": {
                    "title": viz_result.get("title", "Визуализация данных"),
                    "xaxis_title": viz_result.get("x_axis_title"),
                    "yaxis_title": viz_result.get("y_axis_title")
                }
            }
        )
        
        # Формирование итогового результата
        result = {
            "success": True,
            "data": self._original_data,
            "visualization": viz_data.get("figure", {}),
            "sql_query": sql_result["sql_query"],
            "explanation": sql_result.get("query_explanation", ""),
            "title": viz_result.get("title", "Результаты анализа"),
            "description": viz_result.get("description", "")
        }
        
        return result
    
    async def _process_with_deepseek(self, query_text):
        """
        Обрабатывает запрос с использованием DeepSeek для анализа
        """
        # Формируем оптимизированный промпт для DeepSeek
        prompt = f"""
        Запрос пользователя: "{query_text}"
        
        Требуется SQL-запрос к представлению test_staging.user_metrics_dashboard_optimized.
        
        Ответ ТОЛЬКО в формате JSON:
        {{
            "sql_query": "SQL-запрос к представлению",
            "title": "Заголовок для визуализации",
            "description": "Краткое описание запроса",
            "visualization_type": "line или bar или pie или table"
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
            raise Exception("Не удалось сгенерировать SQL-запрос")
        
        # Выполняем SQL-запрос
        db_result = await asyncio.to_thread(self.db_tool.execute_query, result_data["sql_query"])
        
        if not db_result["success"]:
            raise Exception(f"Ошибка базы данных: {db_result['error']}")
        
        # Получаем данные из результата
        data = db_result["data"]
        self._original_data = data.to_dict(orient="records")
        
        # Определяем тип визуализации, если он не указан
        visualization_type = result_data.get("visualization_type", "line")
        if not visualization_type:
            if len(data) <= 10 and "user_type" in data.columns:
                visualization_type = "pie"
            elif any(col for col in data.columns if col.lower() in ["month", "date", "week", "year"]):
                visualization_type = "line"
            else:
                visualization_type = "bar"
        
        # Создаем визуализацию
        viz_tool = VisualizationTool()
        viz_data = await asyncio.to_thread(
            viz_tool.create_visualization,
            {
                "data": data,
                "type": visualization_type,
                "config": {
                    "title": result_data.get("title", "Визуализация данных")
                }
            }
        )
        
        # Формируем итоговый результат
        result = {
            "success": True,
            "data": self._original_data,
            "visualization": viz_data.get("figure", {}),
            "sql_query": result_data["sql_query"],
            "explanation": result_data.get("description", ""),
            "title": result_data.get("title", "Анализ данных"),
            "description": result_data.get("description", "")
        }
        
        return result
    
    # Синхронные версии методов для совместимости
    def process_query_sync(self, query_text: str, db_metadata=None, use_cache=True, 
                          pagination: Optional[PaginationParams] = None):
        """
        Синхронная версия метода process_query
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.process_query(query_text, db_metadata, use_cache, pagination)
        )
    
    # Метод для прямого выполнения SQL запроса
    async def execute_sql_query(self, sql_query: str, pagination: Optional[PaginationParams] = None):
        """
        Выполняет произвольный SQL-запрос
        
        Args:
            sql_query: SQL-запрос для выполнения
            pagination: Параметры пагинации
            
        Returns:
            Результаты выполнения SQL-запроса
        """
        try:
            # Выполняем запрос
            db_result = await asyncio.to_thread(self.db_tool.execute_query, sql_query)
            
            if not db_result["success"]:
                return {
                    "success": False,
                    "error": db_result["error"]
                }
            
            # Получаем данные
            data = db_result["data"]
            data_records = data.to_dict(orient="records")
            
            # Сохраняем оригинальные данные для кэша
            self._original_data = data_records
            
            # Применяем пагинацию, если она указана
            if pagination:
                paginated_data = paginate(data_records, pagination)
                result = {
                    "success": True,
                    "data": paginated_data["items"],
                    "sql_query": sql_query,
                    "pagination": {
                        "total": paginated_data["total"],
                        "page": paginated_data["page"],
                        "page_size": paginated_data["page_size"],
                        "total_pages": paginated_data["total_pages"]
                    }
                }
            else:
                result = {
                    "success": True,
                    "data": data_records,
                    "sql_query": sql_query
                }
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }