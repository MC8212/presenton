"""
Template Providers API - Endpoint for getting available LLM providers for template creation.
"""

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from services.vision_llm_service import (
    get_available_vision_providers,
    get_default_vision_provider,
)


TEMPLATE_PROVIDERS_ROUTER = APIRouter(
    prefix="/template-providers",
    tags=["template-providers"]
)


class ProviderInfo(BaseModel):
    id: str
    name: str
    model: str
    available: bool


class AvailableProvidersResponse(BaseModel):
    providers: List[ProviderInfo]
    default: str
    has_available: bool


@TEMPLATE_PROVIDERS_ROUTER.get(
    "/available",
    response_model=AvailableProvidersResponse,
    summary="Get available LLM providers for template creation",
    description="Returns list of providers with configured API keys that support vision/multimodal tasks"
)
async def get_available_template_providers():
    """
    Get list of available LLM providers for template creation.

    Returns providers that have valid API keys configured and support
    vision/multimodal tasks (required for slide-to-HTML conversion).
    """
    providers = get_available_vision_providers()
    default_provider = get_default_vision_provider()

    return AvailableProvidersResponse(
        providers=[ProviderInfo(**p) for p in providers],
        default=default_provider,
        has_available=len(providers) > 0
    )
