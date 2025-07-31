"""
Configuration file for ROS Chatbot CLI
"""

import os
from typing import Optional
from typing import List
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import platform
import shutil

from rich.console import Console
console = Console()


# Load .env file from multiple locations
possible_paths = [
    Path(__file__).parent.parent / ".env",  # Project root
    Path(__file__).parent / ".env",         # cli directory  
    Path.cwd() / ".env"                     # Current directory
]

for env_path in possible_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break
else:
    # Try auto-discovery
    from dotenv import find_dotenv
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file, override=True)
        print(f"Auto-discovered .env at: {env_file}")

# API Keys - get them after all loading attempts
AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")

# Default configurations
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OLLAMA_MODEL = "qwen3:1.7b"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_ROS_VERSION = "both"
SUPPORTED_ROS_VERSIONS = ["ros1", "ros2", "both"]

# Available models
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant", 
    "gemma2-9b-it"
]

OLLAMA_MODELS = [
    "qwen3:1.7b",
]

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4-turbo", 
    "gpt-3.5-turbo",
    "gpt-4.1",
    "gpt-4o-mini"
]

# Azure OpenAI Configuration (preferred)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Available Azure OpenAI models (deployment names in Azure)
AZURE_OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4",
    "gpt-4-turbo", 
    "gpt-35-turbo",
    "gpt-4o",
    "gpt-4o-mini"
]

# Add retrieval API base URL configuration
RETRIEVAL_API_BASE_URL = os.getenv("RETRIEVAL_API_BASE_URL", "http://localhost:8000")

# Helper functions
def get_available_backends() -> List[str]:
    """Get list of available backends"""
    if OPENAI_API_KEY:
        available = "openai"
    elif AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
        available = "azure"
    else:
        available = "ollama"

    return available

def get_best_available_backend() -> str:
    """Get the best available backend in order of preference"""
    # Prefer Azure OpenAI, then OpenAI, then Ollama
    if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
        return "azure"
    elif OPENAI_API_KEY:
        return "openai"
    else:
        # Check Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return "ollama"
        except:
            pass
    
    return "azure"  # Default fallback


#TODO: find a method to select the appropriate model from the API key 
def get_default_model_for_backend(backend: str) -> str:
    """Get default model for a backend"""
    if backend == "azure":
        return AZURE_OPENAI_MODELS[0]
    elif backend == "openai":
        return OPENAI_MODELS[0]
    elif backend == "ollama":
        return OLLAMA_MODELS[0]
    else:
        return AZURE_OPENAI_MODELS[0]

def check_backend_availability(backend: str) -> tuple[bool, str]:
    """Check if a specific backend is available"""
    backend = backend.lower()
    
    if backend == "azure" or backend == "openai":
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
            return True, "Azure OpenAI API available"
        elif OPENAI_API_KEY:
            return True, "OpenAI API available"
        else:
            return False, "Neither AZURE_OPENAI_API_KEY nor OPENAI_API_KEY set"
    
    elif backend == "ollama":
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return True, "Ollama service running"
            else:
                return False, "Ollama service not responding"
        except:
            return False, "Ollama service not running"
    else:
        return False, f"Unknown backend: {backend}"

def validate_config():
    """Validate configuration"""
    errors = []
    warnings = []
    
    if not AZURE_OPENAI_API_KEY and not OPENAI_API_KEY:
        warnings.append("No API keys found. Set AZURE_OPENAI_API_KEY or OPENAI_API_KEY or use Ollama.")
    
    if DEFAULT_TEMPERATURE < 0 or DEFAULT_TEMPERATURE > 1:
        errors.append("DEFAULT_TEMPERATURE must be between 0 and 1")
    
    return {"errors": errors, "warnings": warnings}


def get_ubuntu_version():
    try:
        version = platform.linux_distribution()[1]
    except AttributeError:
        import distro
        version = distro.version()
    return version

def ROS_Distro():
    ros_distro = os.environ.get("ROS_DISTRO")
    if ros_distro:
        return ros_distro
    else:
        return "ROS distro not found (make sure ROS environment is sourced)"



def is_ros_installed(ros_version):
        if ros_version == "ros1":
            return shutil.which("roscore") is not None
        elif ros_version == "ros2":
            return shutil.which("ros2") is not None
        elif ros_version == "both":
            return shutil.which("roscore") is not None and shutil.which("ros2") is not None
        return False
