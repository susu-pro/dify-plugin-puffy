"""
Puffy Media Extractor — Dify Plugin Tool

Calls the local Puffy daemon's REST API to extract video, audio,
and transcripts from supported platforms (YouTube, TikTok, Bilibili, X, etc.).

Requires Puffy running locally:
  - GUI mode: just open Puffy.app
  - Headless: puffy serve
"""

import json
from typing import Any
from urllib.parse import urljoin

import requests


HEALTH_PATH = "/api/health"
EXTRACT_PATH = "/api/extract"
DEFAULT_ENDPOINT = "http://127.0.0.1:41480"
TIMEOUT_HEALTH = 3
TIMEOUT_EXTRACT = 300  # 5 minutes — downloads can be slow


class ExtractMediaTool:
    """Dify tool implementation for Puffy media extraction."""

    name = "extract_media"

    def _invoke(self, tool_parameters: dict[str, Any], **kwargs) -> str:
        endpoint = (
            kwargs.get("credentials", {}).get("puffy_endpoint", "").strip()
            or DEFAULT_ENDPOINT
        )
        url = tool_parameters.get("url", "").strip()
        if not url:
            return json.dumps({"error": "Missing required parameter: url"})

        # 1. Health check
        try:
            health = requests.get(
                urljoin(endpoint, HEALTH_PATH), timeout=TIMEOUT_HEALTH
            )
            health.raise_for_status()
        except Exception:
            return json.dumps(
                {
                    "error": (
                        "Puffy daemon is not reachable. "
                        "Please install and start Puffy first: "
                        "https://github.com/susu-pro/puffy"
                    )
                }
            )

        # 2. Extract
        payload = {"url": url}
        save_dir = tool_parameters.get("save_dir", "").strip()
        if save_dir:
            payload["saveDir"] = save_dir

        try:
            response = requests.post(
                urljoin(endpoint, EXTRACT_PATH),
                json=payload,
                timeout=TIMEOUT_EXTRACT,
            )
            response.raise_for_status()
            return json.dumps(response.json(), ensure_ascii=False)
        except requests.Timeout:
            return json.dumps({"error": "Extraction timed out after 5 minutes."})
        except Exception as exc:
            return json.dumps({"error": f"Extraction failed: {exc}"})
