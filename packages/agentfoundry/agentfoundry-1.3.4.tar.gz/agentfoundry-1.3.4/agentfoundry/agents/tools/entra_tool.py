# entra_tool.py

import json
import logging
import sys
from threading import Lock
import time

import msal
import requests
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
from agentfoundry.utils.config import Config

# Load configuration for Microsoft Graph credentials
CONFIG = Config()
CLIENT_ID = CONFIG.get("MS.CLIENT_ID")
TENANT_ID = CONFIG.get("MS.TENANT_ID")
# Determine if credentials are missing (tool will be disabled if so)
config_missing = not CLIENT_ID or not TENANT_ID

# Delegated scopes for reading mail & calendar
SCOPES = ["Mail.Read", "Calendars.Read"]

# -------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------
logger = logging.getLogger("entra_tool")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s - %(name)-16s:%(lineno)-4s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(handler)

# Warn if credentials are missing (tool functionality will error on invocation)
if config_missing:
    logger.warning(
        "MS.CLIENT_ID and MS.TENANT_ID not set in configuration; entra_tool disabled."
    )
# Initialize MSAL cache and placeholders for lazy client initialization
_cache = msal.SerializableTokenCache()
_app = None
_lock = Lock()


def get_delegated_token() -> str:
    """
    Acquire or reuse an access token via device code flow.
    Blocks on first call to have user sign in; then uses cache.
    """
    # Ensure credentials are available and initialize MSAL client lazily
    if config_missing:
        raise RuntimeError("MS.CLIENT_ID and MS.TENANT_ID must be set in your configuration.")
    global _app
    if _app is None:
        _app = msal.PublicClientApplication(
            client_id=CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            token_cache=_cache
        )
    with _lock:
        # Try silent first
        accounts = _app.get_accounts()
        if accounts:
            logger.debug("Attempting silent token acquisition for %s", accounts[0]["username"])
            result = _app.acquire_token_silent(SCOPES, account=accounts[0])
            if result and "access_token" in result:
                logger.info("Reused token for %s", accounts[0]["username"])
                return result["access_token"]

        # No cached token: start device code flow
        logger.info("Starting device code flow for scopes: %s", SCOPES)
        flow = _app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            logger.error("Device flow initiation failed: %s", flow)
            raise RuntimeError(f"Device flow error: {flow}")
        print(flow["message"])  # instruct user
        # Wait up to flow['expires_in'] seconds, polling internally
        result = _app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            logger.error("Device flow token error: %s", result)
            raise RuntimeError(f"Device flow token error: {result.get('error_description', result)}")
        user = result.get("id_token_claims", {}).get("preferred_username", "<unknown>")
        logger.info("Acquired new token for %s", user)
        return result["access_token"]

# -------------------------------------------------------------------
# Input model
# -------------------------------------------------------------------
class EntraInput(BaseModel):
    method: str = Field(..., description="HTTP method: GET, POST, etc.")
    path: str = Field(..., description="Graph API path, e.g. 'me/messages'")
    query_params: dict = Field(default_factory=dict)
    body: dict = Field(default_factory=dict)

# -------------------------------------------------------------------
# Core request
# -------------------------------------------------------------------
def make_entra_request(raw_input) -> dict:
    """
    Execute a delegated Graph request under /me.
    Accepts EntraInput or JSON/dict/string.
    """
    logger.info("make_entra_request invoked")
    # 1) Normalize input
    if isinstance(raw_input, EntraInput):
        inp = raw_input
        logger.debug("Using passed EntraInput: %s", inp)
    else:
        try:
            # If it's a simple string GET path, wrap it
            if isinstance(raw_input, str) and not raw_input.strip().startswith("{"):
                method = "GET"
                path = raw_input.strip()
                inp = EntraInput(method=method, path=path)
                logger.debug("Wrapped raw string into EntraInput: %s", inp)
            else:
                data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
                inp = EntraInput(**data)
                logger.debug("Parsed JSON into EntraInput: %s", data)
        except Exception as e:
            logger.error("Failed to parse input: %s", e, exc_info=True)
            return {"error": f"Invalid input for EntraInput: {e}"}

    method = inp.method.upper()
    if method not in {"GET","POST","PUT","PATCH","DELETE"}:
        logger.error("Unsupported HTTP method: %s", method)
        return {"error": f"Unsupported HTTP method: {method}"}

    # 2) Force /me prefix
    raw_path = inp.path.lstrip("/")
    if raw_path.startswith("users/") or raw_path.startswith("https://"):
        # Strip users/{UPN} or full URL
        # e.g. users/alice@mail/...  → remove prefix up to /v1.0/
        parts = raw_path.split("/v1.0/",1)
        raw_path = parts[-1]
        logger.debug("Stripped full users path to: %s", raw_path)
    if not raw_path.startswith("me/"):
        raw_path = f"me/{raw_path}"
        logger.debug("Prefixed path with 'me/': %s", raw_path)

    url = f"https://graph.microsoft.com/v1.0/{raw_path}"
    logger.info("Prepared URL: %s %s", method, url)

    # 3) Get token
    try:
        token = get_delegated_token()
        logger.debug("Token length: %d", len(token))
    except Exception as e:
        return {"error": f"Token acquisition error: {e}"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }

    # 4) Perform HTTP call
    logger.debug("Headers: %s", headers)
    logger.debug("Query params: %s, Body: %s", inp.query_params, inp.body)
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            params=inp.query_params or None,
            json=inp.body or None,
            timeout=15
        )
        logger.info("HTTP %s → status %d", method, resp.status_code)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"message": "Success − no content"}
        data = resp.json()
        logger.debug("Response JSON: %s", data)
        return data
    except requests.exceptions.HTTPError as e:
        logger.error("Graph API error: %s (%s)", e, resp.text)
        return {"error": str(e), "status": resp.status_code, "body": resp.text}
    except Exception as e:
        logger.exception("Unexpected error")
        return {"error": str(e)}

# -------------------------------------------------------------------
# LangChain tool export
# -------------------------------------------------------------------
if not config_missing:
    from langchain_core.tools import Tool

    entra_tool = Tool(
        name="entra_tool",
        func=make_entra_request,
        description="Calls Microsoft Graph under /me using delegated device-code authentication"
    )
