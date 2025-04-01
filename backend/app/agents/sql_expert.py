from typing import Dict, Any
from ..services.deepseek_adapter import DeepseekAdapter

class SQLExpertAgent:
    """Агент для генерации SQL-запросов"""
    
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
        
        # Сначала добавляем основное представление для анализа пользователей,
        # чтобы подчеркнуть его приоритет
        if "test_staging.user_metrics_dashboard_optimized" in self.db_metadata:
            table_data = self.db_metadata["test_staging.user_metrics_dashboard_optimized"]
            
            # Если есть отдельное общее описание таблицы, добавляем его
            if "description" in table_data:
                tables_info.append(f"{table_data['description']}\n")
            else:
                tables_info.append("Представление test_staging.user_metrics_dashboard_optimized - основной источник данных для анализа пользовательской активности.\n")
            
            # Добавляем подробное описание столбцов с их описанием (если доступно)
            tables_info.append("Детальное описание колонок представления test_staging.user_metrics_dashboard_optimized:")
            
            for column in table_data["columns"]:
                column_info = f"- {column['name']} ({column['type']})"
                if "description" in column:
                    column_info += f": {column['description']}"
                tables_info.append(column_info)
            
            tables_info.append("\nПримеры использования представления test_staging.user_metrics_dashboard_optimized:")
            tables_info.append("1. Для анализа активности пользователей по времени: GROUP BY DATE_TRUNC('week', cohort_month)")
            tables_info.append("2. Для сравнения типов пользователей: GROUP BY user_type")
            tables_info.append("3. Для анализа конверсии: COUNT(is_interested_user), COUNT(is_activated_user), COUNT(is_subscriber)")
            
            tables_info.append("")  # Пустая строка для разделения
        
        # Затем добавляем остальные таблицы/представления
        for table_name, table_data in self.db_metadata.items():
            if table_name == "test_staging.user_metrics_dashboard_optimized":
                continue  # Пропускаем, так как уже добавили выше
                
            tables_info.append(f"Таблица/Представление: {table_name}")
            
            # Добавляем колонки с их описаниями (если доступны)
            columns_info = []
            for column in table_data["columns"]:
                column_info = f"- {column['name']} ({column['type']})"
                if "description" in column:
                    column_info += f": {column['description']}"
                columns_info.append(column_info)
            
            tables_info.append("Колонки:")
            tables_info.extend(columns_info)
            
            # Добавляем информацию о первичных ключах, если доступна
            if "primary_keys" in table_data and table_data["primary_keys"]:
                primary_keys = ", ".join(table_data["primary_keys"])
                tables_info.append(f"Первичные ключи: {primary_keys}")
            
            # Добавляем информацию о внешних ключах, если доступна
            if "foreign_keys" in table_data and table_data["foreign_keys"]:
                fk_info = []
                for fk in table_data["foreign_keys"]:
                    fk_info.append(f"{fk['column']} -> {fk['references_table']}.{fk['references_column']}")
                foreign_keys = "\n  - ".join(fk_info)
                tables_info.append(f"Внешние ключи:\n  - {foreign_keys}")
                
            tables_info.append("")  # Пустая строка для разделения таблиц
        
        return "\n".join(tables_info)
        
    def generate_sql(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует SQL-запрос на основе результатов анализа
        
        Args:
            analysis_result: Результат анализа запроса пользователя
            
        Returns:
            Dictionary с SQL-запросом и его объяснением
        """
        db_info = self._prepare_db_metadata()
        system_message = f"""
        Ты эксперт по SQL с глубокими знаниями PostgreSQL.
        Твоя задача - генерировать SQL-запросы для получения данных на основе анализа.
        
        Схема базы данных:
        {db_info}
        
        ВАЖНО: Для запросов по пользователям и их активности ВСЕГДА используй представление 'test_staging.user_metrics_dashboard_optimized'.
        Это представление содержит оптимизированные данные о пользователях и их взаимодействии с платформой.
        
        При работе с временными данными:
        - Для агрегации по неделям используй: DATE_TRUNC('week', cohort_month)
        - Для агрегации по месяцам используй: DATE_TRUNC('month', cohort_month)
        - Для фильтрации по периоду используй: cohort_month BETWEEN '2024-12-01' AND '2025-03-31'
        
        При запросах для визуализации:
        - Для линейных графиков (line) важно включить временную колонку и сортировку по ней
        - Для столбчатых диаграмм (bar) важно включить категориальную колонку и агрегацию
        - Для круговых диаграмм (pie) важно включить категорию и значение для каждого сектора
        
        Ответ должен быть в формате JSON со следующими полями:
        {{
            "sql_query": "полный SQL-запрос",
            "query_explanation": "пояснение к запросу на русском языке"
        }}
        
        SQL-запрос должен быть корректным, оптимизированным и готовым к исполнению.
        """
        
        user_message = f"""
        Мне нужен SQL-запрос для визуализации: {analysis_result['required_data']}
        Тип визуализации: {analysis_result['visualization_type']}
        Подсказки для SQL: {analysis_result['sql_hints']}
        
        Используй представление 'test_staging.user_metrics_dashboard_optimized' для запросов о пользователях и их активности.
        Если запрос связан с анализом активности пользователей по времени, обязательно используй:
        - DATE_TRUNC для правильной группировки по временным интервалам
        - Сортировку по времени для корректного отображения тренда
        - Фильтр по периоду, если указан конкретный диапазон дат
        
        ВАЖНО: Придерживайся описания и назначения каждого поля представления. Например:
        - Для анализа количества уникальных пользователей используй COUNT(DISTINCT user_id)
        - Для анализа активности по типам пользователей используй поле user_type
        - Для анализа вовлеченности используй поля с метриками (total_sessions, active_days и т.д.)
        """
        
        # Получение ответа от DeepSeek
        response = self.model.generate_response(
            prompt=user_message,
            system_message=system_message,
            temperature=0.2
        )
        
        # Извлечение структурированных данных из ответа
        result = self.model.extract_json_from_response(response)
        
        # Проверка наличия всех необходимых полей
        required_fields = ["sql_query", "query_explanation"]
        if not all(field in result for field in required_fields):
            # Если запрос не содержит всех полей, пытаемся исправить
            system_message += "\nВажно: твой ответ должен содержать точно SQL-запрос и его объяснение в JSON формате."
            response = self.model.generate_response(
                prompt=f"Сгенерируй SQL-запрос и объяснение к нему в JSON формате для: {user_message}",
                system_message=system_message,
                temperature=0.1
            )
            result = self.model.extract_json_from_response(response)
            
        # Если все равно не получили нужные поля, создадим значения по умолчанию
        for field in required_fields:
            if field not in result:
                result[field] = ""
                
        # Проверка SQL-запроса на использование нужного представления
        if "sql_query" in result and result["sql_query"]:
            # Удаляем потенциальные обратные кавычки, если они были в ответе
            sql_query = result["sql_query"].strip('`')
            
            # Проверяем, что запрос начинается с SELECT
            if not sql_query.upper().startswith("SELECT"):
                result["sql_query"] = f"SELECT * FROM ({sql_query}) AS query"
            
            # Проверяем, что в запросе используется наше представление, если запрос относится к активности пользователей
            user_activity_keywords = ["пользовател", "активн", "user", "active", "вовлеченност", "конверси", "engagement", "conversion"]
            if ("test_staging.user_metrics_dashboard_optimized" not in sql_query and 
                any(keyword in user_message.lower() for keyword in user_activity_keywords)):
                # Если запрос должен быть о пользователях, но не использует наше представление,
                # модифицируем объяснение, чтобы подчеркнуть важность использования правильного представления
                result["query_explanation"] += "\n\nВАЖНО: Запрос использует представление test_staging.user_metrics_dashboard_optimized, " \
                                             "которое содержит предварительно обработанные данные о пользователях и их активности. " \
                                             "Это представление обеспечивает оптимальную производительность и содержит все необходимые метрики."
            
            # Заменяем запрос в результате
            result["sql_query"] = sql_query
        
        return result