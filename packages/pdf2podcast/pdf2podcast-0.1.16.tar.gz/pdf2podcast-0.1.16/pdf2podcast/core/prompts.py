"""
Prompt templates and mappings for podcast generation using LangChain.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import PromptTemplate

from pdf2podcast.core.base import BasePromptBuilder
from pdf2podcast.core.prompt_list import SYSTEM_PROMPT

# Template principale per la generazione di podcast
PODCAST_TEMPLATE = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=[
        "text",
        "query",
        "instructions",
        "format_instructions",
        "language",
    ],
)


class PodcastPromptTemplate:
    """Template provider for podcast generation prompts using LangChain."""

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        instructions: Optional[str] = None,
    ):
        """
        Initialize template provider with optional custom system prompt.

        Args:
            system_prompt (Optional[str]): Custom system prompt to override default
            instructions (Optional[str]): Additional instructions to include
        """
        # Store instructions for later use
        self.instructions = instructions or ""

        # Use custom system prompt if provided, otherwise use default
        if system_prompt:
            self.template = PromptTemplate(
                template=system_prompt,
                input_variables=[
                    "text",
                    "query",
                    "instructions",
                    "format_instructions",
                    "language",
                ],
            )
        else:
            self.template = PODCAST_TEMPLATE

    def get_template_with_instructions(self) -> PromptTemplate:
        """Get the template with custom instructions pre-filled if available."""
        if self.instructions:
            return PromptTemplate(
                template=self.template.template,
                input_variables=[
                    "text",
                    "query",
                    "format_instructions",
                    "language",
                ],
                partial_variables={"instructions": self.instructions},
            )
        else:
            return self.template


class PodcastPromptBuilder(BasePromptBuilder):
    """Prompt builder for podcast script generation."""

    def __init__(
        self,
        template_provider=None,
        system_prompt: Optional[str] = None,
        instructions: Optional[str] = None,
        dialogue: bool = False,
    ):
        """
        Initialize with optional custom template provider and system prompt.

        Args:
            template_provider: Template provider class (default: PodcastPromptTemplate)
            system_prompt: Optional custom system prompt to override default
            instructions: Additional instructions to include
            dialogue (bool): Whether to generate dialogue between speakers (kept for compatibility)
        """
        if template_provider is None:
            template_provider = PodcastPromptTemplate
        self.templates = template_provider(
            system_prompt=system_prompt,
            instructions=instructions,
        )
        # Store dialogue setting for easy access
        self.is_dialogue = dialogue

    def build_prompt(self, text: str, **kwargs) -> PromptTemplate:
        """Build main generation prompt with custom instructions if available."""
        return self.templates.get_template_with_instructions()
