from contextlib import asynccontextmanager
from datetime import timedelta

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware

from app.auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.config import settings
from app.database import create_db_and_tables, get_session
from app.middleware import TimingMiddleware, LoggingMiddleware, RateLimitingMiddleware
from app.routes.posts import post_router
from app.routes.users import user_router
from app.schemas import Token


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the FastAPI application...")
    create_db_and_tables()
    yield
    print("Shutting down the FastAPI application...")


app = FastAPI(lifespan=lifespan, title="Blog App", version="0.1.0")
app.include_router(user_router)
app.include_router(post_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add our custom middleware
app.add_middleware(TimingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitingMiddleware, max_requests=100, window_seconds=60)


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# start FastAPI application server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=settings.RELOAD)
