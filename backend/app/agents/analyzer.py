import asyncio
from typing import Dict, Any
from ..services.deepseek_adapter import DeepseekAdapter

class AnalyzerAgent:
    """Агент для анализа запросов пользователя"""
    
    def __init__(self, db_metadata):
        self.db_metadata = db_metadata
        self.model = DeepseekAdapter()
        
    def _prepare_db_metadata(self) -> str:
        """
        Подготавливает метаданные базы данных для включения в запрос
        
        Returns:
            Строка с форматированными метаданными базы данных
        """
        tables_info = []
        
        # Сначала добавляем наше ключевое представление с подробным описанием
        if "test_staging.user_metrics_dashboard_optimized" in self.db_metadata:
            table_data = self.db_metadata["test_staging.user_metrics_dashboard_optimized"]
            
            # Если есть отдельное общее описание таблицы, добавляем его
            if "description" in table_data:
                tables_info.append(f"{table_data['description']}\n")
            
            # Добавляем информацию о колонках с их описанием
            tables_info.append("Детальная информация о колонках представления test_staging.user_metrics_dashboard_optimized:")
            
            for column in table_data["columns"]:
                column_info = f"- {column['name']} ({column['type']})"
                if "description" in column:
                    column_info += f": {column['description']}"
                tables_info.append(column_info)
            
            # Добавляем примеры типичных запросов к представлению
            tables_info.append("\nТипичные запросы к представлению test_staging.user_metrics_dashboard_optimized:")
            tables_info.append("1. Анализ активности по времени: GROUP BY DATE_TRUNC('week', cohort_month)")
            tables_info.append("2. Анализ по типам пользователей: GROUP BY user_type")
            tables_info.append("3. Анализ метрик вовлеченности: AVG(total_sessions), AVG(active_days), AVG(avg_session_minutes)")
            
            tables_info.append("")  # Пустая строка для разделения
        
        # Затем добавляем остальные таблицы с базовым описанием
        for table_name, table_data in self.db_metadata.items():
            if table_name == "test_staging.user_metrics_dashboard_optimized":
                continue  # Пропускаем, так как уже добавили выше
                
            # Добавляем базовую информацию о таблице/представлении
            table_info = f"Таблица/Представление: {table_name}\nКолонки: "
            
            # Собираем информацию о колонках
            columns = []
            for column in table_data["columns"]:
                column_info = f"{column['name']} ({column['type']})"
                if "description" in column:
                    column_info += f" - {column['description']}"
                columns.append(column_info)
            
            table_info += ", ".join(columns)
            tables_info.append(table_info)
        
        return "\n".join(tables_info)
    
    async def process_query_async(self, user_query: str) -> Dict[str, Any]:
        """
        Асинхронная версия метода process_query
        
        Args:
            user_query: Текстовый запрос пользователя
            
        Returns:
            Dictionary с результатами анализа
        """
        return await asyncio.to_thread(self.process_query, user_query)

        
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Анализирует запрос пользователя и определяет тип визуализации и требуемые данные
        
        Args:
            user_query: Текстовый запрос пользователя
            
        Returns:
            Dictionary с результатами анализа
        """
        # Подготовка системного промпта с метаданными БД
        db_info = self._prepare_db_metadata()
        system_message = f"""
        Ты аналитик данных с фокусом на анализ пользовательской активности на платформе Atlantix.

        Основное представление данных - 'test_staging.user_metrics_dashboard_optimized', которое содержит следующие столбцы:
        {db_info}

        ОБРАТИ ВНИМАНИЕ:
        1. Для любого анализа пользовательской активности ВСЕГДА используй ТОЛЬКО представление 'test_staging.user_metrics_dashboard_optimized'.
        2. "Подписчик", "Активированный" и "Заинтересованный" - это значения столбца user_type. Также доступны флаги is_subscriber, is_activated_user и is_interested_user для фильтрации.
        3. cohort_month - это месяц, когда пользователь впервые посетил платформу (timestamp).
        4. При работе с временными данными всегда используй правильные функции SQL для группировки: DATE_TRUNC('month', cohort_month) или DATE_TRUNC('week', cohort_month).

        Твоя задача - определить:
        1. Какие данные нужно получить из представления
        2. Какой тип визуализации лучше всего подходит
        3. Какие подсказки нужны для SQL-запроса

        Ответ ОБЯЗАТЕЛЬНО в формате JSON:
        {{
            "required_data": "подробное описание какие данные нужно получить",
            "visualization_type": "тип визуализации (bar, line, pie, table)",
            "sql_hints": "подсказки для SQL-запроса включая рекомендуемые группировки и фильтры"
        }}

        Рекомендации по типам визуализации:
        - Для анализа трендов во времени: 'line'
        - Для сравнения метрик по категориям: 'bar'
        - Для распределения долей: 'pie'
        - Для детального просмотра данных: 'table'
        """
        
        # Получение ответа от DeepSeek
        response = self.model.generate_response(
            prompt=user_query,
            system_message=system_message,
            temperature=0.3
        )
        
        # Извлечение структурированных данных из ответа
        result = self.model.extract_json_from_response(response)
        
        # Проверка наличия всех необходимых полей
        required_fields = ["required_data", "visualization_type", "sql_hints"]
        if not all(field in result for field in required_fields):
            # Если не все поля присутствуют, попробуем еще раз с более явной инструкцией
            system_message += "\nВажно: твой ответ должен содержать все указанные поля в формате JSON."
            response = self.model.generate_response(
                prompt=f"Проанализируй следующий запрос и верни только JSON: {user_query}",
                system_message=system_message,
                temperature=0.2
            )
            result = self.model.extract_json_from_response(response)
        
        # Если все равно не получили нужные поля, создадим значения по умолчанию
        for field in required_fields:
            if field not in result:
                if field == "visualization_type":
                    # Определяем тип визуализации на основе ключевых слов в запросе
                    if any(keyword in user_query.lower() for keyword in ["тренд", "динамика", "по времени", "по неделям", "по месяцам"]):
                        result[field] = "line"
                    elif any(keyword in user_query.lower() for keyword in ["сравни", "сравнение", "распределение"]):
                        result[field] = "bar"
                    elif any(keyword in user_query.lower() for keyword in ["доля", "процент", "круговая"]):
                        result[field] = "pie"
                    elif any(keyword in user_query.lower() for keyword in ["связь", "корреляция", "зависимость"]):
                        result[field] = "scatter"
                    else:
                        result[field] = "line"  # По умолчанию линейный график
                else:
                    result[field] = ""
        
        # Проверяем и улучшаем SQL подсказки
        if "sql_hints" in result:
            # Если в подсказках нет упоминания о представлении, добавляем его
            if "test_staging.user_metrics_dashboard_optimized" not in result["sql_hints"]:
                user_activity_keywords = ["пользовател", "активност", "вовлеченност", "конверси", "юзер", "метрик"]
                if any(keyword in user_query.lower() for keyword in user_activity_keywords):
                    result["sql_hints"] += " Используйте представление test_staging.user_metrics_dashboard_optimized для анализа пользовательских данных."
            
            # Определяем временной период из запроса
            if any(period in user_query.lower() for period in ["по неделям", "еженедельно", "недельный"]):
                if "DATE_TRUNC('week'" not in result["sql_hints"]:
                    result["sql_hints"] += " Используйте DATE_TRUNC('week', cohort_month) для группировки по неделям."
            elif any(period in user_query.lower() for period in ["по месяцам", "ежемесячно", "месячный"]):
                if "DATE_TRUNC('month'" not in result["sql_hints"]:
                    result["sql_hints"] += " Используйте DATE_TRUNC('month', cohort_month) для группировки по месяцам."
            
            # Добавляем рекомендации для конкретных видов анализа
            if "тип" in user_query.lower() and "пользователь" in user_query.lower():
                result["sql_hints"] += " Используйте поле user_type или флаги is_interested_user, is_activated_user, is_subscriber для сегментации пользователей."
            
            if "конверсия" in user_query.lower() or "воронка" in user_query.lower():
                result["sql_hints"] += " Для анализа конверсионной воронки используйте COUNT(is_interested_user), COUNT(is_activated_user), COUNT(is_subscriber)."
        
        return result