# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
# from .models import UserRequest
# from .config import AppConfig
# from .services.prompt_service import PromptService
# from .services.ollama_service import OllamaService

# class FinancialAssistantAPI:
#     """
#     Main API class for the Financial Assistant application.
#     """
#     def __init__(self):
#         self.app = FastAPI(
#             title="FinBuddy Financial Assistant",
#             description="AI-powered financial assistance API"
#         )
#         AppConfig.configure_cors(self.app)
#         self._setup_routes()

#     def _setup_routes(self):
#         """
#         Set up API routes.
#         """
#         @self.app.post("/generate-response/")
#         async def generate_response(request: UserRequest):
#             try:
#                 # Generate system prompt with user query and optional user data
#                 system_prompt = PromptService.generate_system_prompt(
#                     user_query=request.user_query,
#                     user_data=request.user_data
#                 )

#                 # Directly pass the async generator to StreamingResponse (NO 'await')
#                 return StreamingResponse(OllamaService.stream_response(system_prompt), media_type="text/plain")

#             except Exception as e:
#                 raise HTTPException(status_code=500, detail=str(e))


#     def get_app(self):
#         """
#         Return the FastAPI application instance.
#         """
#         return self.app

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from starlette_exporter import PrometheusMiddleware, handle_metrics
from .models import UserRequest
from .config import AppConfig
from .services.prompt_service import PromptService
from .services.ollama_service import OllamaService
from .services.metrics import APIMetrics  # Import metrics class
import json
import time

class FinancialAssistantAPI:
    """
    Main API class for the Financial Assistant application.
    """
    def __init__(self):
        self.app = FastAPI(
            title="FinBuddy Financial Assistant",
            description="AI-powered financial assistance API"
        )
        AppConfig.configure_cors(self.app)
        self.app.add_middleware(PrometheusMiddleware)
        self.app.add_route("/metrics", handle_metrics)  # Expose metrics
        self._setup_routes()

    def _setup_routes(self):
        """
        Set up API routes.
        """
        @self.app.post("/generate-response/")
        async def generate_response(request: UserRequest, req: Request):
            method = req.method
            endpoint = req.url.path
            start_time = time.time()  # Start time tracking
            
            try:
                # Increment request counter
                APIMetrics.REQUEST_COUNTER.labels(method=method, endpoint=endpoint, status="200").inc()

                # Generate system prompt with user query and optional user data
                system_prompt = PromptService.generate_system_prompt(
                    user_query=request.user_query,
                    user_data=request.user_data
                )

                # Create an async generator that converts dict to JSON string
                async def stream_json_response():
                    async for chunk in OllamaService.stream_response(system_prompt):
                        yield json.dumps(chunk) + "\n"
                
                response = StreamingResponse(
                    stream_json_response(), 
                    media_type="application/json"
                )
                # Measure response time
                APIMetrics.RESPONSE_TIME.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)

                # Return StreamingResponse with JSON-encoded chunks
                return response

            except Exception as e:
                APIMetrics.ERROR_COUNTER.labels(method=method, endpoint=endpoint, error_type=type(e).__name__).inc()
                raise HTTPException(status_code=500, detail=str(e))

    def get_app(self):
        """
        Return the FastAPI application instance.
        """
        return self.app