# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloAI",
    version="0.2.6",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai",
        "groq",
        "google-genai",
        "anthropic",
        
        "SyncLink",
        "SynMem",
        "SynLrn",
        "BitSig",
        "MediaCapture",
        "AgentToAgent",

        "python-dotenv",
        "requests",
        "opencv-python",
        "Pillow",
        "gguf-parser",
        "numpy",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="Modular, provider-agnostic AI framework for multi-model orchestration, agent workflows, and vision."

)
