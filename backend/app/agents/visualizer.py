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
        Твоя задача - генерировать код для создания информативных и красивых визуализаций на основе данных.
        
        Контекст данных:
        Данные относятся к платформе Atlantix и отражают активность пользователей, их вовлеченность и поведение.
        
        Основные понятия:
        - Пользователи делятся на типы: "Подписчик" (платящий), "Активированный" (использует ключевые функции), "Заинтересованный" (только просматривает контент)
        - Когортный анализ основан на месяце первого посещения пользователем платформы (cohort_month)
        - Ключевые метрики вовлеченности: количество сессий, время на платформе, просмотры технологий и бизнес-планов
        
        Рекомендации по визуализации разных типов данных:
        1. Временные ряды (line):
           - Используйте понятные подписи осей (например, "Неделя" вместо "creation_week", "Активные пользователи" вместо "user_count")
           - Добавьте сетку для облегчения восприятия
           - Используйте плавное сглаживание для трендов
           - Используйте синюю цветовую гамму (#1976d2, #90caf9, #1565c0)
        
        2. Столбчатые диаграммы (bar):
           - Сортируйте значения от большего к меньшему (если это не временной ряд)
           - Используйте цветовую гамму синего (#1976d2) для позитивных метрик
           - Добавляйте подписи значений на столбцах
        
        3. Круговые диаграммы (pie):
           - Используйте их только для распределения категорий (например, типов пользователей)
           - Добавляйте проценты в подписи
           - Используйте согласованную цветовую схему (синяя гамма)
        
        4. Диаграммы рассеяния (scatter):
           - Используйте для корреляционного анализа метрик
           - Добавляйте линию тренда
           - Используйте размер точек для отображения третьей переменной
        
        Ответ должен быть в формате JSON со следующими полями:
        {
            "plotly_code": "строка с кодом для Plotly",
            "figure_json": {
                "data": [...],  // массив объектов данных Plotly
                "layout": {...}  // объект настроек макета Plotly
            },
            "title": "заголовок для визуализации",
            "description": "краткое описание визуализации на русском языке",
            "x_axis_title": "название оси X",
            "y_axis_title": "название оси Y"
        }
        
        Визуализация должна быть информативной, иметь подписи осей, легенду и соответствующий заголовок.
        """
        
        # Формируем текст с примером данных
        sample_data = data.head(5).to_dict(orient="records")
        data_shape = data.shape
        columns_info = {col: str(data[col].dtype) for col in data.columns}
        
        # Определяем русские названия для колонок (если они есть в данных)
        column_translations = {
            "user_id": "ID пользователя",
            "cohort_month": "Когортный месяц",
            "user_type": "Тип пользователя",
            "technology_views": "Просмотры технологий",
            "technology_sessions": "Сессии с просмотром технологий",
            "business_plan_clicks": "Клики по бизнес-планам",
            "custom_business_plan_views": "Просмотры кастомных бизнес-планов",
            "discovery_views": "Просмотры страницы 'Discover'",
            "collection_views": "Просмотры коллекций",
            "search_queries": "Поисковые запросы",
            "total_sessions": "Всего сессий",
            "active_days": "Активные дни",
            "avg_session_minutes": "Среднее время сессии (мин)",
            "total_platform_minutes": "Всего времени на платформе (мин)",
            "total_discover_minutes": "Всего времени на 'Discover' (мин)",
            "minutes_to_first_tech_view": "Минут до первого просмотра технологии",
            "minutes_to_first_favorites": "Минут до первого добавления в избранное",
            "is_interested_user": "Заинтересованный пользователь",
            "is_activated_user": "Активированный пользователь",
            "is_subscriber": "Подписчик",
            "creation_week": "Неделя",
            "user_count": "Количество пользователей",
            "count": "Количество"
        }
        
        # Определяем бизнес-контекст для колонок в данных
        column_contexts = {}
        for col in data.columns:
            if col in column_translations:
                column_contexts[col] = column_translations[col]
            elif "week" in col.lower() or "month" in col.lower() or "date" in col.lower():
                column_contexts[col] = "Временной период"
            elif "count" in col.lower() or "qty" in col.lower() or "number" in col.lower():
                column_contexts[col] = "Количественная метрика"
            elif "avg" in col.lower() or "mean" in col.lower() or "average" in col.lower():
                column_contexts[col] = "Средняя величина"
            elif "total" in col.lower() or "sum" in col.lower():
                column_contexts[col] = "Суммарная величина"
        
        user_message = f"""
        Запрос пользователя: {user_query}
        Тип визуализации: {visualization_type}
        
        Бизнес-контекст для колонок:
        {json.dumps(column_contexts, ensure_ascii=False, indent=2)}
        
        Структура данных:
        Количество строк: {data_shape[0]}
        Количество столбцов: {data_shape[1]}
        
        Столбцы и их типы:
        {json.dumps(columns_info, ensure_ascii=False, indent=2)}
        
        Пример данных (первые 5 строк):
        {json.dumps(sample_data, ensure_ascii=False, indent=2)}
        
        Сгенерируй код Plotly для визуализации этих данных, учитывая их бизнес-смысл и рекомендации по типам визуализаций.
        Используй русские названия для подписей осей и легенд, если это возможно.
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
            fallback_result = self._generate_fallback_visualization(data, visualization_type, user_query, column_translations)
            
            # Объединяем результаты
            for field in required_fields:
                if field not in result and field in fallback_result:
                    result[field] = fallback_result[field]
        
        # Убедимся, что заголовок визуализации на русском
        if "title" in result and not any(char in result["title"] for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
            # Если в заголовке нет русских букв, пробуем перевести
            translated_title = self._translate_title(result["title"], user_query)
            if translated_title:
                result["title"] = translated_title
        
        return result
    
    def _translate_title(self, title: str, user_query: str) -> Optional[str]:
        """
        Пытается перевести заголовок на русский язык, если он на английском
        
        Args:
            title: Оригинальный заголовок
            user_query: Запрос пользователя для контекста
            
        Returns:
            Переведенный заголовок или None, если перевод не требуется
        """
        # Словарь базовых английских терминов и их русских эквивалентов
        translations = {
            "users": "пользователи",
            "active users": "активные пользователи",
            "weekly": "еженедельно",
            "monthly": "ежемесячно",
            "by week": "по неделям",
            "by month": "по месяцам",
            "activity": "активность",
            "sessions": "сессии",
            "views": "просмотры",
            "engagement": "вовлеченность",
            "conversion": "конверсия",
            "distribution": "распределение",
            "time spent": "затраченное время",
            "technology": "технологии",
            "business plan": "бизнес-план"
        }
        
        # Если в запросе есть русские слова, извлекаем существительные для заголовка
        if any(char in user_query for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
            # Простая эвристика: если в запросе есть "график" или "диаграмма"
            if "график" in user_query.lower() or "диаграмма" in user_query.lower():
                # Пытаемся извлечь фразы после "график" или "диаграмма"
                for prefix in ["график", "диаграмма"]:
                    if prefix in user_query.lower():
                        pos = user_query.lower().find(prefix) + len(prefix)
                        phrase = user_query[pos:].strip()
                        if phrase.startswith("активных пользователей"):
                            return "Активные пользователи по неделям"
                        elif "активных" in phrase and "неделям" in phrase:
                            return "Активные пользователи по неделям"
                        elif "активных" in phrase and "месяцам" in phrase:
                            return "Активные пользователи по месяцам"
                        elif "по типам" in phrase:
                            return "Распределение пользователей по типам"
        
        # Проверяем ключевые фразы из запроса и формируем заголовок
        if "актив" in user_query.lower() and "пользовател" in user_query.lower():
            if "недел" in user_query.lower():
                return "Активные пользователи по неделям"
            elif "месяц" in user_query.lower() or "месяц" in user_query.lower():
                return "Активные пользователи по месяцам"
            else:
                return "Активные пользователи"
        
        # Пытаемся перевести английский заголовок
        translated = title
        for eng, rus in translations.items():
            translated = translated.replace(eng, rus)
        
        # Если произошли изменения, значит был перевод
        if translated != title:
            return translated
        
        # Возвращаем оригинальный заголовок, если перевод не требуется
        return None
    
    def _generate_fallback_visualization(self, 
                                    data: pd.DataFrame, 
                                    visualization_type: str, 
                                    user_query: str,
                                    column_translations: Dict[str, str]) -> Dict[str, Any]:
        """
        Создает резервную визуализацию, если основной метод не сработал
        
        Args:
            data: DataFrame с данными для визуализации
            visualization_type: Тип визуализации
            user_query: Исходный запрос пользователя
            column_translations: Словарь с переводами названий колонок
            
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
            # Устанавливаем заголовок на основе запроса
            if "актив" in user_query.lower() and "пользовател" in user_query.lower():
                if "недел" in user_query.lower():
                    result["title"] = "Активные пользователи по неделям"
                    result["x_axis_title"] = "Неделя"
                    result["y_axis_title"] = "Количество пользователей"
                elif "месяц" in user_query.lower() or "месяц" in user_query.lower():
                    result["title"] = "Активные пользователи по месяцам"
                    result["x_axis_title"] = "Месяц"
                    result["y_axis_title"] = "Количество пользователей"
                else:
                    result["title"] = "Активные пользователи"
            
            # Переводим названия колонок для отображения
            axis_labels = {}
            for col in data.columns:
                if col in column_translations:
                    axis_labels[col] = column_translations[col]
            
            # Выбираем числовые и категориальные столбцы
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            # Определяем временные столбцы
            time_cols = [col for col in data.columns if any(term in col.lower() for term in ['date', 'time', 'week', 'month', 'day'])]
            
            # Стандартные настройки макета для удаления брендирования
            layout_config = {
                "plot_bgcolor": 'white',
                "font": dict(family="Arial, sans-serif", size=12),
                "title_font": dict(size=16),
                "showlegend": True,
                # Удаляем атрибуцию Plotly из макета
                "modebar": {
                    "remove": ["sendDataToCloud", "autoScale2d", "resetScale2d", "toggleSpikelines",
                            "hoverClosestCartesian", "hoverCompareCartesian"]
                }
            }
            
            # Строим визуализацию в зависимости от типа
            if visualization_type == "line" and time_cols and numeric_cols:
                x = time_cols[0]  # Берем первый временной столбец
                y = [col for col in numeric_cols if col != x][0] if x in numeric_cols and len(numeric_cols) > 1 else numeric_cols[0]
                
                x_title = axis_labels.get(x, x)
                y_title = axis_labels.get(y, y)
                
                fig = px.line(data, x=x, y=y, title=result["title"],
                            labels={x: x_title, y: y_title},
                            template="plotly_white",
                            color_discrete_sequence=['#1976d2'])
                
                # Добавляем стандартные настройки и убираем брендирование
                fig.update_layout(**layout_config)
                
                # Дополнительные настройки для линейного графика
                fig.update_layout(
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        title_font=dict(size=14)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        title_font=dict(size=14)
                    )
                )
                
                # Обновляем код для компонента VisualizationPanel (включая config для удаления брендирования)
                result["plotly_code"] = f"""
                // Создание графика
                const fig = px.line(df, x='{x}', y='{y}', 
                                title='{result['title']}', 
                                labels={{'{x}': '{x_title}', '{y}': '{y_title}'}},
                                template='plotly_white', 
                                color_discrete_sequence=['#1976d2']);
                
                // Обновление макета для удаления брендирования Plotly
                fig.update_layout({{
                    plot_bgcolor: 'white',
                    font: {{family: 'Arial, sans-serif', size: 12}},
                    title_font: {{size: 16}},
                    xaxis: {{
                        showgrid: true,
                        gridcolor: 'lightgray',
                        title_font: {{size: 14}}
                    }},
                    yaxis: {{
                        showgrid: true,
                        gridcolor: 'lightgray',
                        title_font: {{size: 14}}
                    }}
                }});
                
                // Конфигурация для удаления логотипа Plotly
                const config = {{
                    displaylogo: false,
                    modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'resetScale2d', 'toggleSpikelines',
                                        'hoverClosestCartesian', 'hoverCompareCartesian'],
                    responsive: true
                }};
                
                return {{figure: fig, config: config}};
                """
                
                result["x_axis_title"] = x_title
                result["y_axis_title"] = y_title
                
            elif visualization_type == "bar":
                # ... (аналогично для других типов визуализаций)
                # Определяем, какие колонки использовать для X и Y
                if categorical_cols and numeric_cols:
                    x = categorical_cols[0]
                    y = numeric_cols[0]
                elif time_cols and numeric_cols:
                    x = time_cols[0]
                    y = [col for col in numeric_cols if col != x][0] if x in numeric_cols and len(numeric_cols) > 1 else numeric_cols[0]
                else:
                    x = data.columns[0]
                    y = data.columns[1] if len(data.columns) > 1 else data.columns[0]
                
                x_title = axis_labels.get(x, x)
                y_title = axis_labels.get(y, y)
                
                fig = px.bar(data, x=x, y=y, title=result["title"],
                        labels={x: x_title, y: y_title},
                        template="plotly_white",
                        color_discrete_sequence=['#1976d2'])
                
                # Добавляем стандартные настройки и убираем брендирование
                fig.update_layout(**layout_config)
                
                # Дополнительные настройки для столбчатой диаграммы
                fig.update_layout(
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        title_font=dict(size=14)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        title_font=dict(size=14)
                    )
                )
                
                # Обновляем код для компонента VisualizationPanel
                result["plotly_code"] = f"""
                // Создание графика
                const fig = px.bar(df, x='{x}', y='{y}', 
                                title='{result['title']}', 
                                labels={{'{x}': '{x_title}', '{y}': '{y_title}'}}, 
                                template='plotly_white', 
                                color_discrete_sequence=['#1976d2']);
                
                // Обновление макета для удаления брендирования Plotly
                fig.update_layout({{
                    plot_bgcolor: 'white',
                    font: {{family: 'Arial, sans-serif', size: 12}},
                    title_font: {{size: 16}},
                    xaxis: {{
                        showgrid: true,
                        gridcolor: 'lightgray',
                        title_font: {{size: 14}}
                    }},
                    yaxis: {{
                        showgrid: true,
                        gridcolor: 'lightgray',
                        title_font: {{size: 14}}
                    }}
                }});
                
                // Конфигурация для удаления логотипа Plotly
                const config = {{
                    displaylogo: false,
                    modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'resetScale2d', 'toggleSpikelines',
                                        'hoverClosestCartesian', 'hoverCompareCartesian'],
                    responsive: true
                }};
                
                return {{figure: fig, config: config}};
                """
                
                result["x_axis_title"] = x_title
                result["y_axis_title"] = y_title
            
            # Добавьте аналогичный код для других типов визуализаций (pie, scatter, table)...
            
            # Добавляем JSON-представление фигуры в результат
            result["figure_json"] = json.loads(fig.to_json())
            
            # Добавляем конфигурацию для удаления брендирования
            result["config"] = {
                "displaylogo": False,
                "modeBarButtonsToRemove": ['sendDataToCloud', 'autoScale2d', 'resetScale2d', 'toggleSpikelines',
                                        'hoverClosestCartesian', 'hoverCompareCartesian'],
                "responsive": True
            }
            
            # Добавляем описание визуализации если его нет
            if "description" not in result or not result["description"]:
                if visualization_type == "line" and "x_axis_title" in result and "y_axis_title" in result:
                    result["description"] = f"График показывает изменение {result['y_axis_title'].lower()} по {result['x_axis_title'].lower()}. Данные представлены в виде линейного графика для наглядного отображения тренда."
                elif visualization_type == "bar" and "x_axis_title" in result and "y_axis_title" in result:
                    result["description"] = f"Столбчатая диаграмма показывает {result['y_axis_title'].lower()} по {result['x_axis_title'].lower()}. Высота каждого столбца соответствует значению показателя."
            
            return result
            
        except Exception as e:
            # Если произошла ошибка, возвращаем пустые значения
            return {
                "plotly_code": "",
                "figure_json": {"data": [], "layout": {}},
                "config": {
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ['sendDataToCloud', 'autoScale2d', 'resetScale2d'],
                    "responsive": True
                },
                "title": "Ошибка при создании визуализации",
                "description": f"Не удалось создать визуализацию: {str(e)}"
            }