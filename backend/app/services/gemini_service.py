"""Google Gemini Free Tier LLM Service.

Uses the official Google Generative AI REST API (no SDK required — just httpx).
Free tier supports: gemini-1.5-flash (recommended), gemini-1.5-pro

Get your free API key at: https://aistudio.google.com/app/apikey

Usage:
    from backend.app.services.gemini_service import gemini_service

    if gemini_service.is_enabled():
        text = gemini_service.generate_text("Summarise these findings...")
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Gemini REST endpoint — free tier uses v1beta
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiService:
    """Client for the Google Gemini free-tier API.

    Uses the generateContent REST endpoint — no SDK dependency needed.
    Recommended free model: gemini-1.5-flash (fast, generous free quota).
    """

    def __init__(self):
        self._api_key: str = settings.GEMINI_API_KEY
        self._model: str = settings.GEMINI_MODEL       # e.g. "gemini-1.5-flash"
        # Only enabled if key is set, non-empty, and not the placeholder value
        _key_valid = bool(
            self._api_key
            and self._api_key != "your_gemini_api_key_here"
            and self._api_key.startswith("AIza")
        )
        self._enabled: bool = bool(settings.GEMINI_ENABLED and _key_valid)

    def is_enabled(self) -> bool:
        """Return True if Gemini is configured and enabled."""
        return bool(self._enabled and self._api_key)

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = (
            "You are an expert sustainability analyst helping audit campus "
            "energy, water, and waste data. Be factual, concise, and precise."
        ),
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> Optional[str]:
        """Send a prompt to Gemini and return the generated text.

        Returns None if Gemini is not enabled or if the request fails.
        """
        if not self.is_enabled():
            logger.debug("[GeminiService] Gemini is disabled or API key not set — skipping LLM call.")
            return None

        url = f"{GEMINI_API_BASE}/{self._model}:generateContent?key={self._api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                # Navigate Gemini response structure
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"[GeminiService] HTTP error {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"[GeminiService] Request error: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"[GeminiService] Unexpected response format: {e}")
        return None

    def generate_audit_summary(
        self, findings: list[dict], campus_name: str
    ) -> Optional[str]:
        """Generate an AI-powered executive narrative summary for the audit report."""
        if not findings:
            return None

        findings_text = "\n".join(
            f"- [{f.get('severity', 'N/A').upper()}] {f.get('title', 'N/A')}: {f.get('description', '')}"
            for f in findings[:15]  # Cap to avoid token limits
        )
        prompt = (
            f"Campus: {campus_name}\n\n"
            f"Sustainability Audit Findings:\n{findings_text}\n\n"
            f"Write a concise executive summary (3–5 paragraphs) covering: "
            f"overall sustainability status, key risk areas, and top 3 recommended actions. "
            f"Be specific and factual. Do not invent statistics not present in the data."
        )
        return self.generate_text(
            prompt=prompt,
            system_instruction=(
                "You are a sustainability expert writing an executive summary for a campus audit report. "
                "Be factual, concise, and actionable. Never fabricate statistics."
            ),
            max_tokens=800,
        )

    def generate_action_rationale(
        self, action_title: str, finding_desc: str
    ) -> Optional[str]:
        """Generate a short rationale for a recommended action."""
        prompt = (
            f"Finding: {finding_desc}\n"
            f"Recommended Action: {action_title}\n\n"
            f"In 2–3 sentences, explain why this action matters and what impact it will have."
        )
        return self.generate_text(prompt=prompt, max_tokens=300)


# Singleton instance — imported by other modules
gemini_service = GeminiService()
