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
        
        for table_name, table_data in self.db_metadata.items():
            columns = ", ".join([f"{c['name']} ({c['type']})" for c in table_data["columns"]])
            tables_info.append(f"Таблица/Представление: {table_name}\nКолонки: {columns}\n")
        
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
        Ты эксперт по анализу данных с доступом к следующим таблицам и представлениям базы данных:
        {db_info}
        
        Твоя задача - понять запрос пользователя о визуализации данных и определить, 
        какие данные нужно получить из базы данных и как их следует визуализировать.
        
        Ответ должен быть в формате JSON со следующими полями:
        {{
            "required_data": "описание данных, которые нужно получить",
            "visualization_type": "тип визуализации (bar, line, scatter, pie, table)",
            "sql_hints": "подсказки для написания SQL-запроса"
        }}
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
                    result[field] = "table"  # По умолчанию - таблица
                else:
                    result[field] = ""
        
        return result