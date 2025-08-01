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
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GoogleConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
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
        user    = kwargs.get('user')  # can be str, list of str, or structured
        skills  = kwargs.get('skills', None)
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens')  # tokens not directly used but kept for consistency
        verbose = kwargs.get('verbose', False)
        if not model:
            raise ValueError("Model cannot be None or empty.")
        if not user:
            raise ValueError("User input cannot be None or empty.")

        devMessage = self.dev

        # --- build system instruction ---
        if not system:
            system_instruction = devMessage
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                system_instruction = f"{devMessage}\n{systemContents}"
            else:
                system_instruction = f"{devMessage}\n{system}"

        # --- build contents list (Google wants Content objects) ---
        contents = parseTypedInput(user)

        # --- build config ---
        config_args = {
            "response_mime_type": "text/plain"
        }
        if system_instruction:
            config_args["system_instruction"] = [system_instruction]
        if tools:
            config_args["tools"] = tools

        generate_content_config = types.GenerateContentConfig(**config_args)

        # --- call Gemini ---
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config
        )
        return response if verbose else response.text

    # -----------------------------------------------------------------
    # Vision
    # -----------------------------------------------------------------
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
        """
        system: Optional system instructions (str or None)
        user: the prompt (str)
        paths: str or list of str (media file paths)
        collect: sample every Nth frame (for videos/animations)
        """
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        # 1) Encode your images
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

        # 2) Build the chat contents: images first, then the text prompt
        text_part = types.Part(text=user)
        contents = [ types.Content(role="user", parts=images + [text_part]) ]

        # --- system / instructions ---
        devMessage = self.dev
        if not system:
            # Gemini's system instructions go in config, not as Content
            system_instruction = devMessage
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                system_instruction = devMessage + "\n" + systemContents
            else:
                system_instruction = devMessage + "\n" + system

        # 4) Bake into the GenerateContentConfig
        config_args = {
            "response_mime_type": "text/plain",
            "system_instruction": [system_instruction]
        }
        generate_content_config = types.GenerateContentConfig(**config_args)

        # 5) Call Gemini
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return response if verbose else response.text
