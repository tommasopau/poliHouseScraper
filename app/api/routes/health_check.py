"""
Health check endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


router = APIRouter(tags=["health"])


@router.get("/healthcheck")
async def healthcheck():
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
