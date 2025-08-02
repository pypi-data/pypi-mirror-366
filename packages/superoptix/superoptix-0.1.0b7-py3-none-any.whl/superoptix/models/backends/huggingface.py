"""
HuggingFace backend implementation for SuperOptiX model management.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime

from ..utils import (
    SuperOptiXModelInfo,
    SuperOptiXBackendInfo,
    SuperOptiXModelStatus,
    SuperOptiXBackendType,
    SuperOptiXModelSize,
    SuperOptiXModelTask,
)
from .base import SuperOptiXBaseBackend


class SuperOptiXHuggingFaceBackend(SuperOptiXBaseBackend):
    """SuperOptiX HuggingFace backend for model management."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Extract cache_dir from kwargs or config
        cache_dir = kwargs.get("cache_dir", "~/.cache/huggingface")
        if isinstance(cache_dir, str):
            self.cache_dir = Path(cache_dir).expanduser()
        else:
            self.cache_dir = Path("~/.cache/huggingface").expanduser()

    @property
    def backend_type(self) -> SuperOptiXBackendType:
        return SuperOptiXBackendType.HUGGINGFACE

    async def is_available(self) -> bool:
        """Check if HuggingFace transformers is available."""
        try:
            import transformers  # noqa: F401
            import torch  # noqa: F401

            return True
        except ImportError:
            return False

    async def get_backend_info(self) -> SuperOptiXBackendInfo:
        """Get HuggingFace backend information."""
        try:
            if not await self.is_available():
                return SuperOptiXBackendInfo(
                    type=self.backend_type,
                    available=False,
                    error="HuggingFace transformers and torch not installed",
                    config=self.config,
                )

            import transformers
            import torch

            # Count installed models (placeholder)
            installed_models = await self.list_installed_models()

            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=True,
                version=f"transformers {transformers.__version__}, torch {torch.__version__}",
                status="available",
                models_count=len(installed_models),
                config=self.config,
            )
        except Exception as e:
            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=False,
                error=str(e),
                config=self.config,
            )

    def get_backend_info_sync(self) -> SuperOptiXBackendInfo:
        """Synchronous wrapper for get_backend_info."""
        return asyncio.run(self.get_backend_info())

    async def list_available_models(self) -> List[SuperOptiXModelInfo]:
        """List all available HuggingFace models."""
        # For now, return a curated list of popular models
        # In a full implementation, this could query the HF Hub API

        popular_models = [
            (
                "microsoft/DialoGPT-medium",
                "345M",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CHAT,
                "Conversational AI model",
            ),
            (
                "microsoft/DialoGPT-large",
                "762M",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CHAT,
                "Large conversational AI model",
            ),
            (
                "google/flan-t5-small",
                "80M",
                SuperOptiXModelSize.TINY,
                SuperOptiXModelTask.REASONING,
                "Small instruction-following model",
            ),
            (
                "google/flan-t5-base",
                "250M",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.REASONING,
                "Base instruction-following model",
            ),
            (
                "google/flan-t5-large",
                "780M",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.REASONING,
                "Large instruction-following model",
            ),
            (
                "sentence-transformers/all-MiniLM-L6-v2",
                "23M",
                SuperOptiXModelSize.TINY,
                SuperOptiXModelTask.EMBEDDING,
                "Sentence embedding model",
            ),
            (
                "sentence-transformers/all-mpnet-base-v2",
                "110M",
                SuperOptiXModelSize.TINY,
                SuperOptiXModelTask.EMBEDDING,
                "High-quality sentence embeddings",
            ),
            (
                "microsoft/DialoGPT-small",
                "117M",
                SuperOptiXModelSize.TINY,
                SuperOptiXModelTask.CHAT,
                "Small conversational AI model",
            ),
            (
                "facebook/opt-125m",
                "125M",
                SuperOptiXModelSize.TINY,
                SuperOptiXModelTask.CHAT,
                "Small OPT model for text generation",
            ),
            (
                "facebook/opt-350m",
                "350M",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CHAT,
                "Medium OPT model for text generation",
            ),
        ]

        models = []

        for name, params, size, task, desc in popular_models:
            models.append(
                SuperOptiXModelInfo(
                    name=name,
                    backend=self.backend_type,
                    status=SuperOptiXModelStatus.INSTALLED,
                    size=size,
                    task=task,
                    description=desc,
                    parameters=params,
                    tags=["popular", "huggingface", task.value],
                )
            )

        return models

    async def list_installed_models(self) -> List[SuperOptiXModelInfo]:
        """List installed HuggingFace models."""
        try:
            models = []

            # Scan the cache directory for downloaded models
            if self.cache_dir.exists():
                for item in self.cache_dir.iterdir():
                    if item.is_dir():
                        # Convert directory name back to model name
                        model_name = item.name.replace("_", "/")

                        # Check if it's a valid model directory
                        if (item / "config.json").exists() or (
                            item / "pytorch_model.bin"
                        ).exists():
                            # Infer model characteristics
                            size = self._infer_model_size(model_name)
                            task = self._infer_model_task(model_name)
                            parameters = self._extract_parameters(model_name)

                            # Calculate disk size
                            disk_size = sum(
                                f.stat().st_size for f in item.rglob("*") if f.is_file()
                            )

                            models.append(
                                SuperOptiXModelInfo(
                                    name=model_name,
                                    backend=self.backend_type,
                                    status=SuperOptiXModelStatus.INSTALLED,
                                    size=size,
                                    task=task,
                                    description=f"HuggingFace model: {model_name}",
                                    parameters=parameters,
                                    disk_size=disk_size,
                                    local_path=item,
                                    tags=[
                                        "huggingface",
                                        "installed",
                                        task.value if task else "general",
                                    ],
                                )
                            )

            return models

        except Exception as e:
            # Log error but don't fail
            import logging

            logging.getLogger(__name__).warning(
                f"Error listing installed HuggingFace models: {e}"
            )
            return []

    def list_installed_models_sync(self):
        return asyncio.run(self.list_installed_models())

    async def install_model(
        self, model_name: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Install a HuggingFace model."""
        try:
            if not await self.is_available():
                from rich.console import Console
                from rich.panel import Panel
                from rich.text import Text
                from rich.columns import Columns

                console = Console()

                # Create colorful error message
                error_text = Text(
                    "❌ HuggingFace is not available on this system", style="bold red"
                )

                # Requirements section
                requirements = Text()
                requirements.append("🔧 HuggingFace requires:\n", style="bold yellow")
                requirements.append("  • Python 3.8+\n", style="cyan")
                requirements.append(
                    "  • The 'transformers' and 'torch' packages installed\n",
                    style="cyan",
                )
                requirements.append(
                    "  • Sufficient RAM for model loading\n", style="cyan"
                )
                requirements.append(
                    "  • Optional: GPU support for better performance\n", style="cyan"
                )

                # Installation instructions
                install_text = Text()
                install_text.append(
                    "🚀 To install HuggingFace, run:\n", style="bold green"
                )
                install_text.append(
                    "  pip install transformers torch accelerate\n",
                    style="bright_white",
                )
                install_text.append("  or (with uv):\n", style="bright_white")
                install_text.append(
                    "  uv pip install transformers torch accelerate\n",
                    style="bright_white",
                )
                install_text.append("  or (with conda):\n", style="bright_white")
                install_text.append(
                    "  conda install -c pytorch transformers\n", style="bright_white"
                )

                # Optional GPU support
                gpu_text = Text()
                gpu_text.append(
                    "🎮 For GPU support (optional):\n", style="bold magenta"
                )
                gpu_text.append(
                    "  pip install torch torchvision torchaudio\n", style="bright_white"
                )
                gpu_text.append(
                    "  --index-url https://download.pytorch.org/whl/cu118\n",
                    style="bright_white",
                )

                # Next steps
                next_steps = Text()
                next_steps.append(
                    "📚 See https://huggingface.co/docs/transformers/ for more details\n",
                    style="blue",
                )
                next_steps.append(
                    "💡 After installation, try: super model install huggingface <model_name>\n",
                    style="bright_green",
                )

                # Create panels
                error_panel = Panel(
                    error_text,
                    border_style="red",
                    title="🤗 HuggingFace Setup Required",
                )
                req_panel = Panel(
                    requirements, border_style="yellow", title="📋 Requirements"
                )
                install_panel = Panel(
                    install_text, border_style="green", title="⚡ Installation"
                )
                gpu_panel = Panel(
                    gpu_text, border_style="magenta", title="🎮 GPU Support"
                )
                next_panel = Panel(
                    next_steps, border_style="blue", title="🎯 Next Steps"
                )

                # Display in columns for better layout
                console.print()
                console.print(error_panel)
                console.print()
                console.print(Columns([req_panel, install_panel]))
                console.print()
                console.print(Columns([gpu_panel, next_panel]))
                console.print()

                return

            yield f"Starting download of {model_name} from HuggingFace..."

            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM  # noqa: F401
                from huggingface_hub import snapshot_download
                import os  # noqa: F401

                yield f"🔍 Checking model availability: {model_name}"

                # Create model directory in cache
                model_dir = self.cache_dir / model_name.replace("/", "_")
                model_dir.mkdir(parents=True, exist_ok=True)

                yield f"📁 Downloading to: {model_dir}"

                # Enhanced progress tracking for large model downloads
                yield f"🔍 Analyzing model repository: {model_name}"
                
                try:
                    # Get repository info for better progress tracking
                    from huggingface_hub import list_repo_files
                    files = list_repo_files(repo_id=model_name)
                    total_files = len(files)
                    yield f"📦 Found {total_files} files to download"
                    
                except Exception as e:
                    yield f"⚠️ Could not analyze repository: {e}"
                    yield "📥 Proceeding with download..."
                    files = []
                    total_files = 0

                # Download model files using huggingface_hub with enhanced progress
                yield f"⏳ Starting download... (this may take a while for large models)"
                yield f"💡 For large models like this, the download may appear stuck but is actually progressing"
                yield f"🔍 You can check the download directory: {model_dir}"
                
                try:
                    # Use snapshot_download with better error handling
                    snapshot_download(
                        repo_id=model_name,
                        local_dir=str(model_dir),
                        local_dir_use_symlinks=False,
                        resume_download=True,
                    )
                    
                    # Verify download completed successfully
                    if not model_dir.exists():
                        yield f"❌ Download failed: model directory not created"
                        return
                    
                    # Check for essential model files
                    model_files = list(model_dir.rglob("*.bin")) + list(model_dir.rglob("*.safetensors"))
                    config_files = list(model_dir.rglob("*.json"))
                    
                    if not model_files and not any(f.name in ["config.json", "tokenizer.json", "tokenizer_config.json"] for f in config_files):
                        yield f"❌ Download failed: no model files found in {model_dir}"
                        return
                    
                    # Calculate total size for user feedback
                    total_size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    
                    yield f"✅ Successfully downloaded {model_name}"
                    yield f"📊 Model size: {size_mb:.1f} MB"
                    yield f"📁 Location: {model_dir}"
                    yield f"📁 Found {len(model_files)} model files and {len(config_files)} config files"
                    yield "💡 You can now use it with SuperOptiX:"
                    yield f"   super model dspy huggingface/{model_name}"
                    
                except Exception as e:
                    yield f"❌ Download failed: {e}"
                    return

            except ImportError as e:
                yield f"❌ Missing required packages: {e}"
                yield "💡 Install with: pip install transformers huggingface_hub torch"
                return
            except Exception as e:
                yield f"❌ Failed to download {model_name}: {e}"
                return

        except Exception as e:
            yield f"❌ Failed to install {model_name}: {e}"

    def install_model_sync(self, model_name: str, **kwargs) -> bool:
        """Synchronous wrapper for install_model (prints progress, returns True if successful)."""
        import asyncio
        import os
        from pathlib import Path

        try:
            # Create a new event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async install_model in the event loop
            async def run_install():
                gen = self.install_model(model_name, **kwargs)
                last_message = None
                async for message in gen:
                    from rich.console import Console
                    Console().print(message)
                    last_message = message
                
                # Verify the model was actually downloaded
                model_dir = self.cache_dir / model_name.replace("/", "_")
                if not model_dir.exists():
                    return False
                
                # Check for essential model files
                required_files = ["config.json", "tokenizer.json", "tokenizer_config.json"]
                model_files = [f for f in model_dir.rglob("*.bin")] + [f for f in model_dir.rglob("*.safetensors")]
                config_files = [f for f in model_dir.rglob("*.json")]
                
                if not model_files and not any(f.name in required_files for f in config_files):
                    return False
                
                return last_message is None or "❌" not in str(last_message)
            
            return loop.run_until_complete(run_install())
            
        except Exception as e:
            from rich.console import Console
            Console().print(f"Failed to install model {model_name}: {e}")
            return False

    async def uninstall_model(self, model_name: str) -> bool:
        """Uninstall a HuggingFace model."""
        try:
            import shutil
            from pathlib import Path
            
            # Convert model name to directory name
            model_dir_name = model_name.replace("/", "_")
            model_dir = self.cache_dir / model_dir_name
            
            # Also check the HuggingFace cache directory
            hf_cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{model_name.replace('/', '--')}"
            
            removed = False
            
            # Remove from SuperOptiX cache
            if model_dir.exists():
                shutil.rmtree(model_dir)
                removed = True
            
            # Remove from HuggingFace cache
            if hf_cache_dir.exists():
                shutil.rmtree(hf_cache_dir)
                removed = True
            
            return removed
        except Exception as e:
            print(f"Error uninstalling {model_name}: {e}")
            return False

    def uninstall_model_sync(self, model_name: str) -> bool:
        """Synchronous wrapper for uninstall_model."""
        try:
            import asyncio
            return asyncio.run(self.uninstall_model(model_name))
        except Exception as e:
            print(f"Error in sync uninstall {model_name}: {e}")
            return False

    def get_model_info_sync(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific model (sync version)."""
        try:
            import asyncio
            return asyncio.run(self.get_model_info(model_name))
        except Exception as e:
            print(f"Error getting model info for {model_name}: {e}")
            return None

    async def get_model_info(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific model."""
        # First check installed models
        installed_models = await self.list_installed_models()
        for model in installed_models:
            if model.name == model_name:
                return model

        # Then check available models
        available_models = await self.list_available_models()
        for model in available_models:
            if model.name == model_name:
                return model
        return None

    def get_model_info_sync(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Synchronous wrapper for get_model_info."""
        return asyncio.run(self.get_model_info(model_name))

    async def start_model(self, model_name: str, **kwargs) -> bool:
        """Start/load a model."""
        # Placeholder implementation
        return False

    async def stop_model(self, model_name: str) -> bool:
        """Stop/unload a model."""
        # Placeholder implementation
        return True

    async def test_model(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Test a HuggingFace model with a simple prompt."""
        try:
            # Check if model is available locally
            model_path = self.cache_dir / model_name.replace("/", "_")
            if not model_path.exists():
                return {
                    "success": False,
                    "error": f"Model {model_name} not found locally",
                    "model": model_name,
                    "prompt": prompt,
                }

            # Try to use transformers pipeline directly
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
                import torch
                
                start_time = datetime.now()
                
                # Load model and tokenizer
                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                model = AutoModelForCausalLM.from_pretrained(
                    str(model_path),
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
                
                # Create pipeline
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True
                )
                
                # Tokenize input to get prompt tokens
                prompt_tokens = len(tokenizer.encode(prompt))
                
                # Generate response
                result = pipe(prompt, max_new_tokens=100, return_full_text=False)
                response = result[0]['generated_text']
                
                # Calculate response tokens
                full_tokens = len(tokenizer.encode(result[0]['generated_text']))
                response_tokens = full_tokens - prompt_tokens
                
                end_time = datetime.now()
                
                return {
                    "success": True,
                    "model": model_name,
                    "prompt": prompt,
                    "response": response,
                    "response_time": (end_time - start_time).total_seconds(),
                    "prompt_tokens": prompt_tokens,
                    "tokens": response_tokens,
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"HuggingFace model testing failed: {str(e)}",
                    "model": model_name,
                    "prompt": prompt,
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"HuggingFace model testing error: {str(e)}",
                "model": model_name,
                "prompt": prompt,
            }

    def test_model_sync(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Synchronous wrapper for test_model."""
        import asyncio
        return asyncio.run(self.test_model(model_name, prompt))

    async def create_dspy_client(self, model_name: str, **kwargs):
        """Create a DSPy-compatible client for HuggingFace using LiteLLM custom_openai."""
        try:
            import dspy

            # Get configuration from kwargs
            api_base = kwargs.get("api_base", "http://localhost:8001")
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2048)
            api_key = kwargs.get(
                "api_key", "dummy_key"
            )  # HuggingFace servers typically don't need real API keys

            # Create DSPy LM with custom_openai provider
            # This assumes you have a HuggingFace server running with OpenAI-compatible API
            lm = dspy.LM(
                model=f"custom_openai/{model_name}",
                api_base=api_base,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=2,
                timeout=30,
            )

            return lm

        except ImportError as e:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text

            console = Console()

            # Create colorful error message
            error_text = Text(
                "❌ Missing required packages for HuggingFace DSPy integration",
                style="bold red",
            )

            # Installation instructions
            install_text = Text()
            install_text.append(
                "🚀 To install required packages, run:\n", style="bold green"
            )
            install_text.append("  pip install dspy-ai litellm\n", style="bright_white")
            install_text.append("  or (with uv):\n", style="bright_white")
            install_text.append(
                "  uv pip install dspy-ai litellm\n", style="bright_white"
            )
            install_text.append("  or (with conda):\n", style="bright_white")
            install_text.append(
                "  conda install -c conda-forge dspy-ai litellm\n", style="bright_white"
            )

            # Create panels
            error_panel = Panel(
                error_text, border_style="red", title="🤗 Package Installation Required"
            )
            install_panel = Panel(
                install_text, border_style="green", title="⚡ Installation"
            )

            # Display panels
            console.print()
            console.print(error_panel)
            console.print()
            console.print(install_panel)
            console.print()

            raise RuntimeError(
                f"Failed to import required libraries for HuggingFace DSPy integration: {e}\n"
                "Please ensure dspy-ai and litellm are installed:\n"
                "  pip install dspy-ai litellm\n"
                "  or\n"
                "  uv pip install dspy-ai litellm"
            )
        except Exception as e:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text

            console = Console()

            # Create colorful error message
            error_text = Text(
                f"❌ Failed to create HuggingFace DSPy client for {model_name}",
                style="bold red",
            )

            # Server setup instructions
            server_text = Text()
            server_text.append(
                "🚀 Make sure you have a HuggingFace server running:\n",
                style="bold green",
            )
            server_text.append(
                f"   super model server huggingface {model_name}\n",
                style="bright_white",
            )
            server_text.append("   or\n", style="bright_white")
            server_text.append(
                f"   python -m superoptix.models.backends.huggingface_server {model_name} --port 8001\n",
                style="bright_white",
            )

            # Playbook configuration
            config_text = Text()
            config_text.append(
                "📋 Example playbook configuration:\n", style="bold blue"
            )
            config_text.append("   language_model:\n", style="bright_white")
            config_text.append("     provider: huggingface\n", style="bright_white")
            config_text.append(f"     model: {model_name}\n", style="bright_white")
            config_text.append(
                "     api_base: http://localhost:8001\n", style="bright_white"
            )
            config_text.append("     temperature: 0.7\n", style="bright_white")
            config_text.append("     max_tokens: 256\n", style="bright_white")

            # Create panels
            error_panel = Panel(
                error_text, border_style="red", title="🤗 HuggingFace Server Setup"
            )
            server_panel = Panel(
                server_text, border_style="green", title="⚡ Server Startup"
            )
            config_panel = Panel(
                config_text, border_style="blue", title="📋 Configuration"
            )

            # Display panels
            console.print()
            console.print(error_panel)
            console.print()
            console.print(server_panel)
            console.print()
            console.print(config_panel)
            console.print()

            raise RuntimeError(
                f"Failed to create HuggingFace DSPy client: {e}\n\n"
                "💡 Make sure you have a HuggingFace server running:\n"
                "   super model server huggingface {model_name}\n\n"
                "📋 Example playbook configuration:\n"
                f"   language_model:\n"
                f"     provider: huggingface\n"
                f"     model: {model_name}\n"
                f"     api_base: http://localhost:8001"
            )

    def create_dspy_client_sync(self, model_name: str, **kwargs):
        """Synchronous wrapper for create_dspy_client."""
        return asyncio.run(self.create_dspy_client(model_name, **kwargs))

    def _infer_model_size(self, model_name: str) -> Optional[SuperOptiXModelSize]:
        """Infer model size from model name."""
        name_lower = model_name.lower()

        if any(size in name_lower for size in ["1b", "1.5b", "2b", "3b"]):
            return SuperOptiXModelSize.SMALL
        elif any(size in name_lower for size in ["7b", "8b", "13b", "14b"]):
            return SuperOptiXModelSize.MEDIUM
        elif any(size in name_lower for size in ["30b", "40b", "70b", "100b"]):
            return SuperOptiXModelSize.LARGE
        else:
            return SuperOptiXModelSize.SMALL  # Default

    def _infer_model_task(self, model_name: str) -> Optional[SuperOptiXModelTask]:
        """Infer model task from model name."""
        name_lower = model_name.lower()

        if any(code in name_lower for code in ["code", "coder", "programming"]):
            return SuperOptiXModelTask.CODE
        elif any(reason in name_lower for reason in ["reason", "logic", "math"]):
            return SuperOptiXModelTask.REASONING
        elif any(embed in name_lower for embed in ["embed", "sentence"]):
            return SuperOptiXModelTask.EMBEDDING
        else:
            return SuperOptiXModelTask.CHAT  # Default

    def _extract_parameters(self, model_name: str) -> Optional[str]:
        """Extract parameter count from model name."""
        import re

        # Look for patterns like "7B", "13B", "70B", etc.
        match = re.search(r"(\d+(?:\.\d+)?)[Bb]", model_name)
        if match:
            return f"{match.group(1)}B"

        return None
