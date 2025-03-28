import pandas as pd
from typing import Dict, Any
import datetime
import json

class DatabaseTool:
    """Инструмент для выполнения запросов к базе данных"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Выполняет SQL-запрос и возвращает результаты
        
        Args:
            sql_query: SQL-запрос для выполнения
            
        Returns:
            Dictionary с результатами и статусом запроса
        """
        try:
            # Выполнение запроса
            result = pd.read_sql(sql_query, self.db_connection)
            
            # Преобразование типов данных для JSON-сериализации
            for col in result.columns:
                if result[col].dtype == 'datetime64[ns]':
                    result[col] = result[col].astype(str)
                elif result[col].dtype == 'timedelta64[ns]':
                    result[col] = result[col].astype(str)
            
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
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Получает метаданные базы данных
        
        Returns:
            Dictionary с метаданными таблиц
        """
        try:
            # Запрос для получения списка таблиц и представлений
            tables_query = """
            SELECT 
                table_name 
            FROM 
                information_schema.tables 
            WHERE 
                table_schema = 'public'
            """
            tables = pd.read_sql(tables_query, self.db_connection)
            
            metadata = {}
            
            for table_name in tables['table_name'].tolist():
                # Запрос для получения информации о столбцах
                columns_query = f"""
                SELECT 
                    column_name, 
                    data_type,
                    is_nullable
                FROM 
                    information_schema.columns 
                WHERE 
                    table_schema = 'public' 
                    AND table_name = '{table_name}'
                """
                columns = pd.read_sql(columns_query, self.db_connection)
                
                # Запрос для получения первичных ключей
                pk_query = f"""
                SELECT
                    c.column_name
                FROM
                    information_schema.table_constraints tc
                JOIN
                    information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
                JOIN
                    information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                    AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
                WHERE
                    constraint_type = 'PRIMARY KEY' AND tc.table_name = '{table_name}'
                """
                primary_keys = pd.read_sql(pk_query, self.db_connection)
                
                # Запрос для получения внешних ключей
                fk_query = f"""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS references_table,
                    ccu.column_name AS references_column
                FROM
                    information_schema.table_constraints AS tc
                JOIN
                    information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
                JOIN
                    information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
                WHERE
                    constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}'
                """
                foreign_keys = pd.read_sql(fk_query, self.db_connection)
                
                # Формирование метаданных таблицы
                table_metadata = {
                    "columns": [
                        {
                            "name": row["column_name"],
                            "type": row["data_type"],
                            "nullable": row["is_nullable"] == "YES"
                        } for _, row in columns.iterrows()
                    ],

                    "primary_keys": primary_keys["column_name"].tolist() if not primary_keys.empty else [],
                    "foreign_keys": [
                        {
                            "column": row["column_name"],
                            "references_table": row["references_table"],
                            "references_column": row["references_column"]
                        } for _, row in foreign_keys.iterrows()
                    ]
                }
                
                # Получение примера данных
                try:
                    sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                    sample_data = pd.read_sql(sample_query, self.db_connection)
                    table_metadata["sample_data"] = sample_data.to_dict(orient="records")
                except:
                    table_metadata["sample_data"] = []
                
                metadata[table_name] = table_metadata
            
            return metadata
            
        except Exception as e:
            return {"error": str(e)}