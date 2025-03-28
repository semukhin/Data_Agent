class SQLExpertAgent:
    def __init__(self, db_metadata, model=ModelType.GPT_4):
        self.db_metadata = db_metadata
        self.assistant_role_name = "SQL Expert"
        self.user_role_name = "Data Analyst"
        
        self.agent = RolePlaying(
            assistant_role_name=self.assistant_role_name,
            user_role_name=self.user_role_name,
            assistant_agent_kwargs={"model": model},
            user_agent_kwargs={"model": model}
        )
        
    def generate_sql(self, analysis_result):
        db_info = self._prepare_db_metadata()
        system_message = f"""
        You are a SQL Expert with deep knowledge of PostgreSQL.
        Your task is to generate SQL queries to fetch the data based on the analysis.
        
        Database schema:
        {db_info}
        """
        
        user_message = f"""
        I need a SQL query to visualize: {analysis_result['required_data']}
        Visualization type: {analysis_result['visualization_type']}
        SQL hints: {analysis_result['sql_hints']}
        """
        
        response = self.agent.step(
            user_message=user_message,
            system_message=system_message
        )
        
        return {
            "sql_query": response.sql_query,
            "query_explanation": response.explanation
        }