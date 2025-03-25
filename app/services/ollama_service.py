# import ollama
# import asyncio
# from app.services.metrics import track_method_performance

# class OllamaService:
#     """
#     Service for handling interactions with the Ollama AI model.
#     """
#     @staticmethod
#     @track_method_performance("ollama_service_stream_response")
#     async def stream_response(prompt: str, model: str = "mistral"):
#         """
#         Stream a response from the Ollama model.
        
#         Args:
#             prompt (str): The complete system and user prompt
#             model (str, optional): The AI model to use. Defaults to "mistral".
        
#         Yields:
#             dict: Tokens from the model's response with additional metadata
#         """
#         try:
#             response_stream = ollama.chat(
#                 model=model, 
#                 messages=[{"role": "user", "content": prompt}], 
#                 stream=True
#             )

#             for chunk in response_stream:
#                 token = chunk.get("message", {}).get("content", "")
#                 if token:
#                     yield {
#                         "token": token,
#                         "finished": False
#                     }
#                     print(token, end="", flush=True)
#                 await asyncio.sleep(0)  # Allow FastAPI to process other requests

#             # Signal end of stream
#             yield {
#                 "token": "",
#                 "finished": True
#             }

#         except Exception as e:
#             yield {
#                 "token": f"Error: {str(e)}",
#                 "finished": True
#             }

import ollama
import asyncio
from app.services.metrics import track_method_performance
import re

class OllamaService:
    """
    Service for handling interactions with the Ollama AI model.
    """
    @staticmethod
    @track_method_performance("ollama_service_stream_response")
    async def stream_response(prompt: str, model: str = "mistral"):
        """
        Stream a response from the Ollama model, ensuring numbers and words are streamed correctly.
        
        Args:
            prompt (str): The complete system and user prompt.
            model (str, optional): The AI model to use. Defaults to "mistral".
        
        Yields:
            dict: Tokens from the model's response with additional metadata.
        """
        try:
            response_stream = ollama.chat(
                model=model, 
                messages=[{"role": "user", "content": prompt}], 
                stream=True
            )
            buffer = ""  # Buffer to store partial tokens
            is_number_buffer = False  # Flag to track if buffer is a number
            punctuation_chars = {".", ",", "!", "?", ":", ";", "%"}
            
            for chunk in response_stream:
                token = chunk.get("message", {}).get("content", "")
                for char in token:
                    # Check if character continues a number or is part of a number format
                    if re.match(r'[\d₹$,.]', char) or (is_number_buffer and char == '%'):
                        buffer += char
                        is_number_buffer = True
                        continue
                    
                    # Handle space characters
                    if char.isspace():
                        if buffer:
                            yield {"token": buffer, "finished": False}
                            print(buffer, end=" ", flush=True)
                            buffer = ""
                            is_number_buffer = False
                        print(char, end="", flush=True)
                        continue
                    
                    # Handle punctuation
                    if char in punctuation_chars:
                        # If buffer is not empty, attach punctuation to it
                        if buffer:
                            buffer += char
                            yield {"token": buffer, "finished": False}
                            print(buffer, end="", flush=True)
                            buffer = ""
                            is_number_buffer = False
                        else:
                            # Standalone punctuation (rare, but possible)
                            yield {"token": char, "finished": False}
                            print(char, end="", flush=True)
                        continue
                    
                    # Reset number buffer if non-number character
                    if is_number_buffer:
                        yield {"token": buffer, "finished": False}
                        print(buffer, end=" ", flush=True)
                        buffer = ""
                        is_number_buffer = False
                    
                    # Start new buffer with current character
                    buffer += char
                    is_number_buffer = False
                
                await asyncio.sleep(0)  # Allow FastAPI to process other requests
            
            # Send any remaining buffer content
            if buffer:
                yield {"token": buffer, "finished": False}
                print(buffer, end="", flush=True)
            
            # Signal end of stream
            yield {"token": "", "finished": True}
        
        except Exception as e:
            yield {"token": f"Error: {str(e)}", "finished": True}