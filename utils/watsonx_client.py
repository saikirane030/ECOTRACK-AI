# utils/watsonx_client.py
#
# This file handles ALL communication with IBM watsonx.ai.
# It is the only place in the project that calls the IBM API.
#
# There are two functions:
#   generate_text()  – sends a text prompt to the Granite instruction model
#   classify_image() – sends an image + prompt to a Granite vision deployment
#
# Both functions return (result_string, error_string).
# If the call succeeds, error_string is None.
# If the call fails, result_string is None and error_string explains what went wrong.
# The UI pages decide what to show the user based on which one is not None.
#
# This design keeps all error-handling in one place and keeps page code simple.

import os
import base64
import logging
from io import BytesIO

from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
# This has no effect when variables are already set (e.g. on Streamlit Cloud)
load_dotenv()

# ---------------------------------------------------------------------------
# CONFIGURATION  –  read from environment, never hardcoded
# ---------------------------------------------------------------------------

WATSONX_API_KEY         = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID      = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_REGION          = os.getenv("WATSONX_REGION", "us-south")
VISION_DEPLOYMENT_ID    = os.getenv("WATSONX_VISION_DEPLOYMENT_ID", "")

# The text model is a verified multitenant IBM Granite model.
# It does not require a deployment – it can be called directly by model ID.
# Source: IBM watsonx.ai documentation (Foundation Models – IBM Foundation Models)
TEXT_MODEL_ID = "ibm/granite-3-3-8b-instruct"

# Base URL pattern for the watsonx.ai REST API
# Docs: https://cloud.ibm.com/apidocs/watsonx-ai
WATSONX_BASE_URL = f"https://{WATSONX_REGION}.ml.cloud.ibm.com"

# ---------------------------------------------------------------------------
# HELPER: Check whether credentials are present
# ---------------------------------------------------------------------------

def is_text_ai_available() -> bool:
    """Returns True if the minimum credentials for text generation are set."""
    return bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)


def is_vision_ai_available() -> bool:
    """
    Returns True if a vision deployment ID is configured.
    The granite-vision model requires a dedicated 'deploy on demand' deployment
    and is NOT available on the Lite multitenant plan.
    """
    return bool(WATSONX_API_KEY and VISION_DEPLOYMENT_ID)


# ---------------------------------------------------------------------------
# HELPER: Get an IBM Cloud IAM Bearer token
# The IBM SDK handles this internally, but for the vision REST call we need it.
# ---------------------------------------------------------------------------

def _get_iam_token() -> tuple[str | None, str | None]:
    """
    Exchange an IBM Cloud API key for a short-lived IAM Bearer token.
    Returns (token, None) on success or (None, error_message) on failure.
    """
    import requests  # imported here to keep top-level imports minimal

    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": WATSONX_API_KEY,
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            return None, "IAM token response did not contain an access_token."
        return token, None
    except requests.exceptions.Timeout:
        return None, "IAM token request timed out. Check your internet connection."
    except requests.exceptions.RequestException as exc:
        return None, f"IAM token request failed: {exc}"


# ---------------------------------------------------------------------------
# TEXT GENERATION  –  uses the IBM watsonx.ai Python SDK
# ---------------------------------------------------------------------------

def generate_text(
    prompt: str,
    system_prompt: str = "",
    max_new_tokens: int = 512,
) -> tuple[str | None, str | None]:
    """
    Send a prompt to the IBM Granite instruction model and return the response.

    Parameters
    ----------
    prompt          : The user's question or instruction.
    system_prompt   : Optional system-level context (persona, rules).
    max_new_tokens  : Maximum length of the generated response.

    Returns
    -------
    (generated_text, None) on success
    (None, error_message)  on failure
    """
    if not is_text_ai_available():
        return None, (
            "AI assistant is not configured. "
            "Please add WATSONX_API_KEY and WATSONX_PROJECT_ID to your .env file."
        )

    try:
        # Import here so that the module loads even if the SDK is not installed
        # (useful during development before pip install runs)
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        credentials = Credentials(
            url=WATSONX_BASE_URL,
            api_key=WATSONX_API_KEY,
        )

        model = ModelInference(
            model_id=TEXT_MODEL_ID,
            project_id=WATSONX_PROJECT_ID,
            credentials=credentials,
            params={
                "max_new_tokens": max_new_tokens,
                "temperature": 0.3,       # lower = more factual, less creative
                "repetition_penalty": 1.1,
            },
        )

        # Build the full prompt by prepending the system prompt if provided
        if system_prompt:
            full_prompt = f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{prompt}"
        else:
            full_prompt = prompt

        response = model.generate_text(prompt=full_prompt)
        return response, None

    except ImportError:
        return None, (
            "The ibm-watsonx-ai package is not installed. "
            "Run: pip install ibm-watsonx-ai"
        )
    except Exception as exc:  # noqa: BLE001
        # Log the full error for debugging but return a clean message to the UI
        logging.error("watsonx text generation error: %s", exc)
        return None, f"IBM watsonx.ai returned an error: {exc}"


# ---------------------------------------------------------------------------
# IMAGE CLASSIFICATION  –  uses the vision deployment REST endpoint
# ---------------------------------------------------------------------------

def classify_image(
    image_bytes: bytes,
    image_mime_type: str,
    prompt: str,
) -> tuple[str | None, str | None]:
    """
    Send an image + prompt to the configured Granite vision deployment.

    The granite-vision model is a deploy-on-demand model that requires a
    separate deployment (not available on the Lite multitenant plan).
    This function is only called when VISION_DEPLOYMENT_ID is set.

    Parameters
    ----------
    image_bytes     : Raw image bytes (from the uploaded file).
    image_mime_type : MIME type string, e.g. "image/jpeg" or "image/png".
    prompt          : Text instruction to accompany the image.

    Returns
    -------
    (response_text, None) on success
    (None, error_message)  on failure
    """
    if not is_vision_ai_available():
        return None, (
            "Vision AI is not configured. "
            "WATSONX_VISION_DEPLOYMENT_ID is not set in your .env file."
        )

    import requests  # imported here to keep top-level imports minimal

    # Step 1 – Get an IAM token
    token, err = _get_iam_token()
    if err:
        return None, err

    # Step 2 – Encode the image as base64 for the API payload
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Step 3 – Build the API request
    # Endpoint pattern for a deployment inference call:
    # POST /ml/v1/deployments/{deployment_id}/text/generation
    # Docs: https://cloud.ibm.com/apidocs/watsonx-ai#deployments-text-generation
    url = (
        f"{WATSONX_BASE_URL}/ml/v1/deployments/"
        f"{VISION_DEPLOYMENT_ID}/text/generation?version=2024-05-01"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "input": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_mime_type};base64,{image_b64}"
                },
            },
            {
                "type": "text",
                "text": prompt,
            },
        ],
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.1,   # low temperature = more consistent classification
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Extract generated text from the response structure
        generated = (
            result.get("results", [{}])[0]
            .get("generated_text", "")
            .strip()
        )
        if not generated:
            return None, "Vision model returned an empty response."
        return generated, None

    except requests.exceptions.Timeout:
        return None, "Vision API request timed out. The image may be too large."
    except requests.exceptions.RequestException as exc:
        logging.error("watsonx vision error: %s", exc)
        return None, f"Vision API request failed: {exc}"
