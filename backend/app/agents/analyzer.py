from camel.agents import RolePlaying
from camel.messages import BaseMessage
from camel.typing import ModelType

class AnalyzerAgent:
    def __init__(self, db_metadata, model=ModelType.GPT_4):
        self.db_metadata = db_metadata
        self.assistant_role_name = "Data Analyst"
        self.user_role_name = "User"
        
        # Инициализация агента с ролью
        self.agent = RolePlaying(
            assistant_role_name=self.assistant_role_name,
            user_role_name=self.user_role_name,
            assistant_agent_kwargs={"model": model},
            user_agent_kwargs={"model": model}
        )
        
    def process_query(self, user_query):
        # Подготовка системного промпта с метаданными БД
        db_info = self._prepare_db_metadata()
        system_message = f"""
        You are a Data Analyst with access to the following database views:
        {db_info}
        
        Your task is to understand the user's query about data visualization 
        and determine what data needs to be fetched and how it should be visualized.
        """
        
        # Получение ответа от агента
        response = self.agent.step(
            user_message=user_query,
            system_message=system_message
        )
        
        return {
            "required_data": response.analysis.required_data,
            "visualization_type": response.analysis.visualization_type,
            "sql_hints": response.analysis.sql_hints
        }