from abc import ABC, abstractmethod
from typing import Any, Dict, List
from ajent import LLMClient
from .openai import OpenAIClient

class LLMFactory:
    @staticmethod
    def create_client(llm_name: str, llm_token: str = None) -> LLMClient:
        switcher = {
            "openai": OpenAIClient(llm_token)
        }
        return switcher.get(llm_name.lower())