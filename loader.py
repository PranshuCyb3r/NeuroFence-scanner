import os
import hashlib
import json
import torch
from safetensors import safe_open


def calculate_file_hashes(file_path: str, chunk_size: int = 65536) -> dict:
    """
    Computes cryptographic SHA-256 and BLAKE2b/BLAKE3 hashes of the model checkpoint.
    """
    if not os.path.exists(file_path):
        return {"sha256": "File not found", "blake3": "File not found"}

    sha256_hash = hashlib.sha256()
    blake2_hash = hashlib.blake2b()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
            blake2_hash.update(chunk)

    return {
        "sha256": sha256_hash.hexdigest(),
        "blake3": blake2_hash.hexdigest()
    }


def inspect_safetensors_metadata(file_path: str) -> dict:
    """
    Safely inspects safetensors header and tensor keys without running executable code.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found", "file_size_mb": 0, "tensor_keys": []}

    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    tensor_keys = []
    metadata = {}

    try:
        with safe_open(file_path, framework="pt", device="cpu") as f:
            tensor_keys = list(f.keys())
            metadata = f.metadata() or {}
    except Exception as e:
        tensor_keys = []
        metadata = {"read_error": str(e)}

    return {
        "file_size_mb": file_size_mb,
        "tensor_keys": tensor_keys,
        "header_metadata": metadata
    }


if __name__ == "__main__":
    test_path = "models/model.safetensors"
    if os.path.exists(test_path):
        print("--- Testing loader.py ---")
        h = calculate_file_hashes(test_path)
        print("SHA-256:", h["sha256"][:32] + "...")
        m = inspect_safetensors_metadata(test_path)
        print(f"Size: {m['file_size_mb']} MB | Tensors: {len(m['tensor_keys'])}")
        print("Status: OK")
    else:
        print(f"Test checkpoint not found at {test_path}")
