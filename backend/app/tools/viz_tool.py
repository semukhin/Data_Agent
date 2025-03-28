import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from typing import Dict, Any

class VisualizationTool:
    """Инструмент для создания визуализаций данных"""
    
    def __init__(self):
        pass
        
    def create_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создает визуализацию данных
        
        Args:
            params: Параметры для создания визуализации
                - data: DataFrame или словарь с данными
                - type: Тип визуализации (bar, line, scatter, pie, table)
                - config: Дополнительные параметры конфигурации
                
        Returns:
            Dictionary с результатом создания визуализации
        """
        try:
            data = params.get("data")
            viz_type = params.get("type", "table")  # По умолчанию таблица
            config = params.get("config", {})
            
            # Преобразование словаря в DataFrame, если необходимо
            if isinstance(data, dict) or isinstance(data, list):
                data = pd.DataFrame(data)
            
            # Проверка на пустые данные
            if data.empty:
                return {
                    "success": False,
                    "figure": None,
                    "error": "Нет данных для визуализации"
                }
            
            # Создание визуализации в зависимости от типа
            if viz_type == "bar":
                x = config.get("x", data.columns[0])
                y = config.get("y", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                title = config.get("title", f"Столбчатая диаграмма: {y} по {x}")
                
                fig = px.bar(data, x=x, y=y, title=title, 
                           color=config.get("color"),
                           labels=config.get("labels", {}),
                           text=config.get("text"))
                
            elif viz_type == "line":
                x = config.get("x", data.columns[0])
                y = config.get("y", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                title = config.get("title", f"Линейный график: {y} по {x}")
                
                fig = px.line(data, x=x, y=y, title=title,
                            color=config.get("color"),
                            line_dash=config.get("line_dash"),
                            labels=config.get("labels", {}))
                
            elif viz_type == "scatter":
                x = config.get("x", data.columns[0])
                y = config.get("y", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                title = config.get("title", f"Диаграмма рассеяния: {y} и {x}")
                
                fig = px.scatter(data, x=x, y=y, title=title,
                               color=config.get("color"),
                               size=config.get("size"),
                               hover_name=config.get("hover_name"),
                               labels=config.get("labels", {}))
                
            elif viz_type == "pie":
                names = config.get("names", data.columns[0])
                values = config.get("values", data.columns[1] if len(data.columns) > 1 else None)
                title = config.get("title", f"Круговая диаграмма: {values} по {names}")
                
                if values:
                    fig = px.pie(data, names=names, values=values, title=title,
                               hole=config.get("hole", 0),
                               labels=config.get("labels", {}))
                else:
                    # Используем подсчет значений в единственном столбце
                    count_data = data[names].value_counts().reset_index()
                    count_data.columns = [names, 'count']
                    fig = px.pie(count_data, names=names, values='count', title=title,
                               hole=config.get("hole", 0),
                               labels=config.get("labels", {}))
                
            elif viz_type == "heatmap":
                x = config.get("x", data.columns[0])
                y = config.get("y", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                z = config.get("z", data.columns[2] if len(data.columns) > 2 else None)
                title = config.get("title", "Тепловая карта")
                
                if z:
                    # Если у нас есть три столбца (x, y, значение)
                    # Преобразуем данные в формат pivot
                    pivot_data = data.pivot_table(index=y, columns=x, values=z, aggfunc=config.get("aggfunc", "mean"))
                    fig = px.imshow(pivot_data, title=title,
                                  labels=config.get("labels", {}),
                                  color_continuous_scale=config.get("color_scale", "Viridis"))
                else:
                    # Создаем матрицу корреляции числовых столбцов
                    corr_data = data.select_dtypes(include=['number']).corr()
                    fig = px.imshow(corr_data, title="Матрица корреляции",
                                  labels=config.get("labels", {}),
                                  color_continuous_scale=config.get("color_scale", "RdBu_r"),
                                  text_auto=True)
                
            else:  # Таблица как резервный вариант
                # Ограничение количества строк для отображения
                max_rows = config.get("max_rows", 20)
                display_data = data.head(max_rows)
                
                # Создание таблицы
                fig = go.Figure(data=[go.Table(
                    header=dict(
                        values=list(display_data.columns),
                        fill_color='paleturquoise',
                        align='left'
                    ),
                    cells=dict(
                        values=[display_data[col] for col in display_data.columns],
                        fill_color='lavender',
                        align='left'
                    )
                )])
                
                fig.update_layout(title=config.get("title", "Таблица данных"))
            
            # Общие настройки макета
            fig.update_layout(
                template=config.get("template", "plotly_white"),
                legend_title=config.get("legend_title", None),
                font=dict(family="Arial, sans-serif", size=12),
                margin=dict(l=60, r=40, t=60, b=60)
            )
            
            # Настройки осей, если они указаны
            if "xaxis_title" in config:
                fig.update_xaxes(title_text=config["xaxis_title"])
            if "yaxis_title" in config:
                fig.update_yaxes(title_text=config["yaxis_title"])
            
            return {
                "success": True,
                "figure": json.loads(fig.to_json()),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "figure": None,
                "error": str(e)
            }