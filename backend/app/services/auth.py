from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Схема данных пользователя
class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

# Схема данных пользователя для БД
class UserInDB(User):
    hashed_password: str

# Константы для JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "atlantix_default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

# Схема токена
class Token(BaseModel):
    access_token: str
    token_type: str

# Схема данных токена
class TokenData(BaseModel):
    username: Optional[str] = None

# Создание OAuth2 схемы для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Простая база пользователей
# В реальном приложении должна быть замена на БД
users_db = {
    "atlantix": {
        "username": "atlantix",
        "hashed_password": "atlantix",  # В реальном приложении пароли должны быть хешированы
        "disabled": False,
    }
}

def get_user(db, username: str):
    """
    Получает пользователя из базы данных
    
    Args:
        db: База данных пользователей
        username: Имя пользователя
        
    Returns:
        UserInDB: Данные пользователя или None
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(db, username: str, password: str):
    """
    Аутентифицирует пользователя
    
    Args:
        db: База данных пользователей
        username: Имя пользователя
        password: Пароль пользователя
        
    Returns:
        UserInDB: Данные пользователя или False
    """
    user = get_user(db, username)
    if not user:
        return False
    # В реальном приложении здесь должна быть проверка хеша пароля
    if password != user.hashed_password:
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создает JWT токен
    
    Args:
        data: Данные для кодирования в токене
        expires_delta: Время действия токена
        
    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Получает текущего пользователя по токену
    
    Args:
        token: JWT токен
        
    Returns:
        User: Данные пользователя
        
    Raises:
        HTTPException: При неверных учетных данных
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Проверяет, что пользователь активен
    
    Args:
        current_user: Данные текущего пользователя
        
    Returns:
        User: Данные пользователя
        
    Raises:
        HTTPException: Если пользователь неактивен
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Пользователь неактивен")
    return current_user

def configure_auth_router(app):
    """
    Настраивает маршруты авторизации
    
    Args:
        app: Экземпляр FastAPI приложения
    """
    @app.post("/api/token", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(users_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}