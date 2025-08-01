import os
import tempfile
import importlib.util
import json
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Dynamically determine package version:
try:
    # Prefer installed package metadata (works for wheels & sdist installs)
    from importlib.metadata import version as _version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version as _version, PackageNotFoundError

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    # Fallback to VERSION file in source distribution
    try:
        here = os.path.dirname(__file__)
        with open(os.path.join(here, '..', 'VERSION'), 'r') as vf:
            __version__ = vf.read().strip()
    except Exception:
        __version__ = '0.0.0'

def load_encrypted_module(module_name, file_path, key):
    print(f"Attempting to decrypt {file_path} as {module_name}")
    cipher = Fernet(key)
    with open(file_path, 'rb') as f:
        data = f.read()
    try:
        decrypted = cipher.decrypt(data)
        print(f"Decrypted {len(decrypted)} bytes for {module_name}")
    except InvalidToken:
        # Not an encrypted payload; load the raw shared object
        print(f"{file_path} is not encrypted, loading raw module")
        decrypted = data
    # Write the (decrypted or raw) data to a temp file for import
    with tempfile.NamedTemporaryFile(suffix='.so', delete=False) as tmp:
        tmp.write(decrypted)
        tmp_path = tmp.name
    spec = importlib.util.spec_from_file_location(module_name, tmp_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    os.remove(tmp_path)
    print(f"Successfully loaded {module_name}")
    return module

# Load encrypted modules in dependency order
_ENFORCE = os.getenv("AGENTFOUNDRY_ENFORCE_LICENSE", "0") == "1"

if _ENFORCE:
    license_key = None
    modules_to_load = []
    dependency_order = [
        "agentfoundry.registry.tool_registry",
        "agentfoundry.registry.database",
        "agentfoundry.utils.logger",
        "agentfoundry.utils.config",
        "agentfoundry.utils.exceptions",
        "agentfoundry.agents.base_agent",
        # Add other critical dependencies here
    ]

    # Collect all .so files
    for root, _, files in os.walk(os.path.dirname(__file__)):
        for file in files:
            if file.endswith('.so') and not file.endswith('.so.enc'):
                rel = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                name = rel.replace(os.sep, '.')[:-len('.cpython-311-x86_64-linux-gnu.so')]
                modules_to_load.append((name, os.path.join(root, file)))

    # Sort modules to prioritize dependencies
    modules_to_load.sort(
        key=lambda x: (
            0 if x[0] in dependency_order else 1,
            dependency_order.index(x[0]) if x[0] in dependency_order else len(dependency_order),
        )
    )

    for module_name, module_path in modules_to_load:
        if license_key is None:
            print("Retrieving decryption key...")
            try:
                with open(os.path.join(os.path.dirname(__file__), "agentfoundry.lic"), 'r') as f:
                    ld = json.load(f)
                with open(os.path.join(os.path.dirname(__file__), "agentfoundry.pem"), 'rb') as f:
                    pk = serialization.load_pem_public_key(f.read(), backend=default_backend())
                sig = base64.b64decode(ld['signature'])
                payload = json.dumps(ld['content'], sort_keys=True).encode()
                pk.verify(sig, payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                license_key = base64.b64decode(ld['content']['decryption_key'])
                print(f"Decryption key: {license_key}")
            except Exception as e:
                print(f"Failed to retrieve decryption key: {type(e).__name__}: {e}")
                raise RuntimeError("Failed to retrieve decryption key")
        try:
            module = load_encrypted_module(module_name, module_path, license_key)
            globals()[module_name] = module
        except Exception as e:
            print(f"Failed to process {module_name}: {type(e).__name__}: {e}")

    # Import modules after successful decryption
    from .registry.tool_registry import ToolRegistry
    from .agents.base_agent import BaseAgent
    from .agents.orchestrator import Orchestrator
    from .license.license import enforce_license, verify_license
    from .license.key_manager import get_license_key

    __all__ = [
        "ToolRegistry",
        "BaseAgent",
        "Orchestrator",
        "enforce_license",
        "get_license_key",
    ]
else:
    # Skip decryption/extension loading; import APIs directly
    from .registry.tool_registry import ToolRegistry
    from .agents.base_agent import BaseAgent
    from .agents.orchestrator import Orchestrator
    from .license.license import enforce_license, verify_license
    from .license.key_manager import get_license_key

    __all__ = [
        "ToolRegistry",
        "BaseAgent",
        "Orchestrator",
        "enforce_license",
        "get_license_key",
    ]
