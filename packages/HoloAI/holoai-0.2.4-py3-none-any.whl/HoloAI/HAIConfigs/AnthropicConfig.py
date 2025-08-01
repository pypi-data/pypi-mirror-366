import os
import threading
from dotenv import load_dotenv
import anthropic

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class AnthropicConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("ANTHROPIC_API_KEY")
        if not apiKey:
            raise KeyError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment variables.")
        self.client = anthropic.Anthropic(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("ANTHROPIC_TEXT_MODEL", "claude-sonnet-4-20250514")
        self.VModel = os.getenv("ANTHROPIC_VISION_MODEL", "claude-opus-4-20250514")

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')  # can be str, list of str, or structured
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens')  # BaseConfig defaults the value to: 369
        verbose = kwargs.get('verbose', False)
        if not model:
            raise ValueError("Model cannot be None or empty.")
        if not user:
            raise ValueError("User input cannot be None or empty.")

        # --- system / instructions ---
        devMessage = self.dev
        if not system:
            systemPrompt = devMessage
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                systemPrompt = devMessage + "\n" + systemContents
            else:
                systemPrompt = devMessage + "\n" + str(system)

        # --- user memories / latest ---
        messages = parseJsonInput(user)

        args = {
            "model": model,
            "system": systemPrompt,
            "messages": messages,
            "max_tokens": tokens,
        }
        if tools:
            args["tools"] = tools

        response = self.client.messages.create(**args)
        return response if verbose else response.content[0].text

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------
    def Vision(self, **kwargs):
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')  # can be str, list of str, or structured
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens')  # tokens not directly used but kept for consistency
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 5)
        verbose = kwargs.get('verbose', False)
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        devMessage = self.dev
        # Compose system prompt
        if not system:
            systemPrompt = devMessage
        else:
            systemPrompt = f"{devMessage}\n{system}"

        images = []
        for path in paths:
            frames = getFrames(path, collect)
            for b64, mimeType, idx in frames:
                images.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{mimeType}",
                        "data": b64
                    }
                })

        user_content = images.copy()
        if user:
            user_content.append({
                "type": "text",
                "text": user
            })
        messages = [{
            "role": "user",
            "content": user_content
        }]

        args = {
            "model": model,
            "system": systemPrompt,
            "messages": messages,
            "max_tokens": 1024,
        }
        if tools:
            args["tools"] = tools

        response = self.client.messages.create(**args)
        return response if verbose else response.content[0].text
