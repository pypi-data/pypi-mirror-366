__author__ = "Chris Steel"
__copyright__ = "Copyright 2023, Syntheticore Corporation"
__credits__ = ["Chris Steel"]
__date__ = "10/23/2023"
__license__ = "Syntheticore Confidential"
__version__ = "1.0"
__email__ = "csteel@syntheticore.com"
__status__ = "Production"

import base64
import json

import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import os


def get_license_key(license_file=None, public_key_file=None):
    """
    Retrieve the decryption key from the RSA-signed license file.

    Args:
        license_file (str): Path to the license file.
        public_key_file (str): Path to the public key file.

    Returns:
        bytes: Decryption key for encrypted .so files, or None if verification fails.
    """
    license_file = license_file or os.path.join(os.path.dirname(__file__), "..", "agentfoundry.lic")
    public_key_file = public_key_file or os.path.join(os.path.dirname(__file__), "..", "agentfoundry.pem")
    if not os.path.exists(license_file):
        raise RuntimeError(f"License key file not found: {license_file}")
    if not os.path.exists(public_key_file):
        raise RuntimeError(f"Public key file not found: {public_key_file}")
    try:
        # Read the license file
        with open(license_file, 'r') as f:
            license_data = json.load(f)

        # Extract components
        signature = base64.b64decode(license_data['signature'])
        license_content = license_data['content']  # Contains key and metadata

        # Load public key
        with open(public_key_file, 'rb') as f:
            public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

        # Verify signature
        public_key.verify(
            signature,
            json.dumps(license_content, sort_keys=True).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Extract and return the decryption key (base64-encoded in license)
        return base64.b64decode(license_content['decryption_key'])

    except (FileNotFoundError, KeyError, ValueError, cryptography.exceptions.InvalidSignature):
        # Return None if license is invalid or missing
        raise RuntimeError("Invalid, tampered, or expired AIgent license.")


if __name__ == "__main__":
    # Example usage
    decryption_key = get_license_key(license_file="agentfoundry.lic", public_key_file="agentfoundry.pem")
    if decryption_key:
        print("Decryption key retrieved successfully.")
    else:
        print("Failed to retrieve decryption key.")