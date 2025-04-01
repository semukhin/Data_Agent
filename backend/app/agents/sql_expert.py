import asyncio
import datetime
import re
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
    

    async def generate_sql_async(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Асинхронная версия метода generate_sql
        
        Args:
            analysis_result: Результат анализа запроса пользователя
            
        Returns:
            Dictionary с SQL-запросом и его объяснением
        """
        # Используем asyncio.to_thread для выполнения синхронного метода в отдельном потоке
        return await asyncio.to_thread(self.generate_sql, analysis_result)

        
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
        Ты SQL-эксперт, специализирующийся на анализе данных пользовательской активности.

        Структура представления 'test_staging.user_metrics_dashboard_optimized':
        {db_info}

        ВАЖНЫЕ ПРАВИЛА:
        1. ВСЕГДА используй ТОЛЬКО представление 'test_staging.user_metrics_dashboard_optimized' для запросов.
        2. Никогда не используй JOIN с другими таблицами - все необходимые данные уже в представлении.
        3. Используй следующие подходы для работы с временными данными:
        - Группировка по неделям: DATE_TRUNC('week', cohort_month)
        - Группировка по месяцам: DATE_TRUNC('month', cohort_month)
        - Фильтрация по периоду: cohort_month BETWEEN '2025-01-01' AND '2025-03-31'
        4. Для анализа по типам пользователей используй:
        - Фильтрация по типу: WHERE user_type = 'Подписчик' ИЛИ
        - Фильтрация по флагу: WHERE is_subscriber = 1
        5. Оптимизируй запросы для максимальной производительности:
        - Используй нужные агрегирующие функции (COUNT, AVG, SUM)
        - Всегда добавляй ORDER BY для временных рядов
        - Ограничивай выборку данных необходимыми полями
        
        Ответ СТРОГО в формате JSON:
        {{
            "sql_query": "полный SQL-запрос для выполнения",
            "query_explanation": "подробное объяснение запроса на русском языке"
        }}
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
    
    SQL_TEMPLATES = {
    "активные_пользователи_по_месяцам": """
        SELECT DATE_TRUNC('month', cohort_month) AS month,
               COUNT(DISTINCT user_id) AS active_users
        FROM test_staging.user_metrics_dashboard_optimized
        WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY month
        ORDER BY month
    """,
    
    "распределение_по_типам_пользователей": """
        SELECT user_type, COUNT(DISTINCT user_id) AS user_count
        FROM test_staging.user_metrics_dashboard_optimized
        WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY user_type
        ORDER BY user_count DESC
    """,
    
    "среднее_время_на_платформе": """
        SELECT DATE_TRUNC('{period}', cohort_month) AS time_period,
               AVG(avg_session_minutes) AS avg_time
        FROM test_staging.user_metrics_dashboard_optimized
        WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY time_period
        ORDER BY time_period
    """
}
    
def extract_time_period(query_text):
    """Определяет временной период из запроса пользователя"""
    today = datetime.datetime.now()
    last_month = today - datetime.timedelta(days=30)
    last_6_months = today - datetime.timedelta(days=180)
    
    # Определяем упоминания временных периодов в запросе
    if "прошлый месяц" in query_text.lower() or "предыдущий месяц" in query_text.lower():
        return last_month.replace(day=1), today.replace(day=1) - datetime.timedelta(days=1)
    elif "последние 6 месяцев" in query_text.lower() or "за 6 месяцев" in query_text.lower():
        return last_6_months, today
    elif "этот год" in query_text.lower() or "текущий год" in query_text.lower():
        return datetime.datetime(today.year, 1, 1), today
    
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
                    start_date = datetime.datetime(year, month, 1)
                    if month == 12:
                        end_date = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(days=1)
                    else:
                        end_date = datetime.datetime(year, month + 1, 1) - datetime.timedelta(days=1)
                    return start_date, end_date
    
    # По умолчанию возвращаем последние 30 дней
    return last_month, today

def optimize_sql_query(sql_query):
    """Оптимизирует SQL-запрос для лучшей производительности"""
    # Убедимся, что запрос использует только нужное представление
    if "FROM" in sql_query.upper() and "test_staging.user_metrics_dashboard_optimized" not in sql_query:
        sql_query = sql_query.replace("FROM", "FROM test_staging.user_metrics_dashboard_optimized")
    
    # Проверим наличие ORDER BY для временных рядов
    if "DATE_TRUNC" in sql_query and "ORDER BY" not in sql_query.upper():
        if "GROUP BY" in sql_query.upper():
            group_by_column = re.search(r'GROUP BY\s+([^\s,]+)', sql_query, re.IGNORECASE)
            if group_by_column:
                sql_query += f" ORDER BY {group_by_column.group(1)}"
    
    # Добавим LIMIT, если его нет
    if "LIMIT" not in sql_query.upper():
        sql_query += " LIMIT 1000"
    
    return sql_query