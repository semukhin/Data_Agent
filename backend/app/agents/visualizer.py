from typing import Dict, Any, Optional
import pandas as pd
from ..services.deepseek_adapter import DeepseekAdapter
import json

class VisualizerAgent:
    """Агент для генерации визуализаций"""
    
    def __init__(self):
        self.model = DeepseekAdapter()
        
    def generate_visualization_code(self, 
                                   data: pd.DataFrame, 
                                   visualization_type: str, 
                                   user_query: str) -> Dict[str, Any]:
        """
        Генерирует код для визуализации данных
        
        Args:
            data: DataFrame с данными для визуализации
            visualization_type: Тип визуализации (bar, line, scatter, pie, table)
            user_query: Исходный запрос пользователя
            
        Returns:
            Dictionary с кодом для визуализации и его конфигурацией
        """
        system_message = """
        Ты эксперт по визуализации данных, специализирующийся на библиотеке Plotly.
        Твоя задача - генерировать код для создания визуализаций на основе данных.
        
        Ответ должен быть в формате JSON со следующими полями:
        {
            "plotly_code": "строка с кодом для Plotly",
            "figure_json": {
                "data": [...],  // массив объектов данных Plotly
                "layout": {...}  // объект настроек макета Plotly
            },
            "title": "заголовок для визуализации",
            "description": "краткое описание визуализации на русском языке"
        }
        
        Визуализация должна быть информативной, иметь подписи осей, легенду и соответствующий заголовок.
        """
        
        # Формируем текст с примером данных
        sample_data = data.head(5).to_dict(orient="records")
        data_shape = data.shape
        columns_info = {col: str(data[col].dtype) for col in data.columns}
        
        user_message = f"""
        Запрос пользователя: {user_query}
        Тип визуализации: {visualization_type}
        
        Структура данных:
        Количество строк: {data_shape[0]}
        Количество столбцов: {data_shape[1]}
        
        Столбцы и их типы:
        {json.dumps(columns_info, ensure_ascii=False, indent=2)}
        
        Пример данных (первые 5 строк):
        {json.dumps(sample_data, ensure_ascii=False, indent=2)}
        
        Сгенерируй код Plotly для визуализации этих данных.
        """
        
        # Получение ответа от DeepSeek
        response = self.model.generate_response(
            prompt=user_message,
            system_message=system_message,
            temperature=0.3,
            max_tokens=3000
        )
        
        # Извлечение структурированных данных из ответа
        result = self.model.extract_json_from_response(response)
        
        # Проверка наличия всех необходимых полей
        required_fields = ["plotly_code", "figure_json", "title", "description"]
        if not all(field in result for field in required_fields):
            # Если не все поля присутствуют, попробуем извлечь код и построить фигуру программно
            fallback_result = self._generate_fallback_visualization(data, visualization_type, user_query)
            
            # Объединяем результаты
            for field in required_fields:
                if field not in result and field in fallback_result:
                    result[field] = fallback_result[field]
        
        return result
    
    def _generate_fallback_visualization(self, 
                                        data: pd.DataFrame, 
                                        visualization_type: str, 
                                        user_query: str) -> Dict[str, Any]:
        """
        Создает резервную визуализацию, если основной метод не сработал
        
        Args:
            data: DataFrame с данными для визуализации
            visualization_type: Тип визуализации
            user_query: Исходный запрос пользователя
            
        Returns:
            Dictionary с кодом для визуализации
        """
        import plotly.express as px
        import plotly.graph_objects as go
        
        result = {
            "title": "Визуализация данных",
            "description": "Автоматически сгенерированная визуализация"
        }
        
        try:
            # Выбираем числовые и категориальные столбцы
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Строим визуализацию в зависимости от типа
            if visualization_type == "bar" and numeric_cols and categorical_cols:
                x = categorical_cols[0] if categorical_cols else numeric_cols[0]
                y = numeric_cols[0] if len(numeric_cols) > 0 else None
                
                if y:
                    fig = px.bar(data, x=x, y=y, title=f"{y} по {x}")
                else:
                    fig = px.bar(data, x=x, title=f"Распределение {x}")
                    
                result["plotly_code"] = f"px.bar(df, x='{x}', y='{y}', title='{result['title']}')"
                
            elif visualization_type == "line" and numeric_cols:
                if len(data.columns) >= 2:
                    x = data.columns[0]
                    y = numeric_cols[0]
                    fig = px.line(data, x=x, y=y, title=f"{y} по {x}")
                    result["plotly_code"] = f"px.line(df, x='{x}', y='{y}', title='{result['title']}')"
                else:
                    fig = px.line(data, title="Динамика значений")
                    result["plotly_code"] = f"px.line(df, title='{result['title']}')"
                    
            elif visualization_type == "scatter" and len(numeric_cols) >= 2:
                x = numeric_cols[0]
                y = numeric_cols[1]
                fig = px.scatter(data, x=x, y=y, title=f"{y} vs {x}")
                result["plotly_code"] = f"px.scatter(df, x='{x}', y='{y}', title='{result['title']}')"
                
            elif visualization_type == "pie" and categorical_cols:
                names = categorical_cols[0]
                values = numeric_cols[0] if numeric_cols else None
                
                if values:
                    fig = px.pie(data, names=names, values=values, title=f"Распределение {values} по {names}")
                    result["plotly_code"] = f"px.pie(df, names='{names}', values='{values}', title='{result['title']}')"
                else:
                    # Создаем счетчик для категорий
                    count_data = data[names].value_counts().reset_index()
                    count_data.columns = [names, 'count']
                    fig = px.pie(count_data, names=names, values='count', title=f"Распределение {names}")
                    result["plotly_code"] = f"px.pie(df['{names}'].value_counts().reset_index(), names='{names}', values='count', title='{result['title']}')"
                    
            else:
                # Таблица как резервный вариант
                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(data.columns)),
                    cells=dict(values=[data[col] for col in data.columns])
                )])
                result["plotly_code"] = "go.Figure(data=[go.Table(header=dict(values=list(df.columns)), cells=dict(values=[df[col] for col in df.columns]))])"
                
            # Обновляем результат
            result["figure_json"] = json.loads(fig.to_json())
            
            return result
            
        except Exception as e:
            # Если произошла ошибка, возвращаем пустые значения
            return {
                "plotly_code": "",
                "figure_json": {"data": [], "layout": {}},
                "title": "Ошибка при создании визуализации",
                "description": f"Не удалось создать визуализацию: {str(e)}"
            }