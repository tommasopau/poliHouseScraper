import uvicorn
from app.app_factory import create_app
from app.core.config import settings
app = create_app()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
