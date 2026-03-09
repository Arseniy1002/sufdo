#!/usr/bin/env python3
"""
sufdo/ai.py - AI integration for error analysis (Optimized)

Provides AI model configuration and query functionality for error analysis.
API keys are encrypted using base64 + salt hashing.
"""

import json
import hashlib
import base64
import urllib.request
import urllib.error
from typing import Dict, List, Optional

from .utils import ensure_config_dir, Colors, AI_CONFIG_FILE

# Salt for key encryption (in production, use environment variable)
_KEY_SALT = "sufdo_ai_key_salt_v1"

# In-memory cache for AI config
_ai_config_cache: Optional[Dict] = None

# Default models - frozen for safety
_DEFAULT_AI_MODELS: tuple = (
    {
        "name": "gpt-4o",
        "alias": "gpt",
        "api_key": "",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "provider": "openai"
    },
    {
        "name": "gemini-2.0-flash",
        "alias": "gemini",
        "api_key": "",
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "provider": "google"
    },
    {
        "name": "meta-llama/llama-3.3-70b-instruct",
        "alias": "openrouter",
        "api_key": "",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "provider": "openrouter"
    },
    {
        "name": "deepseek-chat",
        "alias": "deepseek",
        "api_key": "",
        "api_url": "https://api.deepseek.com/chat/completions",
        "provider": "deepseek"
    },
)

__all__ = [
    'get_default_ai_models', 'load_ai_config', 'save_ai_config',
    'query_ai', 'analyze_command_error', 'encrypt_key', 'decrypt_key'
]


def encrypt_key(api_key: str) -> str:
    """
    Encrypt API key using base64 + salt hash.
    
    Args:
        api_key: Plain text API key.
    
    Returns:
        Encrypted key string.
    """
    if not api_key:
        return ""
    # Add salt and encode
    salted = _KEY_SALT + api_key + _KEY_SALT[::-1]
    encoded = base64.b64encode(salted.encode()).decode()
    # Add checksum for validation
    checksum = hashlib.md5(api_key.encode()).hexdigest()[:8]
    return f"{checksum}:{encoded}"


def decrypt_key(encrypted_key: str) -> str:
    """
    Decrypt API key.
    
    Args:
        encrypted_key: Encrypted key string.
    
    Returns:
        Plain text API key or empty string on error.
    """
    if not encrypted_key or ':' not in encrypted_key:
        return ""
    try:
        checksum, encoded = encrypted_key.split(':', 1)
        decoded = base64.b64decode(encoded.encode()).decode()
        # Remove salt
        api_key = decoded[len(_KEY_SALT):-len(_KEY_SALT[::-1])]
        # Verify checksum
        if hashlib.md5(api_key.encode()).hexdigest()[:8] != checksum:
            return ""
        return api_key
    except:
        return ""


def get_default_ai_models() -> List[Dict]:
    """
    Get default AI model presets.
    
    Returns:
        List of default AI model configurations.
    """
    return list(_DEFAULT_AI_MODELS)


def load_ai_config() -> Dict:
    """
    Load AI models configuration from file (cached).
    
    Returns:
        AI configuration dictionary with models and default settings.
    """
    global _ai_config_cache
    if _ai_config_cache is not None:
        return _ai_config_cache
    
    if not AI_CONFIG_FILE.exists():
        _ai_config_cache = {"models": {}, "default": None}
    else:
        try:
            with open(AI_CONFIG_FILE, encoding="utf-8") as f:
                _ai_config_cache = json.load(f)
        except:
            _ai_config_cache = {"models": {}, "default": None}
    return _ai_config_cache


def save_ai_config(config: Dict) -> None:
    """
    Save AI models configuration to file.
    
    Args:
        config: AI configuration dictionary to save.
    """
    global _ai_config_cache
    _ai_config_cache = config
    ensure_config_dir()
    with open(AI_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def query_ai(model_config: Dict, prompt: str) -> Optional[str]:
    """
    Query AI model with the given prompt.
    
    Args:
        model_config: Model configuration dictionary.
        prompt: Prompt text to send to AI.
    
    Returns:
        AI response text or error message.
    """
    try:
        api_url = model_config.get("api_url", "")
        encrypted_key = model_config.get("api_key", "")
        api_key = decrypt_key(encrypted_key)
        provider = model_config.get("provider", "openai")
        model_name = model_config.get("name", "")

        if not api_key:
            return f"{Colors.RED}[AI] API key not configured for {model_config.get('alias', 'model')}{Colors.RESET}"

        headers = {"Content-Type": "application/json"}

        if provider in ["openai", "openrouter", "deepseek"]:
            headers["Authorization"] = f"Bearer {api_key}"
            if provider == "openrouter":
                headers["HTTP-Referer"] = "https://github.com/Arseniy1002/sufdo"
                headers["X-Title"] = "sufdo"

            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful terminal assistant. Be concise and provide practical solutions."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }

            req = urllib.request.Request(
                api_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            return result.get("choices", [{}])[0].get("message", {}).get("content", "No response")

        elif provider == "google":
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 500, "temperature": 0.7}
            }

            req = urllib.request.Request(
                f"{api_url}?key={api_key}",
                data=json.dumps(data).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
        else:
            return f"{Colors.RED}[AI] Unknown provider: {provider}{Colors.RESET}"

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace') if e.fp else ""
        return f"{Colors.RED}[AI] API error ({e.code}): {error_body[:200]}{Colors.RESET}"
    except urllib.error.URLError as e:
        return f"{Colors.RED}[AI] Network error: {e.reason}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}[AI] Error: {e}{Colors.RESET}"


def analyze_command_error(
    command: str,
    stdout: str,
    stderr: str,
    returncode: int,
    model_alias: str = None
) -> str:
    """
    Analyze a command error using AI.
    
    Args:
        command: Failed command string.
        stdout: Command stdout output.
        stderr: Command stderr output.
        returncode: Command exit code.
        model_alias: Optional model alias to use.
    
    Returns:
        AI analysis text or error message.
    """
    ai_config = load_ai_config()

    if not ai_config.get("models"):
        return f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}"

    model_config = None
    if model_alias and model_alias in ai_config["models"]:
        model_config = ai_config["models"][model_alias]
    elif ai_config.get("default") and ai_config["default"] in ai_config["models"]:
        model_config = ai_config["models"][ai_config["default"]]
    else:
        model_config = list(ai_config["models"].values())[0] if ai_config["models"] else None

    if not model_config:
        return f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}"

    prompt = f"""Analyze this command error and provide a brief solution:

Command: {command}
Exit Code: {returncode}

Stdout:
{stdout[:500] if stdout else "(empty)"}

Stderr:
{stderr[:1000] if stderr else "(empty)"}

Provide:
1. What went wrong (1 sentence)
2. How to fix it (1-2 steps)
3. Alternative command if applicable

Be concise."""

    print(f"{Colors.CYAN}[AI] Analyzing error with {model_config.get('alias', 'AI')}...{Colors.RESET}")
    return query_ai(model_config, prompt)
