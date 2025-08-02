"""
Large Language Model (LLM) implementations for pdf2podcast.
"""

import os
import logging
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from .base import BaseLLM
from .prompts import PodcastPromptBuilder

# Setup logging
logger = logging.getLogger(__name__)


class GeminiLLM(BaseLLM):
    """
    Google's Gemini-based LLM implementation with optimized content generation.
    """

    def __init__(
        self,
        api_key: str = None,
        model_name: str = "gemini-1.5-flash",
        language: str = "en",
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_output_tokens: int = 4096,
        streaming: bool = False,
        prompt_builder: PodcastPromptBuilder = None,
        dialogue: bool = False,
    ):
        """
        Initialize Gemini LLM system.

        Args:
            api_key (str, optional): Google API key. If not provided, will look for GENAI_API_KEY env var
            model_name (str): Name of the Gemini model to use (default: "gemini-1.5-flash")
            temperature (float): Sampling temperature (default: 0.2)
            top_p (float): Nucleus sampling parameter (default: 0.9)
            max_output_tokens (int): Maximum output length (default: 4096)
            streaming (bool): Whether to use streaming mode (default: False)
            prompt_builder (Optional[PodcastPromptBuilder]): Custom prompt builder
            dialogue (bool): Whether to generate dialogue between speakers (default: False)
        """
        super().__init__(prompt_builder)

        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GENAI_API_KEY")
            if not api_key:
                raise ValueError("No API key provided and GENAI_API_KEY not found")

        self.language = language
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            streaming=streaming,
            google_api_key=api_key,
        )


class AnthropicLLM(BaseLLM):

    def __init__(
        self,
        api_key: str = None,
        model_name: str = "claude-4-sonnet",
        language: str = "en",
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_output_tokens: int = 4096,
        streaming: bool = False,
        prompt_builder: PodcastPromptBuilder = None,
        dialogue: bool = False,
    ):

        super().__init__(prompt_builder)

        if api_key is None:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("No API key provided and ANTHROPIC_API_KEY not found")

        self.language = language
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=max_output_tokens,
            top_p=top_p,
            streaming=streaming,
            api_key=api_key,
        )
