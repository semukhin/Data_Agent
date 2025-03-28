import plotly.express as px
import plotly.graph_objects as go
import json

class VisualizationTool(BaseTool):
    def __init__(self):
        self.name = "visualization_tool"
        self.description = "Tool for creating data visualizations"
        
    def _run(self, params):
        data = params["data"]
        viz_type = params["type"]
        config = params.get("config", {})
        
        try:
            if viz_type == "bar":
                fig = px.bar(data, **config)
            elif viz_type == "line":
                fig = px.line(data, **config)
            elif viz_type == "scatter":
                fig = px.scatter(data, **config)
            elif viz_type == "pie":
                fig = px.pie(data, **config)
            elif viz_type == "table":
                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(data.columns)),
                    cells=dict(values=[data[col] for col in data.columns])
                )])
            else:
                # Обработка других типов визуализации
                raise ValueError(f"Visualization type {viz_type} not supported")
                
            return {
                "success": True,
                "figure": fig.to_json(),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "figure": None,
                "error": str(e)
            }