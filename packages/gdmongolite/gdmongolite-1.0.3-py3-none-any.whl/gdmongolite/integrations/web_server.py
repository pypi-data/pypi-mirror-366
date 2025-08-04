"""Web server integration with Uvicorn for gdmongolite"""

import asyncio
import uvicorn
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from ..core import DB, Schema
from .fastapi import create_fastapi_app


class WebServer:
    """Easy web server setup for gdmongolite applications"""
    
    def __init__(
        self,
        db: DB,
        schemas: List[Type[Schema]] = None,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False,
        **app_kwargs
    ):
        self.db = db
        self.schemas = schemas or list(db._schemas.values())
        self.host = host
        self.port = port
        self.reload = reload
        self.app_kwargs = app_kwargs
        
        # Create FastAPI app
        self.app = create_fastapi_app(db, self.schemas, **app_kwargs)
    
    def run(self, **uvicorn_kwargs):
        """Run the web server"""
        config = {
            "app": self.app,
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            **uvicorn_kwargs
        }
        
        print(f"🚀 Starting gdmongolite web server...")
        print(f"📡 Server: http://{self.host}:{self.port}")
        print(f"📚 API Docs: http://{self.host}:{self.port}/docs")
        print(f"🔍 Health Check: http://{self.host}:{self.port}/health")
        
        uvicorn.run(**config)
    
    async def run_async(self, **uvicorn_kwargs):
        """Run the web server asynchronously"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            reload=self.reload,
            **uvicorn_kwargs
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def add_custom_routes(self, router_func):
        """Add custom routes to the app"""
        router_func(self.app, self.db)
        return self
    
    def add_middleware(self, middleware_class, **kwargs):
        """Add middleware to the app"""
        self.app.add_middleware(middleware_class, **kwargs)
        return self
    
    def add_static_files(self, directory: str, path: str = "/static"):
        """Add static file serving"""
        from fastapi.staticfiles import StaticFiles
        
        if Path(directory).exists():
            self.app.mount(path, StaticFiles(directory=directory), name="static")
        
        return self
    
    def add_templates(self, directory: str):
        """Add template rendering support"""
        from fastapi.templating import Jinja2Templates
        
        if Path(directory).exists():
            templates = Jinja2Templates(directory=directory)
            
            # Add template rendering endpoint
            @self.app.get("/")
            async def render_index(request):
                return templates.TemplateResponse("index.html", {"request": request})
        
        return self


def create_web_server(
    db: DB,
    schemas: List[Type[Schema]] = None,
    **kwargs
) -> WebServer:
    """Create a web server instance"""
    return WebServer(db, schemas, **kwargs)


def quick_serve(
    db: DB,
    schemas: List[Type[Schema]] = None,
    host: str = "127.0.0.1",
    port: int = 8000,
    **kwargs
):
    """Quickly serve your gdmongolite app"""
    server = WebServer(db, schemas, host, port, **kwargs)
    server.run()


# Development server with hot reload
def dev_serve(
    db: DB,
    schemas: List[Type[Schema]] = None,
    host: str = "127.0.0.1",
    port: int = 8000,
    **kwargs
):
    """Development server with auto-reload"""
    server = WebServer(db, schemas, host, port, reload=True, **kwargs)
    server.run()


# Production server configuration
def prod_serve(
    db: DB,
    schemas: List[Type[Schema]] = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 4,
    **kwargs
):
    """Production server configuration"""
    config = {
        "app": create_fastapi_app(db, schemas, **kwargs),
        "host": host,
        "port": port,
        "workers": workers,
        "access_log": True,
        "reload": False,
        **kwargs
    }
    
    print(f"🚀 Starting gdmongolite production server...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"👥 Workers: {workers}")
    
    uvicorn.run(**config)