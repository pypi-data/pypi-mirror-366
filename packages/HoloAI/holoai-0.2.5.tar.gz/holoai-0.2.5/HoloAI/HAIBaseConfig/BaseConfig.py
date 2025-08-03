import os
import threading

from HoloAI.HAIUtils.HAIUtils import (
    parseInstructions,
    validateResponseArgs,
    validateVisionArgs,
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

        self.skills  = None  # Default skills
        self.tools   = None  # Default tools
        self.show    = 'hidden'  # Default visibility for Reasoning/Thinking
        self.effort  = 'auto'  # Default effort level
        self.budget  = 1369  # Default budget
        self.tokens  = 3369  # Default tokens
        self.collect = 10  # Default frames to collect
        self.paths   = []  # Default paths for images
        self.collect = 10  # Default number of frames to collect
        self.verbose = False  # Default verbose mode

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
            
            - tools: (list) Tools to use (Optional).
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - show: (str) Show reasoning/thinking ('hidden', 'parsed', 'raw') (Optional (default: 'hidden')).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        model   = kwargs.get('model')
        system  = parseInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        skills  = kwargs.get('skills', self.skills)
        tools   = kwargs.get('tools', self.tools)
        show    = kwargs.get('show', self.show)
        effort  = kwargs.get('effort', self.effort)
        budget  = kwargs.get('budget', self.budget) or kwargs.get('max_budget', self.budget)
        tokens  = kwargs.get('tokens', self.tokens) or kwargs.get('max_tokens', self.tokens)
        paths   = kwargs.get('paths', self.paths)
        collect = kwargs.get('collect', self.collect)
        verbose = kwargs.get('verbose', self.verbose)
        validateResponseArgs(model, user)
        return self.Response(model=model, system=system, user=user, skills=skills, tools=tools, show=show, effort=effort, budget=budget, tokens=tokens, verbose=verbose)

    def getVision(self, **kwargs):
        """
        Get a Vision response from the configured model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - paths: (list) List of image paths (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Vision response object.
        """
        model   = kwargs.get('model')
        system  = parseInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        skills  = kwargs.get('skills', self.skills)
        tools   = kwargs.get('tools', self.tools)
        show    = kwargs.get('show', self.show)
        effort  = kwargs.get('effort', self.effort)
        budget  = kwargs.get('budget', self.budget) or kwargs.get('max_budget', self.budget)
        tokens  = kwargs.get('tokens', self.tokens) or kwargs.get('max_tokens', self.tokens)
        paths   = kwargs.get('paths', self.paths)
        collect = kwargs.get('collect', self.collect)
        verbose = kwargs.get('verbose', self.verbose)
        validateVisionArgs(model, user, paths)
        return self.Vision(model=model, system=system, user=user, paths=paths, collect=collect, tokens=tokens, verbose=verbose)
