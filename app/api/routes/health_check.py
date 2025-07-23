"""
Health check endpoint.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.middleware.rate_limiter import limiter


router = APIRouter(tags=["health"])


@router.get("/healthcheck")
@limiter.limit("10/minute")
async def healthcheck(request: Request):
    """
    Basic health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "house-scraper-api",
        "version": "1.0.0"
    }
