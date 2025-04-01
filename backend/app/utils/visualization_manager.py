import pandas as pd
from typing import Dict, Any, Optional
import json

import plotly

# Оптимизированные шаблоны визуализаций
VISUALIZATION_TEMPLATES = {
    "line_time_series": {
        "layout": {
            "title": "{title}",
            "xaxis": {
                "title": "{x_title}",
                "showgrid": True,
                "gridcolor": "lightgray"
            },
            "yaxis": {
                "title": "{y_title}",
                "showgrid": True,
                "gridcolor": "lightgray"
            },
            "font": {
                "family": "Arial, sans-serif",
                "size": 12
            },
            "margin": {"l": 60, "r": 40, "t": 60, "b": 60},
            "hovermode": "closest",
            "plot_bgcolor": "white"
        },
        "config": {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                'sendDataToCloud', 'autoScale2d', 'resetScale2d', 'toggleSpikelines',
                'hoverClosestCartesian', 'hoverCompareCartesian'
            ],
            "responsive": True
        }
    },
    
    "bar_chart": {
        "layout": {
            "title": "{title}",
            "xaxis": {
                "title": "{x_title}",
                "showgrid": False
            },
            "yaxis": {
                "title": "{y_title}",
                "showgrid": True,
                "gridcolor": "lightgray"
            },
            "font": {
                "family": "Arial, sans-serif",
                "size": 12
            },
            "margin": {"l": 60, "r": 40, "t": 60, "b": 60},
            "plot_bgcolor": "white"
        },
        "config": {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                'sendDataToCloud', 'autoScale2d', 'resetScale2d'
            ],
            "responsive": True
        }
    },
    
    "pie_chart": {
        "layout": {
            "title": "{title}",
            "font": {
                "family": "Arial, sans-serif",
                "size": 12
            },
            "margin": {"l": 20, "r": 20, "t": 60, "b": 20},
            "showlegend": True,
            "legend": {
                "orientation": "v",
                "x": 1.05,
                "y": 0.5
            }
        },
        "config": {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                'sendDataToCloud', 'zoom2d', 'pan2d', 'select2d', 'lasso2d'
            ],
            "responsive": True
        }
    },
    
    "table": {
        "layout": {
            "title": "{title}",
            "font": {
                "family": "Arial, sans-serif",
                "size": 12
            },
            "margin": {"l": 20, "r": 20, "t": 60, "b": 20}
        },
        "config": {
            "displaylogo": False,
            "responsive": True
        }
    }
}

def create_optimized_visualization(data, viz_type, query_type, object_type, title=""):
    """
    Создает оптимизированную визуализацию на основе шаблонов
    """
    import plotly.graph_objects as go
    import plotly.express as px
    
    # Если данных нет или они пустые, возвращаем пустой график
    if data is None or len(data) == 0:
        return {
            "data": [],
            "layout": {
                "title": "Нет данных для отображения",
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                    "text": "Нет данных для отображения",
                    "showarrow": False,
                    "font": {"size": 14}
                }]
            }
        }
    
    # Выбор шаблона в зависимости от типа визуализации
    if viz_type == "line":
        template = VISUALIZATION_TEMPLATES["line_time_series"]
        
        # Определяем колонки для осей
        time_cols = [col for col in data.columns if any(term in col.lower() for term in ['date', 'time', 'period', 'month', 'week'])]
        numeric_cols = [col for col in data.columns if data[col].dtype.kind in 'if' and col not in time_cols]
        
        x_col = time_cols[0] if time_cols else data.columns[0]
        y_col = numeric_cols[0] if numeric_cols else (data.columns[1] if len(data.columns) > 1 else data.columns[0])
        
        # Форматируем заголовки
        x_title = x_col.replace('_', ' ').title() if not title else "Период времени"
        y_title = y_col.replace('_', ' ').title() if not title else "Значение"
        
        # Создаем фигуру
        fig = px.line(
            data, 
            x=x_col, 
            y=y_col,
            markers=True,
            line_shape='linear',
            color_discrete_sequence=['#1976d2']
        )
        
        # Применяем шаблон с форматированием
        layout = template["layout"].copy()
        layout["title"] = title or f"Динамика {y_title.lower()} по времени"
        layout["xaxis"]["title"] = x_title
        layout["yaxis"]["title"] = y_title
        
        fig.update_layout(layout)
        
        result = {
            "data": fig.data,
            "layout": fig.layout,
            "config": template["config"]
        }
        
    elif viz_type == "bar":
        template = VISUALIZATION_TEMPLATES["bar_chart"]
        
        # Определяем колонки для осей
        categorical_cols = [col for col in data.columns if data[col].dtype == 'object']
        numeric_cols = [col for col in data.columns if data[col].dtype.kind in 'if' and col not in categorical_cols]
        
        x_col = categorical_cols[0] if categorical_cols else data.columns[0]
        y_col = numeric_cols[0] if numeric_cols else (data.columns[1] if len(data.columns) > 1 else data.columns[0])
        
        # Сортируем данные по значению, если это не временной ряд
        if not any(term in x_col.lower() for term in ['date', 'time', 'period', 'month', 'week']):
            data = data.sort_values(by=y_col, ascending=False)
        
        # Форматируем заголовки
        x_title = x_col.replace('_', ' ').title()
        y_title = y_col.replace('_', ' ').title()
        
        # Создаем фигуру
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            color_discrete_sequence=['#1976d2'],
            text=y_col if len(data) <= 10 else None  # Добавляем подписи значений только если точек не много
        )
        
        # Применяем шаблон с форматированием
        layout = template["layout"].copy()
        layout["title"] = title or f"{y_title} по {x_title.lower()}"
        layout["xaxis"]["title"] = x_title
        layout["yaxis"]["title"] = y_title
        
        fig.update_layout(layout)
        
        result = {
            "data": fig.data,
            "layout": fig.layout,
            "config": template["config"]
        }
        
    elif viz_type == "pie":
        template = VISUALIZATION_TEMPLATES["pie_chart"]
        
        # Определяем колонки для секторов и значений
        categorical_cols = [col for col in data.columns if data[col].dtype == 'object']
        numeric_cols = [col for col in data.columns if data[col].dtype.kind in 'if' and col not in categorical_cols]
        
        label_col = categorical_cols[0] if categorical_cols else data.columns[0]
        value_col = numeric_cols[0] if numeric_cols else (data.columns[1] if len(data.columns) > 1 else data.columns[0])
        
        # Создаем фигуру
        fig = px.pie(
            data,
            names=label_col,
            values=value_col,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        
        # Добавляем проценты и абсолютные значения в подписи
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            insidetextfont=dict(color='white')
        )
        
        # Применяем шаблон с форматированием
        layout = template["layout"].copy()
        layout["title"] = title or f"Распределение {label_col.replace('_', ' ').title()}"
        
        fig.update_layout(layout)
        
        result = {
            "data": fig.data,
            "layout": fig.layout,
            "config": template["config"]
        }
        
    else:  # Таблица как значение по умолчанию
        template = VISUALIZATION_TEMPLATES["table"]
        
        # Ограничиваем количество строк
        display_data = data.head(20)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(display_data.columns),
                fill_color='#1976d2',
                align='left',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[display_data[col] for col in display_data.columns],
                fill_color='lavender',
                align='left'
            )
        )])
        
        # Применяем шаблон с форматированием
        layout = template["layout"].copy()
        layout["title"] = title or "Данные в табличном виде"
        
        fig.update_layout(layout)
        
        result = {
            "data": fig.data,
            "layout": fig.layout,
            "config": template["config"]
        }
    
    # Преобразуем данные Plotly в JSON, чтобы избежать проблем с сериализацией
    result_json = json.loads(json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder))
    return result_json