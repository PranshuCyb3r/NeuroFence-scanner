import os
import hashlib
import json
from typing import Dict, Any
from safetensors.torch import load_file

def calculate_file_hashes(file_path: str) -> Dict[str, str]:
    """Calculate SHA-256 hash for integrity verification."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return {
        "sha256": sha256.hexdigest()
    }

def inspect_safetensors_metadata(file_path: str) -> Dict[str, Any]:
    """
    Safely inspects SafeTensors checkpoint metadata and tensor headers 
    without running arbitrary Python bytecode (Zero Code Execution).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model checkpoint not found at: {file_path}")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    file_hashes = calculate_file_hashes(file_path)

    # Inspect tensors safely
    tensors = load_file(file_path)
    total_params = 0
    tensors_info = []

    for name, tensor in tensors.items():
        param_count = tensor.numel()
        total_params += param_count
        tensors_info.append({
            "name": name,
            "shape": list(tensor.shape),
            "dtype": str(tensor.dtype)
        })

    # Formatting parameter count
    if total_params >= 1e9:
        param_str = f"{total_params / 1e9:.2f}B (SmolLM / TinyLlama Class)"
    elif total_params >= 1e6:
        param_str = f"{total_params / 1e6:.1f}M Parameters"
    else:
        param_str = f"{total_params:,} Parameters"

    return {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "size_mb": round(file_size_mb, 2),
        "sha256": file_hashes["sha256"],
        "total_parameters": param_str,
        "tensor_count": len(tensors),
        "primary_dtype": str(tensors_info[0]["dtype"]) if tensors_info else "FP16 (Half Precision)",
        "serialization": "SafeTensors (Zero-Code Exec)",
        "tensors": tensors_info
    }

if __name__ == "__main__":
    print("--- NeuroFence Safe Ingestion Engine: OK ---")