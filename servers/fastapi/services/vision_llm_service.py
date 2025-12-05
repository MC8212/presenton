"""
Vision LLM Service - Multi-provider support for multimodal/vision LLM calls.

This service abstracts vision/image-based LLM calls across all supported providers:
- OpenAI (GPT-4 Vision, etc.)
- Anthropic (Claude with vision)
- Google (Gemini with vision)
- Custom (OpenRouter or any OpenAI-compatible API with vision support)
"""

import asyncio
import base64
from typing import List, Dict, Optional
from fastapi import HTTPException
from openai import AsyncOpenAI
from google import genai
from google.genai.types import Content as GoogleContent, Part as GooglePart
from google.genai.types import GenerateContentConfig
from anthropic import AsyncAnthropic

from enums.llm_provider import LLMProvider
from constants.llm import (
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_GOOGLE_MODEL,
    DEFAULT_OPENAI_MODEL,
)
from utils.get_env import (
    get_anthropic_api_key_env,
    get_anthropic_model_env,
    get_custom_llm_api_key_env,
    get_custom_llm_url_env,
    get_custom_model_env,
    get_disable_thinking_env,
    get_google_api_key_env,
    get_google_model_env,
    get_llm_provider_env,
    get_openai_api_key_env,
    get_openai_model_env,
)
from utils.parsers import parse_bool_or_none


class VisionLLMService:
    """
    Service for handling vision/multimodal LLM calls across multiple providers.

    Unlike the standard LLMClient, this service is specifically designed for
    image-based content generation used in template creation (slide-to-HTML,
    HTML-to-React conversions).
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize the Vision LLM Service.

        Args:
            provider: Optional provider name ("openai", "google", "anthropic", "custom").
                     If not specified, uses the global LLM setting from environment.
        """
        if provider:
            try:
                self.provider = LLMProvider(provider)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid provider '{provider}'. Must be one of: openai, google, anthropic, custom"
                )
        else:
            # Fall back to global LLM provider setting
            try:
                self.provider = LLMProvider(get_llm_provider_env() or "openai")
            except ValueError:
                self.provider = LLMProvider.OPENAI

        self._client = self._get_client()

    def _get_client(self):
        """Get the appropriate client for the selected provider."""
        match self.provider:
            case LLMProvider.OPENAI:
                return self._get_openai_client()
            case LLMProvider.GOOGLE:
                return self._get_google_client()
            case LLMProvider.ANTHROPIC:
                return self._get_anthropic_client()
            case LLMProvider.CUSTOM:
                return self._get_custom_client()
            case LLMProvider.OLLAMA:
                raise HTTPException(
                    status_code=400,
                    detail="Ollama provider is not supported for vision/template creation tasks"
                )
            case _:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid provider for vision tasks"
                )

    def _get_openai_client(self) -> AsyncOpenAI:
        api_key = get_openai_api_key_env()
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API Key is not configured"
            )
        return AsyncOpenAI(api_key=api_key)

    def _get_google_client(self) -> genai.Client:
        api_key = get_google_api_key_env()
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Google API Key is not configured"
            )
        return genai.Client(api_key=api_key)

    def _get_anthropic_client(self) -> AsyncAnthropic:
        api_key = get_anthropic_api_key_env()
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Anthropic API Key is not configured"
            )
        return AsyncAnthropic(api_key=api_key)

    def _get_custom_client(self) -> AsyncOpenAI:
        url = get_custom_llm_url_env()
        if not url:
            raise HTTPException(
                status_code=400,
                detail="Custom LLM URL is not configured"
            )
        return AsyncOpenAI(
            base_url=url,
            api_key=get_custom_llm_api_key_env() or "null"
        )

    def _get_model(self) -> str:
        """Get the model name for the current provider."""
        match self.provider:
            case LLMProvider.OPENAI:
                return get_openai_model_env() or DEFAULT_OPENAI_MODEL
            case LLMProvider.GOOGLE:
                return get_google_model_env() or DEFAULT_GOOGLE_MODEL
            case LLMProvider.ANTHROPIC:
                return get_anthropic_model_env() or DEFAULT_ANTHROPIC_MODEL
            case LLMProvider.CUSTOM:
                model = get_custom_model_env()
                if not model:
                    raise HTTPException(
                        status_code=400,
                        detail="Custom model is not configured"
                    )
                return model
            case _:
                return DEFAULT_OPENAI_MODEL

    def _disable_thinking(self) -> bool:
        """Check if thinking should be disabled (for custom providers)."""
        return parse_bool_or_none(get_disable_thinking_env()) or False

    async def generate_with_vision(
        self,
        system_prompt: str,
        user_text: str,
        images: List[Dict[str, str]],
        max_tokens: int = 8000,
    ) -> str:
        """
        Generate content using vision/multimodal capabilities.

        Args:
            system_prompt: The system prompt to guide the model
            user_text: User text content (e.g., OXML, HTML to convert)
            images: List of image dicts with 'base64' and 'media_type' keys
            max_tokens: Maximum tokens for response

        Returns:
            Generated text content

        Raises:
            HTTPException: If generation fails or no content is returned
        """
        model = self._get_model()

        match self.provider:
            case LLMProvider.OPENAI:
                return await self._generate_openai_vision(
                    model, system_prompt, user_text, images, max_tokens
                )
            case LLMProvider.GOOGLE:
                return await self._generate_google_vision(
                    model, system_prompt, user_text, images, max_tokens
                )
            case LLMProvider.ANTHROPIC:
                return await self._generate_anthropic_vision(
                    model, system_prompt, user_text, images, max_tokens
                )
            case LLMProvider.CUSTOM:
                return await self._generate_custom_vision(
                    model, system_prompt, user_text, images, max_tokens
                )
            case _:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider {self.provider.value} does not support vision"
                )

    async def _generate_openai_vision(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        images: List[Dict[str, str]],
        max_tokens: int,
    ) -> str:
        """Generate using OpenAI's vision API."""
        client: AsyncOpenAI = self._client

        # Build content array with images first, then text
        content = []
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['media_type']};base64,{img['base64']}",
                    "detail": "high"
                }
            })
        content.append({"type": "text", "text": user_text})

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=max_tokens,
            )

            if not response.choices or not response.choices[0].message.content:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI did not return any content"
                )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                raise HTTPException(
                    status_code=408,
                    detail=f"OpenAI API timeout: {error_msg}"
                )
            elif "connection" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail=f"OpenAI API connection error: {error_msg}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"OpenAI API error: {error_msg}"
                )

    async def _generate_google_vision(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        images: List[Dict[str, str]],
        max_tokens: int,
    ) -> str:
        """Generate using Google Gemini's vision API."""
        client: genai.Client = self._client

        # Build parts array with images and text
        parts = []
        for img in images:
            # Google expects inline_data format for base64 images
            parts.append(GooglePart.from_bytes(
                data=base64.b64decode(img['base64']),
                mime_type=img['media_type']
            ))
        parts.append(GooglePart.from_text(user_text))

        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model,
                contents=[GoogleContent(role="user", parts=parts)],
                config=GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=max_tokens,
                    response_mime_type="text/plain",
                )
            )

            if not response.candidates or not response.candidates[0].content.parts:
                raise HTTPException(
                    status_code=500,
                    detail="Google Gemini did not return any content"
                )

            # Extract text from response
            text_content = ""
            for part in response.candidates[0].content.parts:
                if part.text:
                    text_content += part.text

            if not text_content:
                raise HTTPException(
                    status_code=500,
                    detail="Google Gemini did not return text content"
                )

            return text_content

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e)
            raise HTTPException(
                status_code=500,
                detail=f"Google Gemini API error: {error_msg}"
            )

    async def _generate_anthropic_vision(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        images: List[Dict[str, str]],
        max_tokens: int,
    ) -> str:
        """Generate using Anthropic Claude's vision API."""
        client: AsyncAnthropic = self._client

        # Build content array with images first, then text
        content = []
        for img in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img['media_type'],
                    "data": img['base64']
                }
            })
        content.append({"type": "text", "text": user_text})

        try:
            response = await client.messages.create(
                model=model,
                system=system_prompt,
                messages=[{"role": "user", "content": content}],
                max_tokens=max_tokens,
            )

            if not response.content:
                raise HTTPException(
                    status_code=500,
                    detail="Anthropic Claude did not return any content"
                )

            # Extract text from response
            text_content = ""
            for block in response.content:
                if block.type == "text" and isinstance(block.text, str):
                    text_content += block.text

            if not text_content:
                raise HTTPException(
                    status_code=500,
                    detail="Anthropic Claude did not return text content"
                )

            return text_content

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                raise HTTPException(
                    status_code=408,
                    detail=f"Anthropic API timeout: {error_msg}"
                )
            elif "connection" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail=f"Anthropic API connection error: {error_msg}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Anthropic API error: {error_msg}"
                )

    async def _generate_custom_vision(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        images: List[Dict[str, str]],
        max_tokens: int,
    ) -> str:
        """
        Generate using a custom OpenAI-compatible API (e.g., OpenRouter).

        Uses the same format as OpenAI since most compatible APIs follow
        the OpenAI vision format.
        """
        client: AsyncOpenAI = self._client

        # Build content array with images first, then text (same as OpenAI)
        content = []
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['media_type']};base64,{img['base64']}",
                    "detail": "high"
                }
            })
        content.append({"type": "text", "text": user_text})

        # Build extra body for custom providers (e.g., disable thinking)
        extra_body = None
        if self._disable_thinking():
            extra_body = {"enable_thinking": False}

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=max_tokens,
                extra_body=extra_body,
            )

            if not response.choices or not response.choices[0].message.content:
                raise HTTPException(
                    status_code=500,
                    detail="Custom LLM did not return any content"
                )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                raise HTTPException(
                    status_code=408,
                    detail=f"Custom LLM API timeout: {error_msg}"
                )
            elif "connection" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail=f"Custom LLM API connection error: {error_msg}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Custom LLM API error: {error_msg}"
                )


def get_available_vision_providers() -> List[Dict]:
    """
    Get list of available vision providers based on configured API keys.

    Returns:
        List of provider dicts with id, name, and available status
    """
    providers = []

    # OpenAI
    if get_openai_api_key_env():
        providers.append({
            "id": "openai",
            "name": "OpenAI",
            "model": get_openai_model_env() or DEFAULT_OPENAI_MODEL,
            "available": True,
        })

    # Google
    if get_google_api_key_env():
        providers.append({
            "id": "google",
            "name": "Google Gemini",
            "model": get_google_model_env() or DEFAULT_GOOGLE_MODEL,
            "available": True,
        })

    # Anthropic
    if get_anthropic_api_key_env():
        providers.append({
            "id": "anthropic",
            "name": "Anthropic Claude",
            "model": get_anthropic_model_env() or DEFAULT_ANTHROPIC_MODEL,
            "available": True,
        })

    # Custom (OpenRouter, etc.)
    if get_custom_llm_url_env() and get_custom_model_env():
        providers.append({
            "id": "custom",
            "name": "Custom (OpenRouter)",
            "model": get_custom_model_env(),
            "available": True,
        })

    return providers


def get_default_vision_provider() -> str:
    """
    Get the default vision provider based on global LLM setting.

    Returns:
        Provider ID string
    """
    llm_provider = get_llm_provider_env()
    if llm_provider and llm_provider in ["openai", "google", "anthropic", "custom"]:
        return llm_provider

    # Fall back to first available provider
    providers = get_available_vision_providers()
    if providers:
        return providers[0]["id"]

    return "openai"
