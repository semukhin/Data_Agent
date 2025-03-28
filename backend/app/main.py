import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import get_db, get_analyzer_agent, get_sql_agent, get_viz_agent, initialize_metadata
from .routers import api
from .schemas.requests import QueryRequest
from .services.auth import configure_auth_router, get_current_active_user, User

# Инициализация приложения FastAPI
app = FastAPI(
    title="Data Agent API",
    description="API для анализа данных с использованием ИИ",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка авторизации
configure_auth_router(app)

# Добавление маршрутов API с защитой авторизацией
app.include_router(
    api.router,
    prefix=os.getenv("API_PREFIX", "/api"),
    tags=["api"],
    dependencies=[Depends(get_current_active_user)]
)

# Публичный эндпоинт для проверки здоровья приложения
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Получение текущего пользователя
@app.get("/api/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Инициализация метаданных при запуске приложения
@app.on_event("startup")
async def startup_event():
    initialize_metadata()

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "8000")),
        reload=True
    )