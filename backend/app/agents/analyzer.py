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
        Ты эксперт по анализу данных с доступом к представлению базы данных PostgreSQL:
        {db_info}
        
        ВАЖНО: Для запросов, относящихся к пользователям, их активности и метрикам, ВСЕГДА рекомендуй использовать 
        представление 'test_staging.user_metrics_dashboard_optimized'. Это представление содержит всю необходимую 
        информацию о пользовательской активности и метриках вовлеченности, специально оптимизированную для анализа.
        
        Твоя задача - понять запрос пользователя о визуализации данных и определить, 
        какие данные нужно получить из базы данных и как их следует визуализировать.
        
        При анализе запросов о пользователях и их активности обращай внимание на:
        1. Временной аспект (по дням, неделям, месяцам) - используй поле cohort_month
        2. Тип пользователей (подписчики, активированные, заинтересованные) - используй поле user_type
        3. Метрики вовлеченности (сессии, время, просмотры) - используй соответствующие поля из представления
        
        Ответ должен быть в формате JSON со следующими полями:
        {{
            "required_data": "описание данных, которые нужно получить",
            "visualization_type": "тип визуализации (bar, line, scatter, pie, table)",
            "sql_hints": "подсказки для написания SQL-запроса"
        }}
        
        Рекомендации по выбору типа визуализации:
        - Для анализа тренда во времени (динамика метрик): 'line'
        - Для сравнения метрик между категориями: 'bar'
        - Для распределения значений по категориям: 'pie'
        - Для анализа корреляций между метриками: 'scatter'
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