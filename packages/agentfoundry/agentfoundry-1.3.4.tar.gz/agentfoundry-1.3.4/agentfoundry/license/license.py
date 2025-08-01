__author__ = "Chris Steel"
__copyright__ = "Copyright 2025, Syntheticore Corporation"
__credits__ = ["Chris Steel"]
__date__ = "9/22/2023"
__license__ = "Syntheticore Confidential"
__version__ = "1.0"
__email__ = "csteel@syntheticore.com"
__status__ = "Production"

import os
import uuid
import platform
import json
import base64
from datetime import datetime

import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

LICENSE_FILE = os.path.join(os.path.dirname(__file__), "..", "agentfoundry.lic")
PUBLIC_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "agentfoundry.pem")


def get_machine_id() -> str:
    return str(uuid.getnode()) + platform.node()


def verify_signature(content: dict, signature: bytes) -> bool:
    try:
        key = serialization.load_pem_public_key(open(PUBLIC_KEY_FILE, 'rb').read(), backend=default_backend())
        content_str = json.dumps(content, sort_keys=True).encode()
        key.verify(
            signature,
            content_str,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (ValueError, cryptography.exceptions.InvalidSignature):
        return False


def verify_license() -> bool:
    if not os.path.exists(LICENSE_FILE):
        raise RuntimeError(f"License file not found: {LICENSE_FILE}")

    with open(LICENSE_FILE, "r") as f:
        license_data = json.load(f)

    content = license_data.get("content")
    signature = base64.b64decode(license_data.get("signature"))
    if not content or not signature:
        raise RuntimeError("Invalid license format")

    # Verify signature
    if not verify_signature(content, signature):
        return False

    # Expiration check
    expiry = content.get("expiry")
    if datetime.today().date() > datetime.strptime(expiry, "%Y-%m-%d").date():
        raise RuntimeError("AIgent license has expired")

    # Machine ID check
    if content.get("machine_id") != get_machine_id():
        raise RuntimeError("AIgent license is not valid for this machine")

    return True


def enforce_license():
    if not verify_license():
        raise RuntimeError("Invalid, tampered, or expired AIgent license.")
