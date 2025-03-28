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
        
        for table_name, table_data in self.db_metadata.items():
            columns = "\n  - ".join([f"{c['name']} ({c['type']})" for c in table_data["columns"]])
            tables_info.append(f"Таблица/Представление: {table_name}\nКолонки:\n  - {columns}")
            
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
                
        # Проверка SQL-запроса на основные ошибки
        if "sql_query" in result and result["sql_query"]:
            # Удаляем потенциальные обратные кавычки, если они были в ответе
            sql_query = result["sql_query"].strip('`')
            
            # Проверяем, что запрос начинается с SELECT
            if not sql_query.upper().startswith("SELECT"):
                result["sql_query"] = f"SELECT * FROM ({sql_query}) AS query"
                
            # Заменяем запрос в результате
            result["sql_query"] = sql_query
        
        return result