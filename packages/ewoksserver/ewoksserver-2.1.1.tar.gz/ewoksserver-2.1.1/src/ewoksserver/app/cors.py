from typing import Optional, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def enable_cors(app: FastAPI) -> None:
    """Enable Cross-Origin Resource Sharing"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_cors_options(app: FastAPI) -> Optional[Dict]:
    for mw in app.user_middleware:
        if mw.cls is CORSMiddleware:
            return mw.options
