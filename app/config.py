from fastapi.middleware.cors import CORSMiddleware

class AppConfig:
    """
    Centralized configuration for the application.
    """
    @staticmethod
    def configure_cors(app):
        """
        Configure CORS middleware for the FastAPI application.
        """
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5500"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )