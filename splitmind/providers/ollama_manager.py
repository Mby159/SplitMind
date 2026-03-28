"""
Ollama Manager - Manage local Ollama models with auto-download.
"""

import json
import subprocess
import httpx
from typing import List, Optional, Dict
from pathlib import Path


class OllamaManager:
    """
    Manages Ollama local models.
    
    Features:
    - Auto-detect Ollama installation
    - Check server status
    - List available models
    - Pull models automatically
    - Recommend models based on hardware
    """
    
    DEFAULT_HOST = "http://localhost:11434"
    
    # Recommended small models for different use cases (2025 updated)
    RECOMMENDED_MODELS = {
        "general": {
            "name": "llama3.2:3b",
            "description": "通用对话，Meta最新，3B参数，速度快",
            "size": "2.0GB",
        },
        "general_small": {
            "name": "gemma3:1b",
            "description": "轻量通用，Google出品，仅815MB",
            "size": "815MB",
        },
        "coding": {
            "name": "qwen2.5-coder:1.5b",
            "description": "代码生成，1.5B参数，轻量级",
            "size": "1.1GB",
        },
        "analysis": {
            "name": "olmo2:7b",
            "description": "推理分析，2025年新出，推理能力强",
            "size": "4.5GB",
        },
        "analysis_small": {
            "name": "llama3.2:1b",
            "description": "轻量推理，1B参数，速度快",
            "size": "1.3GB",
        },
        "chinese": {
            "name": "qwen2.5:3b",
            "description": "中文通用，阿里出品，3B参数",
            "size": "1.9GB",
        },
        "english": {
            "name": "llama3.2:1b",
            "description": "英文任务，Meta最新，1B参数",
            "size": "1.3GB",
        },
    }
    
    def __init__(self, host: Optional[str] = None):
        self.host = host or self.DEFAULT_HOST
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def is_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = await self._client.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> List[Dict]:
        """List all installed models."""
        try:
            response = await self._client.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
        except Exception as e:
            print(f"Error listing models: {e}")
        return []
    
    async def has_model(self, model_name: str) -> bool:
        """Check if a specific model is installed."""
        models = await self.list_models()
        return any(m["name"] == model_name or m["name"].startswith(model_name + ":") 
                   for m in models)
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            print(f"Downloading model: {model_name}...")
            print("This may take a few minutes depending on your internet speed.")
            
            response = await self._client.post(
                f"{self.host}/api/pull",
                json={"name": model_name, "stream": False}
            )
            
            if response.status_code == 200:
                print(f"Model {model_name} downloaded successfully!")
                return True
            else:
                print(f"Failed to download model: {response.text}")
                return False
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False
    
    async def ensure_model(self, model_name: str) -> bool:
        """Ensure a model is available, pull if not."""
        if await self.has_model(model_name):
            return True
        
        print(f"Model {model_name} not found locally.")
        return await self.pull_model(model_name)
    
    def get_recommended_model(self, task_type: str = "general") -> str:
        """Get a recommended model for the task type."""
        if task_type in self.RECOMMENDED_MODELS:
            return self.RECOMMENDED_MODELS[task_type]["name"]
        return self.RECOMMENDED_MODELS["general"]["name"]
    
    async def get_system_info(self) -> Dict:
        """Get system information for model recommendations."""
        import psutil
        
        memory = psutil.virtual_memory()
        
        info = {
            "total_memory_gb": memory.total / (1024**3),
            "available_memory_gb": memory.available / (1024**3),
            "cpu_count": psutil.cpu_count(),
        }
        
        # Recommend models based on available memory
        if info["available_memory_gb"] < 4:
            info["recommended"] = "llama3.2:1b or qwen2.5-coder:1.5b"
        elif info["available_memory_gb"] < 8:
            info["recommended"] = "qwen2.5:3b or deepseek-r1:1.5b"
        else:
            info["recommended"] = "qwen2.5:7b or llama3.1:8b"
        
        return info
    
    async def chat(self, model: str, message: str, system: Optional[str] = None) -> str:
        """Simple chat completion with a model."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self._client.post(
                f"{self.host}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()


class LocalModelSetup:
    """
    Helper class for setting up local models.
    """
    
    @staticmethod
    def check_ollama_installed() -> bool:
        """Check if Ollama is installed on the system."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def get_install_instructions() -> str:
        """Get installation instructions for Ollama."""
        return """
Ollama is not installed. Please install it first:

Windows:
    Download from: https://ollama.com/download/windows
    Or use winget: winget install Ollama.Ollama

macOS:
    Download from: https://ollama.com/download/mac
    Or use Homebrew: brew install --cask ollama

Linux:
    curl -fsSL https://ollama.com/install.sh | sh

After installation, start Ollama and run this command again.
"""
    
    @staticmethod
    async def setup_default_model() -> Optional[str]:
        """
        Setup a default model for first-time users.
        Returns the model name if successful.
        """
        if not LocalModelSetup.check_ollama_installed():
            print(LocalModelSetup.get_install_instructions())
            return None
        
        manager = OllamaManager()
        
        if not await manager.is_running():
            print("""
Ollama is installed but not running.
Please start Ollama first:
    - Windows: Start Ollama from the Start menu
    - macOS/Linux: Run 'ollama serve' in terminal
""")
            return None
        
        # Use a small, fast model as default
        default_model = "qwen2.5:3b"
        
        if await manager.ensure_model(default_model):
            await manager.close()
            return default_model
        
        await manager.close()
        return None
