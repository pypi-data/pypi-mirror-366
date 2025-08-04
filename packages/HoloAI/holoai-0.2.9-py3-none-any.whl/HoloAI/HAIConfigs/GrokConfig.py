import os
from dotenv import load_dotenv
from openai import OpenAI

from HoloAI.HAIUtils.HAIUtils import (
    parseInstructions,
    isStructured,
    formatJsonInput,
    parseJsonInput,
    getFrames,
    supportsReasoning,
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GrokConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("XAI_API_KEY")
        if not apiKey:
            raise KeyError("Grok API key not found. Please set XAI_API_KEY in your environment variables.")
        self.client = OpenAI(
            base_url="https://api.x.ai/v1",
            api_key=apiKey
        )

    def _setModels(self):
        self.RModel = os.getenv("GROK_RESPONSE_MODEL", "grok-4")
        self.VModel = os.getenv("GROK_VISION_MODEL", "grok-4")

    # ---------------------------------------------------------
    # Response generation
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')
        skills  = kwargs.get('skills')
        tools   = kwargs.get('tools')
        show    = kwargs.get('show')
        effort  = kwargs.get('effort')
        budget  = kwargs.get('budget')
        tokens  = kwargs.get('tokens')
        verbose = kwargs.get('verbose')

        messages = []

        # --- system / instructions ---
        messages.append(formatJsonInput("system", system))

        # --- user memories / latest ---
        messages.extend(parseJsonInput(user))

        args = self._getArgs(model, messages, tokens)
        if tools:
            args["tools"] = tools
            args["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**args)
        return response if verbose else response.choices[0].message.content

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------
    def Vision(self, **kwargs):
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')
        skills  = kwargs.get('skills')
        tools   = kwargs.get('tools')
        effort  = kwargs.get('effort')
        budget  = kwargs.get('budget')
        tokens  = kwargs.get('tokens')
        paths   = kwargs.get('paths')
        collect = kwargs.get('collect')
        verbose = kwargs.get('verbose')

        messages = []
        messages.append(formatJsonInput("system", system))

        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{mimeType};base64,{b64}"}
            })

        userContent = [{"type": "text", "text": user}] + images
        payload = messages + [{
            "role": "user",
            "content": userContent
        }]

        args = self._getArgs(model, payload, tokens)

        response = self.client.chat.completions.create(**args)
        return response if verbose else response.choices[0].message.content

    def _getArgs(self, model, messages, tokens):
        args = {
            "model": model,
            "messages": messages,
            "max_tokens": tokens,
        }
        return args
