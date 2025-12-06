# app/llm_wrappers.py
import os
from typing import Optional

# ---- Gemini wrapper (google-genai) ----
try:
    from google import genai as _genai
    GENAI_AVAILABLE = True
except Exception:
    _genai = None
    GENAI_AVAILABLE = False

class GeminiWrapper:
    """
    Gemini via google-genai. Use the Developer API:
      export GOOGLE_GENAI_API_KEY="..."
    """
    def __init__(self, model: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        if not GENAI_AVAILABLE:
            raise RuntimeError("google-genai package not installed (pip install google-genai)")
        api_key = api_key or os.getenv("GOOGLE_GENAI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_GENAI_API_KEY not set")
        self.client = _genai.Client(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            if hasattr(resp, "text") and resp.text:
                return resp.text.strip()
            return str(resp)
        except Exception as e:
            return f"--ERROR-- Gemini error: {e}"
# ---- Hugging Face Router (OpenAI-compatible) ----
try:
    from openai import OpenAI
    HF_OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    HF_OPENAI_AVAILABLE = False


class HFDeepSeekWrapper:
    """
    Hugging Face Router using OpenAI-compatible API
    Model: deepseek-ai/DeepSeek-V3.2:novita

    Requires:
      export HF_TOKEN="hf_..."
    """

    def __init__(
        self,
        model: str = "deepseek-ai/DeepSeek-V3.2:novita",
        api_key: Optional[str] = None,
    ):
        if not HF_OPENAI_AVAILABLE:
            raise RuntimeError("openai package not installed")

        api_key = api_key or os.getenv("HF_TOKEN")
        if not api_key:
            raise RuntimeError("HF_TOKEN environment variable not set")

        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
        )
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"--ERROR-- HF DeepSeek error: {e}"
