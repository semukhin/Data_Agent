import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .dependencies import get_db, get_analyzer_agent, get_sql_agent, get_viz_agent, initialize_metadata, get_data_analysis_service
from .routers import api
from .schemas.requests import QueryRequest
from .services.auth import configure_auth_router, get_current_active_user, User

# Инициализация приложения FastAPI
app = FastAPI(
    title="Atlantix Data Agent API",
    description="API для анализа пользовательской активности с использованием ИИ",
    version="1.0.0"
)

# Добавление сжатия ответов
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка заголовков кэширования
@app.middleware("http")
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    
    # Для GET-запросов к API метаданных добавляем кэширование на 5 минут
    if request.method == "GET" and "/api/metadata" in request.url.path:
        response.headers["Cache-Control"] = "public, max-age=300"
    
    return response

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
    return {"status": "healthy", "message": "Сервис аналитики пользовательской активности работает", "version": "1.0.0"}

# Получение текущего пользователя
@app.get("/api/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Инициализация метаданных при запуске приложения
@app.on_event("startup")
async def startup_event():
    initialize_metadata()
    print("✅ Метаданные представления успешно инициализированы")

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "9000")),
        reload=True
    )