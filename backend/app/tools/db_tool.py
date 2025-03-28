from camel.tools import BaseTool
import pandas as pd

class DatabaseTool(BaseTool):
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.name = "database_tool"
        self.description = "Tool for executing SQL queries on PostgreSQL database"
        
    def _run(self, sql_query):
        try:
            # Выполнение запроса
            result = pd.read_sql(sql_query, self.db_connection)
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }