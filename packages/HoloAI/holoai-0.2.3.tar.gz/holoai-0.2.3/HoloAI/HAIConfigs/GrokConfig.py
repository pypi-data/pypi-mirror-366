import os
from dotenv import load_dotenv
from openai import OpenAI

from HoloAI.HAIUtils.HAIUtils import (
    DEV_MSG,
    parseInstructions,
    isStructured,
    formatJsonInput,
    parseJsonInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GrokConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("XAI_API_KEY")
        if not apiKey:
            raise KeyError("Grok API key not found. Please set XAI_API_KEY in your environment variables.")
        self.client = OpenAI(
            base_url="https://api.grok.x.ai/v1",
            api_key=apiKey
        )

    def _setModels(self):
        self.RModel = os.getenv("GROK_RESPONSE_MODEL", "grok-2-latest")
        self.VModel = os.getenv("GROK_VISION_MODEL", "grok-2-vision-latest")

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

        messages = []
        if not system:
            messages.append(formatJsonInput("system", self.dev))
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                messages.append(formatJsonInput("system", f"{self.dev}\n{systemContents}"))
            else:
                messages.append(formatJsonInput("system", f"{self.dev}\n{system}"))
        messages.extend(parseJsonInput(user))

        args = {
            "model": model,
            "messages": messages,
        }
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

        contents = []
        if system:
            merged = f"{self.dev}\n{system}"
            sys_out = formatJsonInput("system", merged)
            contents.extend(sys_out if isinstance(sys_out, list) else [sys_out])
        else:
            contents.append(formatJsonInput("system", self.dev))

        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{mimeType};base64,{b64}"}
            })

        user_content = [{"type": "text", "text": user}] + images
        input_payload = contents + [{
            "role": "user",
            "content": user_content
        }]

        response = self.client.chat.completions.create(
            model=model,
            messages=input_payload
        )
        return response if verbose else response.choices[0].message.content
