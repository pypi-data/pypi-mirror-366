import os
import threading
from dotenv import load_dotenv
from groq import Groq

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GroqConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("GROQ_API_KEY")
        if not apiKey:
            raise KeyError("Groq API key not found. Please set GROQ_API_KEY in your environment variables.")
        self.client = Groq(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("GROQ_RESPONSE_MODEL", "llama-3.3-70b-versatile")
        self.VModel = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    # ---------------------------------------------------------
    # Response generation
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        model   = kwargs.get('model')
        system  = kwargs.get('system')
        user    = kwargs.get('user')  # can be str, list of str, or structured
        skills  = kwargs.get('skills', None)
        tools   = kwargs.get('tools', None)
        verbose = kwargs.get('verbose', False)
        if not model:
            raise ValueError("Model cannot be None or empty.")
        if not user:
            raise ValueError("User input cannot be None or empty.")

        devMessage = self.dev
        messages = []

        # --- system / instructions ---
        if not system:
            messages.append(formatJsonInput("system", devMessage))
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                messages.append(formatJsonInput("system", devMessage + "\n" + systemContents))
            else:
                messages.append(formatJsonInput("system", devMessage + "\n" + system))

        # --- user memories / latest ---
        messages.extend(parseJsonInput(user))

        # Debug
        #print(f"Messages: {messages}")
        # --- streamlined response creation ---
        args = {
            "model": model,
            "messages": messages,
        }
        if tools:
            args["tools"] = tools
            #args["tool_choice"] = toolChoice
            args["tool_choice"] = "auto"  # Always set to auto if tools are provided

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
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 5)
        verbose = kwargs.get('verbose', False)

        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        # 1) Build your system block exactly like in Response()
        devMessage = self.dev
        contents = []
        if system:
            merged = f"{devMessage}\n{system}"
            sys_out = formatJsonInput("system", merged)
            if isinstance(sys_out, list):
                contents.extend(sys_out)
            else:
                contents.append(sys_out)
        else:
            contents.append(formatJsonInput("system", devMessage))

        # 2) Build the image payload (CRITICAL FIX: image_url must be an object with a "url" key)
        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{mimeType};base64,{b64}"}
            })

        # 3) Attach user prompt and images
        user_content = [{"type": "text", "text": user}] + images
        input_payload = contents.copy()
        input_payload.append({
            "role": "user",
            "content": user_content
        })

        # 4) Call Groq
        response = self.client.chat.completions.create(
            model=model,
            messages=input_payload
        )
        return response if verbose else response.choices[0].message.content
