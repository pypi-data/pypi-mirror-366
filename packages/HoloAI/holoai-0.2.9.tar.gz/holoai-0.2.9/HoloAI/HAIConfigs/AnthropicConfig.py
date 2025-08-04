import os
import threading
from dotenv import load_dotenv
import anthropic

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

class AnthropicConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("ANTHROPIC_API_KEY")
        if not apiKey:
            raise KeyError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment variables.")
        self.client = anthropic.Anthropic(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("ANTHROPIC_TEXT_MODEL", "claude-sonnet-4")
        self.VModel = os.getenv("ANTHROPIC_VISION_MODEL", "claude-sonnet-4")

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

        # --- user memories / latest ---
        messages = parseJsonInput(user)

        args = self._getArgs(model, system, messages, tokens)

        if tools:
            args["tools"] = tools

        if supportsReasoning(model):
            if effort == "auto":
                budget = 1024
            # the budget can be no less than 1024 tokens so we need to ensure that
            if budget < 1024:
                orgBudget = budget
                budget = 1024
                print(f"[Notice] Budget ({orgBudget}) is less than 1024 tokens. Adjusting budget to {budget}.")
                print(f"[Notice] To avoid this, set budget to at least 1024 tokens.")
            # now we to make sure the token amount is greater than the budget
            if tokens and tokens < budget:
                orgTokens = tokens
                tokens = tokens + budget
                print(f"[Notice] Tokens ({orgTokens}) is less than budget ({budget}). Adjusting tokens to {tokens}.")
                print(f"[Notice] To avoid this, set tokens higher than your budget amount e.g tokens=1500, budget=1024")
                args["max_tokens"] = tokens
            args["thinking"] = {"type": "enabled", "budget_tokens": budget}
        
        response = self.client.messages.create(**args)
        return response if verbose else response.content[0].text

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

        userContent = images.copy()
        if user:
            userContent.append({
                "type": "text",
                "text": user
            })
        messages = [{
            "role": "user",
            "content": userContent
        }]

        args = self._getArgs(model, system, messages, tokens)

        response = self.client.messages.create(**args)
        return response if verbose else response.content[0].text

    def _getArgs(self, model, system, messages, tokens):
        args = {
            "model": model,
            "system": system,
            "messages": messages,
            "max_tokens": tokens,
        }
        return args
