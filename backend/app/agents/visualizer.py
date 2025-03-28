class VisualizerAgent:
    def __init__(self, model=ModelType.GPT_4):
        self.assistant_role_name = "Data Visualization Expert"
        self.user_role_name = "Data Analyst"
        
        self.agent = RolePlaying(
            assistant_role_name=self.assistant_role_name,
            user_role_name=self.user_role_name,
            assistant_agent_kwargs={"model": model},
            user_agent_kwargs={"model": model}
        )
        
    def generate_visualization_code(self, data, visualization_type, user_query):
        system_message = """
        You are a Data Visualization Expert specializing in Plotly.
        Your task is to generate code for creating visualizations based on the data.
        """
        
        user_message = f"""
        User query: {user_query}
        Visualization type: {visualization_type}
        Data structure: {data.head().to_dict()}
        Full data shape: {data.shape}
        
        Generate Plotly code to visualize this data.
        """
        
        response = self.agent.step(
            user_message=user_message,
            system_message=system_message
        )
        
        return {
            "plotly_code": response.code,
            "visualization_config": response.config
        }