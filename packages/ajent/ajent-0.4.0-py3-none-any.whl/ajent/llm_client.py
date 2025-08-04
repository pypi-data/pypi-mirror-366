from abc import ABC, abstractmethod
from typing import Any, Dict, List

class LLMClient(ABC):    
    @abstractmethod
    def send(self, messages: List[Dict], tools: List[Dict], model: str) -> Any:
        pass

    @abstractmethod
    def stream(self, messages: List[Dict], tools: List[Dict], model: str) -> Any:
        pass

    @abstractmethod
    def serialize_response(self, response: Any) -> Dict:
        pass

    @abstractmethod
    def stt(self, audio_file_path) -> Any:
        pass

    @abstractmethod
    def text_to_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024", quality: str = "standard", n: int = 1) -> Any:
        pass