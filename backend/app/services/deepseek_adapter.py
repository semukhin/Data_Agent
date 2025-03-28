import os
from typing import Dict, Any, List, Optional
import requests
import json

class DeepseekAdapter:
    """Адаптер для взаимодействия с DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
        
        if not self.api_key or not self.api_base:
            raise ValueError("DEEPSEEK_API_KEY и DEEPSEEK_API_BASE должны быть установлены в .env")
    
    def generate_response(self, 
                          prompt: str, 
                          system_message: Optional[str] = None,
                          temperature: float = 0.7,
                          max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Отправляет запрос к DeepSeek API и возвращает ответ
        
        Args:
            prompt: Текст запроса
            system_message: Системное сообщение для модели
            temperature: Температура (степень случайности) ответа
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            Dictionary с ответом API
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к DeepSeek API: {str(e)}")
    
    def extract_json_from_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает JSON из ответа модели
        
        Args:
            response: Ответ от DeepSeek API
            
        Returns:
            Словарь с извлеченными данными
        """
        if "choices" not in response or len(response["choices"]) == 0:
            raise ValueError("Некорректный ответ от DeepSeek API")
        
        content = response["choices"][0]["message"]["content"]
        
        # Попытка извлечь JSON из текста
        try:
            # Ищем JSON в тексте между ```json и ```
            json_pattern_start = content.find("```json")
            if json_pattern_start != -1:
                json_pattern_start += 7  # Длина "```json"
                json_pattern_end = content.find("```", json_pattern_start)
                if json_pattern_end != -1:
                    json_str = content[json_pattern_start:json_pattern_end].strip()
                    return json.loads(json_str)
            
            # Поиск {...} в тексте
            json_pattern_start = content.find("{")
            if json_pattern_start != -1:
                # Рекурсивный подсчет скобок для корректного извлечения
                open_braces = 0
                for i in range(json_pattern_start, len(content)):
                    if content[i] == "{":
                        open_braces += 1
                    elif content[i] == "}":
                        open_braces -= 1
                        if open_braces == 0:
                            json_str = content[json_pattern_start:i+1]
                            return json.loads(json_str)
            
            # Если не нашли JSON, возвращаем весь текст
            return {"content": content}
            
        except json.JSONDecodeError:
            return {"content": content}