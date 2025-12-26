from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from time import time
import traceback

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Content Generation API with Memory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full error in debug mode
    if settings.DEBUG:
        print(f"❌ Error: {exc}")
        traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Root endpoint
@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "debug": settings.DEBUG
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.APP_NAME} starting up...")
    
    # Create all database tables automatically
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise
    
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔧 Debug Mode: {settings.DEBUG}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print(f"👋 {settings.APP_NAME} shutting down...")

# Import and include routers AFTER app is created
# This prevents circular import issues
try:
    from app.api import auth
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["Authentication"]
    )
    print("✅ Auth router loaded")
except Exception as e:
    print(f"❌ Failed to load auth router: {e}")
    if settings.DEBUG:
        traceback.print_exc()

try:
    from app.api import conversations
    app.include_router(
        conversations.router,
        prefix="/api/conversations",
        tags=["Conversations"]
    )
    print("✅ Conversations router loaded")
except Exception as e:
    print(f"⚠️  Conversations router not available: {e}")
    if settings.DEBUG:
        traceback.print_exc()

try:
    from app.api import messages
    app.include_router(
        messages.router,
        prefix="/api/messages",
        tags=["Messages"]
    )
    print("✅ Messages router loaded")
except Exception as e:
    print(f"⚠️  Messages router not available: {e}")
    if settings.DEBUG:
        traceback.print_exc()

try:
    from app.api import content
    app.include_router(
        content.router,
        prefix="/api/content",
        tags=["Content Generation"]
    )
    print("✅ Content router loaded")
except Exception as e:
    print(f"⚠️  Content router not available: {e}")
    if settings.DEBUG:
        traceback.print_exc()

try:
    from app.api import memory
    app.include_router(
        memory.router,
        prefix="/api/memory",
        tags=["Memory & Context"]
    )
    print("✅ Memory router loaded")
except Exception as e:
    print(f"⚠️  Memory router not available: {e}")
    if settings.DEBUG:
        traceback.print_exc()

try:
    from app.api import analytics
    app.include_router(
        analytics.router,
        prefix="/api/analytics",
        tags=["Analytics"]
    )
    print("✅ Analytics router loaded")
except Exception as e:
    print(f"⚠️  Analytics router not available: {e}")
    if settings.DEBUG:
        traceback.print_exc()