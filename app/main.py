import uvicorn
from app.app_factory import create_app
from app.core.config import settings

app = create_app()
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=settings.PORT)
