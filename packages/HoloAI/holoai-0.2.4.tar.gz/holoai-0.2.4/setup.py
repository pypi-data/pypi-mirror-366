# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloAI",
    version="0.2.4",
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

        "python-dotenv",
        "requests",
        "opencv-python",
        "Pillow",
        "gguf-parser",
        "numpy",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="A modern AI Client",
)
