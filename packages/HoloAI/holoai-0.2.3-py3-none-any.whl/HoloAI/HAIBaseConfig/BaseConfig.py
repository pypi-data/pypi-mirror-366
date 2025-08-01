import os
import threading

from HoloAI.HAIUtils.HAIUtils import (
    DEV_MSG,
    parseInstructions,
)


class BaseConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(BaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.dev = DEV_MSG

        self.initialized = True

    # ---------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------
    def getResponse(self, **kwargs):
        """
        Get a Response from the configured model.
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
        model   = kwargs.get('model')
        system  = parseInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        skills  = kwargs.get('skills', None)
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens', 369) or kwargs.get('budget', 369)
        verbose = kwargs.get('verbose', False)
        return self.Response(model=model, system=system, user=user, skills=skills, tools=tools, tokens=tokens, verbose=verbose)

    def getVision(self, **kwargs):
        """
        Get a Vision response from the configured model.
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
        model   = kwargs.get('model')
        system  = parseInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        skills  = kwargs.get('skills', None)
        tools   = kwargs.get('tools', None)
        tokens  = kwargs.get('tokens', 369) or kwargs.get('budget', 369)
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 10)
        verbose = kwargs.get('verbose', False)
        return self.Vision(model=model, system=system, user=user, paths=paths, collect=collect, verbose=verbose)