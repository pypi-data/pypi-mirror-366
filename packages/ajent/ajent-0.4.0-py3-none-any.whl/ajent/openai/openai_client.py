import logging
import openai
from ajent import LLMClient
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from typing import Any, Dict, List, Generator
from ..response_serializer import ResponseSerializer


class OpenAIClient(LLMClient):
    def __init__(self, token: str):
        self._client = OpenAI(api_key=token)

    def send(self, messages: List[Dict], tools: List[Dict], model: str) -> Any:
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools
            )
            message = response.choices[0].message
            return self.serialize_response(message)
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            return {"error": "OpenAI API error", "details": str(e)}
        except openai.RateLimitError as e:
            logging.warning("Rate limit exceeded. Please slow down your requests.")
            return {"error": "Rate limit exceeded", "details": str(e)}
        except openai.InvalidRequestError as e:
            logging.error(f"Invalid request: {e}")
            return {"error": "Invalid request", "details": str(e)}
        except openai.AuthenticationError as e:
            logging.error(f"Authentication error: {e}")
            return {"error": "Authentication error", "details": str(e)}
        except openai.OpenAIError as e:
            logging.error(f"General OpenAI error: {e}")
            return {"error": "OpenAI error", "details": str(e)}
        except Exception as e:
            logging.exception("Unexpected error occurred")
            return {"error": "Unexpected error", "details": str(e)}
        
    def serialize_response(self, response: Any) -> Dict:
        return ResponseSerializer.serialize_message(response)

    def stream(self, messages: List[Dict], tools: List[Dict], model: str) -> Generator[Dict, None, None]:
        """
        Streaming version of the send function that yields chunks of the response.
        
        Args:
            messages: List of message dictionaries
            tools: List of tool dictionaries
            model: Model identifier string
        
        Yields:
            Dictionary containing either response chunks or error information
        """
        try:
            # Create streaming response
            stream = self._client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                stream=True  # Enable streaming
            )
            
            # Initialize variables to accumulate the response
            current_tool_calls = {}
            current_content = ""
            current_tool_call_id = None

            
            # Process each chunk
            for chunk in stream:
                if not isinstance(chunk, ChatCompletionChunk):
                    continue
                    
                delta = chunk.choices[0].delta
                
                # Handle tool calls
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if tool_call.id:
                            current_tool_call_id = tool_call.id
                            print(f"Tool call id: {current_tool_call_id}")
                        else:
                            print("Tool call id not found, keep using the previous one")
                        
                        if current_tool_call_id not in current_tool_calls:
                            print(f"Tool call not found, creating new one. Tool call id: {current_tool_call_id}")
                            print( f"Existing tool calls: {current_tool_calls}")
                            current_tool_calls[current_tool_call_id] = {
                                "id": current_tool_call_id,
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            }
                        
                        if tool_call.function.name:
                            print("Tool call function name found")
                            current_tool_calls[current_tool_call_id]["function"]["name"] = tool_call.function.name
                        if tool_call.function.arguments:
                            print("Tool call function arguments found")
                            current_tool_calls[current_tool_call_id]["function"]["arguments"] += tool_call.function.arguments
                            
                        yield {
                            "type": "tool_call",
                            "tool_call": current_tool_calls[current_tool_call_id]
                        }
                
                # Handle content
                if delta.content:
                    current_content += delta.content
                    yield {
                        "type": "content",
                        "content": delta.content
                    }
                    
                # Handle end of response
                if chunk.choices[0].finish_reason:
                    yield {
                        "type": "finish",
                        "finish_reason": chunk.choices[0].finish_reason,
                        "final_content": current_content,
                        "final_tool_calls": list(current_tool_calls.values()) if current_tool_calls else None
                    }
                    
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            yield {"error": "OpenAI API error", "details": str(e)}
        except openai.RateLimitError as e:
            logging.warning("Rate limit exceeded. Please slow down your requests.")
            yield {"error": "Rate limit exceeded", "details": str(e)}
        except openai.InvalidRequestError as e:
            logging.error(f"Invalid request: {e}")
            yield {"error": "Invalid request", "details": str(e)}
        except openai.AuthenticationError as e:
            logging.error(f"Authentication error: {e}")
            yield {"error": "Authentication error", "details": str(e)}
        except openai.OpenAIError as e:
            logging.error(f"General OpenAI error: {e}")
            yield {"error": "OpenAI error", "details": str(e)}
        except Exception as e:
            logging.exception("Unexpected error occurred")
            yield {"error": "Unexpected error", "details": str(e)}

    def stt(self, audio_file_path):
        """
        Transcribe audio file to text using OpenAI's Whisper model
        
        Args:
            audio_file_path (str): Path to the audio file
            api_token (str): OpenAI API token
            
        Returns:
            str: Transcribed text
        """
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    language="pt" 
                )
                
            text_content = transcription.text
            
            if not text_content:
                logging.warning("Failed to transcribe audio content")
                raise Exception("Failed to transcribe audio content")
                
            logging.info(f"Audio transcribed successfully")
            return text_content
                
        except Exception as e:
            logging.error(f"Whisper transcription error: {str(e)}")
            raise Exception(f"Speech-to-text transcription failed: {str(e)}")

    def text_to_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024", quality: str = "standard", n: int = 1) -> Dict:
        """
        Generate image from text prompt using OpenAI's DALL-E model
        
        Args:
            prompt (str): Text description of the image to generate
            model (str): Model to use (dall-e-2 or dall-e-3, default: dall-e-3)
            size (str): Image size (256x256, 512x512, 1024x1024 for dall-e-2; 1024x1024, 1792x1024, 1024x1792 for dall-e-3)
            quality (str): Image quality (standard or hd, only for dall-e-3)
            n (int): Number of images to generate (1-10 for dall-e-2, only 1 for dall-e-3)
            
        Returns:
            Dict: Response containing image URLs or error information
        """
        try:
            request_params = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "n": n
            }
            
            # Only add quality parameter for dall-e-3
            if model == "dall-e-3":
                request_params["quality"] = quality
                # dall-e-3 only supports n=1
                if n > 1:
                    logging.warning("DALL-E 3 only supports generating 1 image at a time. Setting n=1.")
                    request_params["n"] = 1
            
            response = self._client.images.generate(**request_params)
            
            # Extract URLs from response
            image_urls = [image.url for image in response.data]
            
            return {
                "success": True,
                "images": image_urls,
                "model": model,
                "size": size,
                "quality": quality if model == "dall-e-3" else None,
                "count": len(image_urls)
            }
            
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            return {"error": "OpenAI API error", "details": str(e)}
        except openai.RateLimitError as e:
            logging.warning("Rate limit exceeded. Please slow down your requests.")
            return {"error": "Rate limit exceeded", "details": str(e)}
        except openai.InvalidRequestError as e:
            logging.error(f"Invalid request: {e}")
            return {"error": "Invalid request", "details": str(e)}
        except openai.AuthenticationError as e:
            logging.error(f"Authentication error: {e}")
            return {"error": "Authentication error", "details": str(e)}
        except openai.OpenAIError as e:
            logging.error(f"General OpenAI error: {e}")
            return {"error": "OpenAI error", "details": str(e)}
        except Exception as e:
            logging.exception("Unexpected error occurred during image generation")
            return {"error": "Unexpected error", "details": str(e)}