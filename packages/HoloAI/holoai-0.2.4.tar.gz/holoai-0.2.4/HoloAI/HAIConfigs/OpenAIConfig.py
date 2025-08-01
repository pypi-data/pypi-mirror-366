import os
import threading
from dotenv import load_dotenv
from openai import OpenAI

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class OpenAIConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("OPENAI_API_KEY")
        if not apiKey:
            raise KeyError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
        self.client = OpenAI(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("OPENAI_RESPONSE_MODEL", "gpt-4.1")
        self.VModel = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")

    # ---------------------------------------------------------
    # Response generation
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')  # can be str, list of str, or structured
        skills  = kwargs.get('skills', None)
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens')  # tokens not directly used but kept for consistency
        verbose = kwargs.get('verbose', False)
        if not model:
            raise ValueError("Model cannot be None or empty.")
        if not user:
            raise ValueError("User input cannot be None or empty.")

        # Build local dev message without mutating self.dev
        devMessage = self.dev
        messages = []

        # --- system / instructions ---
        if not system:
            messages.append(formatJsonInput("system", devMessage))
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                messages.append(self.formatJsonInput("system", devMessage + "\n" + systemContents))
            else:
                messages.append(formatJsonInput("system", devMessage + "\n" + system))

        # --- user memories / latest ---
        messages.extend(parseJsonInput(user))
        # debug
        #print(f"Messages: {messages}")
        # --- streamlined response creation ---
        args = {
            "model": model,
            "input": messages,
        }
        if tools:
            args["tools"] = tools

        response = self.client.responses.create(**args)
        return response if verbose else response.output_text

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------
    def Vision(self, **kwargs):
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')  # can be str, list of str, or structured
        skills  = kwargs.get('skills', None)
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens')  # tokens not directly used but kept for consistency
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 5)
        verbose = kwargs.get('verbose', False)
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        # 1) Build the dev+system block exactly like in Response()
        devMessage = self.dev
        contents = []
        if not system:
            # no extra system text → just devMessage
            contents.append(formatJsonInput("system", devMessage))
        else:
            # merge devMessage + your system instructions
            merged = f"{devMessage}\n{system}"
            sys_out = formatJsonInput("system", merged)
            if isinstance(sys_out, list):
                contents.extend(sys_out)
            else:
                contents.append(sys_out)

        # 2) Build proper image payload
        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({
                "type": "input_image",
                "image_url": f"data:image/{mimeType};base64,{b64}"
            })

        # 3) Attach only your single prompt (user) + images
        user_content = [{"type": "input_text", "text": user}] + images
        input_payload = contents.copy()
        input_payload.append({
            "role": "user",
            "content": user_content
        })

        # 4) Fire off the vision API
        response = self.client.responses.create(
            model=model,
            input=input_payload
        )
        return response if verbose else response.output_text
