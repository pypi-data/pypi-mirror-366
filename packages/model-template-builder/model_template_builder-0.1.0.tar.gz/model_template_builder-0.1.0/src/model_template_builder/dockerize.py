import tempfile
import pathlib
from typing import Optional

import docker
from huggingface_hub import list_models
import re

def normalize_image_name(model_name: str) -> str:
    name = model_name.replace("/", "_")
    name = name.lower()
    name = re.sub(r"[^a-z0-9._-]", "-", name)
    return f"hugging_face/{name}:latest"

def dockerize_hugging_face_model_vllm(model_name: str, image_name: Optional[str]) -> bool:
    if not image_name:
        image_name = normalize_image_name(model_name)
    if not list_models(model_name=model_name, sort='downloads', limit=1):
        print(f"Model {model_name} not found on Hugging Face.")
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)

        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(f"""
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install system dependencies
RUN apt update && apt install -y git python3-pip && rm -rf /var/lib/apt/lists/*

# Install vLLM
RUN pip install --upgrade pip && pip install vllm

# Run vLLM server and download model at runtime
CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", "--model", "{model_name}", "--host", "0.0.0.0", "--port", "8000"]
""")

        client = docker.from_env()
        print(f"Building Docker image `{image_name}`...")
        client.images.build(path=str(tmp_path), tag=image_name)
        print(f"Docker image `{image_name}` built successfully.")
        print("Usage: docker run -p 8000:8000 -e HUGGING_FACE_HUB_TOKEN=<your-hugging-face-hub-token> --gpus all -t <your-image-name>:latest")

    return True
