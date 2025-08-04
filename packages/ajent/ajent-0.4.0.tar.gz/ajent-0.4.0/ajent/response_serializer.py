from typing import Any, Dict

class ResponseSerializer:
    @staticmethod
    def serialize_message(message: Any) -> Dict[str, Any]:
        try:
            if isinstance(message, dict):
                return ResponseSerializer._serialize_dict_message(message)
            return ResponseSerializer._serialize_object_message(message)
        except Exception as e:
            raise ValueError(f"Unable to serialize message: {str(e)}")

    @staticmethod
    def _serialize_dict_message(message: Dict) -> Dict[str, Any]:
        content = message.get("content")
        result = {
            "role": str(message.get("role", "assistant")),
            "content": "" if content is None else str(content)
        }
        
        if "tool_calls" in message:
            result["tool_calls"] = [
                ResponseSerializer._serialize_tool_call(tool_call)
                for tool_call in message["tool_calls"]
            ]
        
        if "tool_call_id" in message:
            result["tool_call_id"] = str(message["tool_call_id"])
            
        return result

    @staticmethod
    def _serialize_object_message(message: Any) -> Dict[str, Any]:
        content = getattr(message, "content", "")
        result = {
            "role": str(getattr(message, "role", "assistant")),
            "content": "" if content is None else str(content)
        }
        
        if hasattr(message, "tool_calls") and message.tool_calls:
            result["tool_calls"] = [
                ResponseSerializer._serialize_tool_call(tool_call)
                for tool_call in message.tool_calls
            ]
            
        if hasattr(message, "tool_call_id"):
            result["tool_call_id"] = str(message.tool_call_id)
            
        return result
    
    @staticmethod
    def _serialize_tool_call(tool_call: Any) -> Dict[str, Any]:
        try:
            if isinstance(tool_call, dict):
                return {
                    "id": str(tool_call.get("id", "")),
                    "type": str(tool_call.get("type", "function")),
                    "function": {
                        "name": str(tool_call.get("function", {}).get("name", "")),
                        "arguments": tool_call.get("function", {}).get("arguments", "{}")
                    }
                }
            return {
                "id": str(tool_call.id),
                "type": str(tool_call.type),
                "function": {
                    "name": str(tool_call.function.name),
                    "arguments": tool_call.function.arguments
                }
            }
        except AttributeError as e:
            raise ValueError(f"Invalid tool call format: {str(e)}")