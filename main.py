import uvicorn
from app.api import FinancialAssistantAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

def create_app():
    """
    Create and return the FastAPI application.
    """
    financial_assistant = FinancialAssistantAPI()
    app = financial_assistant.get_app()

    # Add Prometheus Middleware
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", handle_metrics)

    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=5050)
