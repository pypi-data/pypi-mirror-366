import os
import threading
from dotenv import load_dotenv
from groq import Groq

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames,
    supportsReasoning,
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig
from pydantic.types import T

load_dotenv()

class GroqConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("GROQ_API_KEY")
        if not apiKey:
            raise KeyError("Groq API key not found. Please set GROQ_API_KEY in your environment variables.")
        self.client = Groq(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("GROQ_RESPONSE_MODEL", "llama-3.3-70b-versatile")
        self.VModel = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

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
            #args["tool_choice"] = toolChoice
            args["tool_choice"] = "auto"  # Always set to auto if tools are provided

        # -- Only add reasoning config if the model supports it --
        if supportsReasoning(model):
            args["reasoning_format"] = show  # "parsed", "raw", or "hidden"
            if model.startswith("qwen/qwen3-32b"):
                args["reasoning_effort"] = "default"
            if effort == "auto":
                budget = 1024
                args["max_completion_tokens"] = budget
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
        images   = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{mimeType};base64,{b64}"}
            })

        userContent = [{"type": "text", "text": user}] + images
        payload = messages.copy()
        payload.append({
            "role": "user",
            "content": userContent
        })

        args = self._getArgs(model, payload, tokens)

        response = self.client.chat.completions.create(**args)
        return response if verbose else response.choices[0].message.content

    def _getArgs(self, model, messages, tokens):
        args = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": tokens,
        }
        return args
