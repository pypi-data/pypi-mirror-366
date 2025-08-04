import os
import threading
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    getFrames,
    supportsReasoning,
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GoogleConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("GOOGLE_API_KEY")
        if not apiKey:
            raise KeyError("Google API key not found. Please set GOOGLE_API_KEY in your environment variables.")
        self.client = genai.Client(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("GOOGLE_RESPONSE_MODEL", "gemini-2.5-flash")
        self.VModel = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")

    # ---------------------------------------------------------
    # Response
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
        
        messages = parseTypedInput(user)

        configArgs = {
            "response_mime_type": "text/plain",
            "system_instruction": [system],
            "max_output_tokens": tokens,
        }
        if tools:
            configArgs["tools"] = tools

        # --- Only add reasoning config if the model supports it ---
        if supportsReasoning(model):
            if effort == "auto":
                budget = -1  # Auto budget
            configArgs["thinking_config"] = types.ThinkingConfig(thinking_budget=budget)

        generateConfig = types.GenerateContentConfig(**configArgs)

        args = self._getArgs(model, messages, generateConfig)

        response = self.client.models.generate_content(**args)
        return response if verbose else response.text

    # -----------------------------------------------------------------
    # Vision
    # -----------------------------------------------------------------
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

        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, _ = frames[0]
            images.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type=f"image/{mimeType}",
                        data=base64.b64decode(b64)
                    )
                )
            )

        textPart = types.Part(text=user)
        messages = [ types.Content(role="user", parts=images + [textPart]) ]

        configArgs = {
            "response_mime_type": "text/plain",
            "system_instruction": [system],
            "max_output_tokens": tokens,
        }

        generateConfig = types.GenerateContentConfig(**configArgs)

        args = self._getArgs(model, messages, generateConfig)

        response = self.client.models.generate_content(**args)
        return response if verbose else response.text

    def _getArgs(self, model, messages, config):
        args = {
            "model": model,
            "contents": messages,
            "config": config
        }
        return args
