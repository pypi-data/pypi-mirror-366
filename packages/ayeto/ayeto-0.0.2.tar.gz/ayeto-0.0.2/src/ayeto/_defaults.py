from __future__ import annotations
import os

BASE_URL = "https://ayeto.ai/api/v2"
API_KEY = os.getenv("AYETO_API_KEY", "")

IMG_GEN_MODEL = "dall-e-2"