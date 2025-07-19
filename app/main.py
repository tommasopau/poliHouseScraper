import uvicorn
from app.app_factory import create_app
from app.core.config import config
if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
