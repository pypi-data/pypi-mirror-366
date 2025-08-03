import os
import threading
from dotenv import load_dotenv
from openai import OpenAI

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames,
    supportsReasoning,
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class OpenAIConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("OPENAI_API_KEY")
        if not apiKey:
            raise KeyError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
        self.client = OpenAI(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("OPENAI_RESPONSE_MODEL", "gpt-4.1")
        self.VModel = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")

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

        messages = []

        # --- system / instructions ---
        messages.append(formatJsonInput("system", system))

        # --- user memories / latest ---
        messages.extend(parseJsonInput(user))

        args = self._getArgs(model, messages, tokens)

        if tools:
            args["tools"] = tools

        # -- Only add reasoning config if the model supports it --
        if supportsReasoning(model):
            if effort == "auto":
                effort = "low"
            args["reasoning"] = {"effort": effort}
            if budget:
                args["max_output_tokens"] = budget

        response = self.client.responses.create(**args)
        return response if verbose else response.output_text

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
                "type": "input_image",
                "image_url": f"data:image/{mimeType};base64,{b64}"
            })

        userContent = [{"type": "input_text", "text": user}] + images
        payload = messages.copy()
        payload.append({
            "role": "user",
            "content": userContent
        })

        args = self._getArgs(model, payload, tokens)

        response = self.client.responses.create(**args)
        return response if verbose else response.output_text

    def _getArgs(self, model, messages, tokens):
        args = {
            "model": model,
            "input": messages,
            "max_output_tokens": tokens,
        }
        return args
