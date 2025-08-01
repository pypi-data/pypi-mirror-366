import ast
import io
import os
import time
from typing import Any, Dict, List

import numpy as np
import torch
from diffusers import DiffusionPipeline as HFDiffusionPipeline
from PIL import Image
from qlip_serve.common.model import BaseModel, SeqEnsembleModel
from qlip_serve.common.model_config import DynamicBatcher, ModelConfig
from qlip_serve.common.signature import ImageSignature, TensorSignature, TextSignature

from elastic_models.diffusers import DiffusionPipeline as EMDiffusionPipeline

# ----------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------
allowed_model_size = ("XL", "L", "M", "S", "eager")
model_size_env = "MODEL_SIZE"
model_size = os.getenv(model_size_env)
if not isinstance(model_size, str) or model_size not in allowed_model_size:
    raise ValueError(
        f"Invalid or missing {repr(model_size_env)} environment variable, must have one of these values "
        f"[{', '.join(map(repr, allowed_model_size))}], but got {repr(model_size)}."
    )

allowed_batch_size = list(range(1, 32 + 1))
max_batch_size_env = "BATCH_SIZE"
max_batch_size = os.getenv(max_batch_size_env)
try:
    max_batch_size = int(max_batch_size)
    if max_batch_size not in allowed_batch_size:
        raise ValueError()
except ValueError:
    raise ValueError(
        f"Invalid {repr(max_batch_size_env)} environment variable, must have one of these values "
        f"[{', '.join(map(repr, allowed_batch_size))}], but got {repr(max_batch_size)}"
    )

model_repo_env = "MODEL_REPO"
model_repo = os.environ.get(model_repo_env)
if not model_repo:
    raise ValueError(f"Environment variable {repr(model_repo_env)} must be set.")

# Generate model name dynamically based on repo and size
base_name = model_repo.split("/")[1].lower().replace(".", "-")
size_lower = model_size.lower()
model_name = f"{base_name}-{size_lower}-bs{max_batch_size}"

model_hf_commit_hash_env = "MODEL_HF_COMMIT_HASH"
commit_hash = os.environ.get(model_hf_commit_hash_env)

model_hf_load_env = "MODEL_HF_LOAD"
model_hf_load = os.environ.get(model_hf_load_env)
if model_hf_load is not None:
    model_hf_load = model_hf_load.lower() in ("true", "1", "t")
else:
    model_hf_load = True

# Project directory
PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/project")

# Hugging Face configuration
HF_TOKEN = os.environ.get("HUGGINGFACE_ACCESS_TOKEN")
# TODO: parametrize through build_model params
HF_CACHE_DIR = os.path.join(PROJECT_DIR, ".cache", "huggingface")

# Default generation configuration
if model_repo == "black-forest-labs/FLUX.1-schnell":
    MODEL_GENERATION_CONFIG = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 4,
        "guidance_scale": 6.5,
        "num_images_per_prompt": 1,
    }
elif model_repo == "black-forest-labs/FLUX.1-dev":
    MODEL_GENERATION_CONFIG = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 28,
        "guidance_scale": 6.5,
        "num_images_per_prompt": 1,
    }
elif model_repo == "stabilityai/stable-diffusion-xl-base-1.0":
    MODEL_GENERATION_CONFIG = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 20,
        "guidance_scale": 6.5,
        "num_images_per_prompt": 1,
    }
else:
    raise ValueError(f"Model {repr(model_repo)} not supported yet.")


class Model(BaseModel):
    model_name = "model"
    inputs = [
        TextSignature(shape=(1,), dtype=np.object_, name="pos_prompt", external=True),
        TensorSignature(shape=(1,), dtype=np.uint32, name="seed", external=True),
    ]
    outputs = [
        ImageSignature(
            shape=(-1, -1, 3), dtype=np.uint8, name="image_pil", external=False
        ),
        TextSignature(
            shape=(1,), dtype=np.bytes_, name="metadata_internal", external=False
        ),
    ]
    device_type = "gpu"  # if torch.cuda.is_available() else "cpu"
    model_config = ModelConfig(
        max_batch_size=max_batch_size,
        batcher=DynamicBatcher(
            preferred_batch_size=[max_batch_size], preserve_ordering=False
        ),
    )

    def __init__(self):
        super().__init__()
        # Set device and precision
        self.device = "cuda" if self.device_type == "gpu" else "cpu"
        torch_dtype = torch.bfloat16 if self.device_type == "gpu" else torch.float32

        # Basic model initialization parameters
        init_params = {
            "torch_dtype": torch_dtype,
        }

        # Set generation configuration
        self.generation_config: dict[str, Any] = MODEL_GENERATION_CONFIG.copy()

        # Load model based on size
        if model_size == "eager":
            pipe_class = HFDiffusionPipeline
        else:
            init_params.update({"mode": model_size})
            pipe_class = EMDiffusionPipeline

        if model_hf_load:
            # Download from HF
            local_files_only = False
            cache_dir = HF_CACHE_DIR
        else:
            # Download from S3 (Should be consistent with S3 path)
            local_files_only = True
            # We need to copy all the files from S3 model directory
            # Because the snapshot directory symlinks to the files in the neighbors directories
            cache_dir = os.path.join(
                PROJECT_DIR,
                "artifacts/huggingface/hub/",
            )

        global_init_params = {
            "local_files_only": local_files_only,
            "cache_dir": cache_dir,
            "pretrained_model_name_or_path": model_repo,
        }

        if commit_hash:
            global_init_params["revision"] = commit_hash

        if model_hf_load:
            global_init_params["token"] = HF_TOKEN

        # Load model and tokenizer
        self.pipe = pipe_class.from_pretrained(
            **global_init_params,
            **init_params,
        ).to(self.device)

        self.pipe.set_progress_bar_config(leave=False)

        if model_size != "eager":
            print("Starting warmup...", flush=True)
            # Warmup run
            with torch.inference_mode():
                self.pipe(
                    prompt=["warmup"] * max_batch_size,
                    **self.generation_config,
                )
            print("Warmup completed.", flush=True)

    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Any]:
        # Example input:
        # {'pos_prompt': [array([b'test'], dtype=object)], 'sampler': [array([b'euler_a'], dtype=object)], 'inference_steps': [array([20], dtype=uint8)], 'height': [array([32], dtype=uint8)], 'width': [array([32], dtype=uint8)], 'num_inference_steps': [array([20], dtype=uint8)], 'guidance_scale': [array([7.5], dtype=float32)], 'seed': [array([164], dtype=uint8)]}
        num_inputs = len(inputs["pos_prompt"])

        # print(inputs, flush=True)

        # We need separate-state generators for each input
        # To get the same results for the same seed
        generator = []
        for i in range(num_inputs):
            generator.append(
                # You could use "cpu" for more deterministic results
                torch.Generator(device=self.device).manual_seed(
                    int(inputs["seed"][i][0])
                )
            )
        start_time = time.time()
        with torch.inference_mode():
            images = self.pipe(
                prompt=[p[0].decode() for p in inputs["pos_prompt"]],
                generator=generator,
                output_type="pil",
                **self.generation_config,
            ).images
        generation_time = (time.time() - start_time) / num_inputs

        # It will be more efficient for speed to convert images to uint8 or with lossy codec
        result = []
        for i in range(num_inputs):
            result.append(
                {
                    "image_pil": images[i],
                    "metadata_internal": [
                        {
                            "generation_time": generation_time,
                            "batch_size": num_inputs,
                            "seed": int(inputs["seed"][i][0]),
                        }
                    ],
                }
            )

        return result


class PostProcessor(BaseModel):
    model_name = "postprocessor"
    inputs = [
        ImageSignature(
            shape=(-1, -1, 3), dtype=np.uint8, name="image_pil", external=False
        ),
        TextSignature(
            shape=(1,), dtype=np.bytes_, name="metadata_internal", external=False
        ),
    ]
    outputs = [
        ImageSignature(shape=(1,), dtype=np.bytes_, name="image", external=True),
        TextSignature(shape=(1,), dtype=np.bytes_, name="metadata", external=True),
    ]
    device_type = "cpu"
    model_config = ModelConfig(
        max_batch_size=max_batch_size,
        batcher=DynamicBatcher(
            preferred_batch_size=[max_batch_size], preserve_ordering=False
        ),
    )
    model_count = 4

    def serialize_image(self, image_array: np.ndarray, format="WEBP", **params):
        buffer = io.BytesIO()
        pil_image = Image.fromarray(image_array)

        # Save image to buffer
        pil_image.save(buffer, format=format, **params)
        image_bytes = buffer.getvalue()
        return image_bytes

    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Dict[str, Any]]:
        num_inputs = len(inputs["image_pil"])

        # It will be more efficient for speed to convert images to uint8 or with lossy codec
        result = []
        for i in range(num_inputs):
            image_pil = inputs["image_pil"][i]
            start_time = time.time()
            image = self.serialize_image(image_pil, format="WEBP", quality=80)
            postprocessing_time = time.time() - start_time
            metadata = ast.literal_eval(inputs["metadata_internal"][i][0].decode())
            metadata["postprocessing_time"] = postprocessing_time
            result.append({"image": image, "metadata": metadata})

        return result


class EnsembleModel(SeqEnsembleModel):
    model_name = model_name
    models = [Model, PostProcessor]
    inputs = [
        TextSignature(shape=(1,), dtype=np.object_, name="pos_prompt", external=True),
        TensorSignature(shape=(1,), dtype=np.uint32, name="seed", external=True),
    ]
    outputs = [
        ImageSignature(shape=(1,), dtype=np.bytes_, name="image", external=True),
        TextSignature(shape=(1,), dtype=np.bytes_, name="metadata", external=True),
    ]
    model_config = ModelConfig(max_batch_size=max_batch_size)
