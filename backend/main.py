"""
LamiGo Backend Entry Point (Legacy)

This file is kept for backward compatibility.
The main application is now at: backend/app/main.py

To run the server:
    uvicorn app.main:app --reload

Or use this file:
    uvicorn main:app --reload
"""

from app.main import app

__all__ = ["app"]
