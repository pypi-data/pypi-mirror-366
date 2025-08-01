
import os
import re
import threading
from datetime import datetime
from dotenv import load_dotenv

from .HAIUtils.HAIUtils import (
    getFrameworkInfo,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    parseInstructions,
    parseModels,
    isStructured,
    safetySettings,
    extractImagePaths,
    getFrames
)

load_dotenv()

PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}

def isKeySet(envKey):
    return os.getenv(envKey) is not None


MODEL_PREFIX_MAP = {
    ("gpt",): "openai", # "o1", "o3"): "openai",
    ("claude",): "anthropic",
    ("llama", "meta-llama", "gemma2",): "groq",
    ("gemini", "gemma",): "google",
}

providerMap = {}

if isKeySet("OPENAI_API_KEY"):
    from .HAIConfigs.OpenAIConfig import OpenAIConfig
    providerMap["openai"] = OpenAIConfig()

if isKeySet("ANTHROPIC_API_KEY"):
    from .HAIConfigs.AnthropicConfig import AnthropicConfig
    providerMap["anthropic"] = AnthropicConfig()

if isKeySet("GOOGLE_API_KEY"):
    from .HAIConfigs.GoogleConfig import GoogleConfig
    providerMap["google"] = GoogleConfig()

if isKeySet("GROQ_API_KEY"):
    from .HAIConfigs.GroqConfig import GroqConfig
    providerMap["groq"] = GroqConfig()


class HoloAI:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HoloAI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.providerMap = providerMap

        self.initialized = True

    def getFrameworkInfo(self):
        """
        Returns a string with framework information.
        """
        return getFrameworkInfo()

    def listProviders(self):
        """
        Returns a list of available model providers.
        This is based on the keys of the providerMap dictionary.
        """
        return list(self.providerMap.keys())

    def _inferModelProvider(self, model: str):
        """
        Infers the provider based on the model name.
        Returns the provider name as a string, or None if not found.
        """
        return next(
            (provider for prefixes, provider in MODEL_PREFIX_MAP.items()
             if any(model.startswith(prefix) for prefix in prefixes)),
            None
        )

    def _getProviderConfig(self, model: str):
        """
        Returns the config instance strictly based on model's inferred provider.
        Raises if provider cannot be inferred.
        """
        provider = self._inferModelProvider(model)
        if provider and provider in self.providerMap:
            return self.providerMap[provider]
        raise ValueError(f"Cannot infer provider from model '{model}'. Valid providers: {list(self.providerMap.keys())}")

    def HoloCompletion(self, **kwargs):
        """
        HoloAI completion requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills to use (Optional).
            - tools: (list) Tools to use (Optional).
            - tokens: (int) Max tokens to use (Optional, default: 369).
            - verbose: (bool) Return verbose output (Optional, default: False).
        :return: A Response object, or a Vision object if image paths are found.
        """
        # kwargs  = {k.lower(): v for k, v in kwargs.items()}
        # models  = kwargs.get("models") or kwargs.get("model")
        # raw     = kwargs.get("input") or kwargs.get("user")
        # system  = parseInstructions(kwargs)
        # verbose = kwargs.get("verbose", False)
        # if models is None or raw is None:
        #     raise ValueError("HoloCompletion requires 'model' or 'models' and input/user")

        # # Use parseModels util
        # models = parseModels(models)

        # # ————— 1) Isolate the *last* user message, not the whole history —————
        # if isinstance(raw, list):
        #     last = raw[-1]
        #     text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
        # else:
        #     text = str(raw)

        # # ————— 2) Find any image paths in that single prompt —————
        # image_paths = extractImagePaths(text)

        # if image_paths:
        #     img = image_paths[-1]
        #     prompt_only = re.split(re.escape(img), text)[0].strip()
        #     return self.Vision(
        #         model=models['vision'],
        #         system=system,
        #         user=prompt_only,
        #         paths=image_paths,
        #         collect=5,
        #         verbose=verbose
        #     )

        # # If no image, run text/response as usual, using the 'response' model
        # kwargs['model'] = models['response']
        # return self.Response(**kwargs)
        return self._routeCompletion(**kwargs)

    def HoloAgent(self, **kwargs):
        """
        HoloAI agent requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills to use (Optional).
            - tools: (list) Tools to use (Optional).
            - tokens: (int) Max tokens to use (Optional, default: 369).
            - verbose: (bool) Return verbose output (Optional, default: False).
        :return: A Response object, or a Vision object if image paths are found.
        """
        # kwargs  = {k.lower(): v for k, v in kwargs.items()}
        # models  = kwargs.get("models") or kwargs.get("model")
        # raw     = kwargs.get("input") or kwargs.get("user")
        # system  = parseInstructions(kwargs)
        # verbose = kwargs.get("verbose", False)
        # if models is None or raw is None:
        #     raise ValueError("HoloCompletion requires 'model' or 'models' and input/user")

        # # Use parseModels util
        # models = parseModels(models)

        # # ————— 1) Isolate the *last* user message, not the whole history —————
        # if isinstance(raw, list):
        #     last = raw[-1]
        #     text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
        # else:
        #     text = str(raw)

        # # ————— 2) Find any image paths in that single prompt —————
        # image_paths = extractImagePaths(text)

        # if image_paths:
        #     img = image_paths[-1]
        #     prompt_only = re.split(re.escape(img), text)[0].strip()
        #     return self.Vision(
        #         model=models['vision'],
        #         system=system,
        #         user=prompt_only,
        #         paths=image_paths,
        #         collect=5,
        #         verbose=verbose
        #     )

        # # If no image, run text/response as usual, using the 'response' model
        # kwargs['model'] = models['response']
        # return self.Response(**kwargs)
        return self._routeCompletion(**kwargs)

    def Agent(self, **kwargs):
        """
        Get a Response from the Agent model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills to use (Optional).
            - tools: (list) Tools to use (Optional).
            - tokens: (int) Max tokens to use (Optional (default: 369)).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        #print(f"\n[Response Request] {kwargs}")
        # kwargs = {k.lower(): v for k, v in kwargs.items()}
        # model  = kwargs.get('model')
        # config = self._getProviderConfig(model)
        # return config.getResponse(**kwargs)
        return self._routeResponse(**kwargs)

    def Response(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills to use (Optional).
            - tools: (list) Tools to use (Optional).
            - tokens: (int) Max tokens to use (Optional (default: 369)).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        #print(f"\n[Response Request] {kwargs}")
        # kwargs = {k.lower(): v for k, v in kwargs.items()}
        # model  = kwargs.get('model')
        # config = self._getProviderConfig(model)
        # return config.getResponse(**kwargs)
        return self._routeResponse(**kwargs)

    def Vision(self, **kwargs):
        """
        Get a Vision response from the Vision model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tokens: (int) Max tokens to use (Optional (default: 369)).
            - paths: (list) List of image paths (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Vision response object.
        """
        #print(f"\n[Vision Request] {kwargs}")
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getVision( **kwargs)

    #------------- Utility Methods -------------#
    # def _routeCompletion(self, **kwargs):
    #     kwargs  = {k.lower(): v for k, v in kwargs.items()}
    #     models  = kwargs.get("models") or kwargs.get("model")
    #     raw     = kwargs.get("input") or kwargs.get("user")
    #     system  = parseInstructions(kwargs)
    #     verbose = kwargs.get("verbose", False)
    #     if models is None or raw is None:
    #         raise ValueError("HoloCompletion requires 'model' or 'models' and input/user")

    #     # Use parseModels util
    #     models = parseModels(models)

    #     # ————— 1) Isolate the *last* user message, not the whole history —————
    #     if isinstance(raw, list):
    #         last = raw[-1]
    #         text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
    #     else:
    #         text = str(raw)

    #     # ————— 2) Find any image paths in that single prompt —————
    #     image_paths = extractImagePaths(text)

    #     if image_paths:
    #         img = image_paths[-1]
    #         prompt_only = re.split(re.escape(img), text)[0].strip()
    #         return self.Vision(
    #             model=models['vision'],
    #             system=system,
    #             user=prompt_only,
    #             paths=image_paths,
    #             collect=5,
    #             verbose=verbose
    #         )

    #     # If no image, run text/response as usual, using the 'response' model
    #     kwargs['model'] = models['response']
    #     return self.Response(**kwargs)
    def _routeCompletion(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        models  = kwargs.get("models") or kwargs.get("model")
        raw     = kwargs.get("input") or kwargs.get("user")
        system  = parseInstructions(kwargs)
        verbose = kwargs.get("verbose", False)
        if models is None or raw is None:
            raise ValueError("HoloCompletion requires 'model' or 'models' and input/user")

        models = parseModels(models)

        # 1. Normalize user input
        if isinstance(raw, list):
            last = raw[-1]
            text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
        else:
            text = str(raw)

        # 2. Detect mode
        imagePaths = extractImagePaths(text)

        # 3. Select mode
        def visionMode():
            img = imagePaths[-1]
            promptOnly = re.split(re.escape(img), text)[0].strip()
            return self.Vision(
                model=models['vision'],
                system=system,
                user=promptOnly,
                paths=imagePaths,
                collect=5,
                verbose=verbose
            )

        def responseMode():
            kwargs['model'] = models['response']
            return self.Response(**kwargs)

        modeMap = {
            "vision": visionMode,
            "response": responseMode,
            # Add more modes here, e.g., "audio": audioMode, etc.
        }

        mode = "vision" if imagePaths else "response"
        return modeMap[mode]()

    def _routeResponse(self, **kwargs):
        #print(f"\n[Response Request] {kwargs}")
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getResponse(**kwargs)

    def isStructured(self, obj):
        """
        Check if the input is a structured list of message dicts.
        A structured list is defined as a list of dictionaries where each dictionary
        contains both "role" and "content" keys.
        Returns True if the input is a structured list, False otherwise.
        """
        return isStructured(obj)

    def formatInput(self, value):
        """
        Formats the input value into a list.
        - If `value` is a string, returns a list containing that string.
        - If `value` is already a list, returns it as is.
        - If `value` is None, returns an empty list.
        """
        return [value] if isinstance(value, str) else value

    def formatConversation(self, convo, user):
        """
        Returns a flat list representing the full conversation:
        - If `convo` is a list, appends the user input (str or list) to it.
        - If `convo` is a string, creates a new list with convo and user input.
        """
        if isinstance(convo, str):
            convo = [convo]
        if isinstance(user, str):
            return convo + [user]
        elif isinstance(user, list):
            return convo + user
        else:
            raise TypeError("User input must be a string or list of strings.")


    def formatJsonInput(self, role: str, content: str) -> dict:
        """
        Format content for JSON-based APIs like OpenAI, Groq, etc.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatJsonInput(role=role, content=content)

    def formatJsonExtended(self, role: str, content: str) -> dict:
        """
        Extended JSON format for APIs like OpenAI, Groq, etc.
        Maps 'assistant', 'developer', 'model' and 'system' to 'assistant'.
        All other roles (including 'user') map to 'user'.
        """
        return formatJsonExtended(role=role, content=content)

    def parseJsonInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized message objects using formatJsonExtended.
        """
        return parseJsonInput(data)

    def formatTypedInput(self, role: str, content: str) -> dict:
        """
        Format content for typed APIs like Google GenAI.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatTypedInput(role=role, content=content)

    def formatTypedExtended(self, role: str, content: str) -> dict:
        """
        Extended typed format for Google GenAI APIs.
        Maps 'assistant', 'developer', 'system' and 'model' to 'model'.
        All other roles (including 'user') map to 'user'.
        """
        return formatTypedExtended(role=role, content=content)

    def parseTypedInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized Google GenAI message objects using formatTypedExtended.
        """
        return parseTypedInput(data)

    def safetySettings(self, **kwargs):
        """
        Construct a list of Google GenAI SafetySetting objects.

        Accepts thresholds as keyword arguments:
            harassment, hateSpeech, sexuallyExplicit, dangerousContent

        Example:
            safetySettings(harassment="block_high", hateSpeech="block_low")
        """
        return safetySettings(**kwargs)

    def extractImagePaths(self, text: str):
        """
        Extracts image file paths from a given text.
        Supports both Windows and Unix-style paths.
        Returns a list of matched image paths.
        """
        return extractImagePaths(text)
