"""
Parsers for handling LLM outputs in specific formats.
"""

from typing import List, Optional, Union
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator
import json


class DialogueTurn(BaseModel):
    """Model for a single dialogue turn between speakers."""

    speaker: str = Field(description="Speaker identifier (S1 or S2)")
    content: str = Field(description="What the speaker says")

    @validator("speaker")
    def validate_speaker(cls, v):
        """Ensure speaker is S1 or S2."""
        if v not in ["S1", "S2"]:
            raise ValueError("Speaker must be S1 or S2")
        return v

    @validator("content")
    def validate_content(cls, v):
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class DialogueChapter(BaseModel):
    """Model for a chapter that MUST contain dialogue."""

    position: int = Field(description="Position of the chapter in the sequence")
    title: str = Field(description="Title of the chapter")
    chapter_content: List[DialogueTurn] = Field(
        description="Array of dialogue turns between speakers",
        min_items=1,
    )

    @validator("chapter_content")
    def validate_dialogue_content(cls, v):
        """Ensure we have alternating speakers and meaningful dialogue."""
        if not v:
            raise ValueError("Dialogue chapter must have at least one dialogue turn")

        # Check for meaningful dialogue (should have both speakers)
        speakers = set(turn.speaker for turn in v)
        if len(speakers) < 2:
            raise ValueError("Dialogue should contain both S1 and S2 speakers")

        return v

    def get_text_content(self) -> str:
        """Get the text content of the dialogue chapter."""
        return "\n".join(
            [f"[{turn.speaker}]: {turn.content}" for turn in self.chapter_content]
        )


class TextChapter(BaseModel):
    """Model for a chapter that contains only text content."""

    position: int = Field(description="Position of the chapter in the sequence")
    title: str = Field(description="Title of the chapter")
    chapter_content: str = Field(
        description="Text content of the chapter",
        min_length=1,
    )

    def get_text_content(self) -> str:
        """Get the text content of the text chapter."""
        return str(self.chapter_content)


class PodcastChapter(BaseModel):
    """Model for a single podcast chapter."""

    position: int = Field(description="Position of the chapter in the sequence")
    title: str = Field(description="Title of the chapter")
    chapter_content: Union[str, List[DialogueTurn]] = Field(
        description="Content of the chapter - can be text string or dialogue array",
        default="",
    )

    def get_text_content(self) -> str:
        """Get the text content of the chapter, regardless of format."""
        if isinstance(self.chapter_content, list):
            # Convert dialogue array to text format
            return "\n".join(
                [f"[{turn.speaker}]: {turn.content}" for turn in self.chapter_content]
            )
        return str(self.chapter_content)


class DialoguePodcast(BaseModel):
    """Model for a podcast that MUST contain dialogue chapters."""

    chapters: List[DialogueChapter] = Field(
        description="List of dialogue chapters in the podcast",
        min_items=1,
    )
    title: str = Field(description="Title of the podcast")
    tags: List[str] = Field(description="List of tags for the podcast")

    @validator("chapters")
    def validate_dialogue_chapters(cls, v):
        """Ensure all chapters are dialogue chapters."""
        if not v:
            raise ValueError("Dialogue podcast must have at least one chapter")
        return v


class TextPodcast(BaseModel):
    """Model for a podcast that contains only text chapters."""

    chapters: List[TextChapter] = Field(
        description="List of text chapters in the podcast",
        min_items=1,
    )
    title: str = Field(description="Title of the podcast")
    tags: List[str] = Field(description="List of tags for the podcast")


class Podcast(BaseModel):
    """Model for a complete podcast with chapters and metadata."""

    chapters: List[PodcastChapter] = Field(
        description="List of chapters in the podcast"
    )
    title: str = Field(description="Title of the podcast")
    tags: List[str] = Field(description="List of tags for the podcast")


class PodcastParser(PydanticOutputParser):
    """Parser for podcast content with chapters and metadata."""

    def __init__(self) -> None:
        super().__init__(pydantic_object=Podcast)

    def parse(self, text: str) -> Podcast:
        """Parse the text into a Podcast object with chapters and metadata."""
        return super().parse(text)


class StrictDialoguePodcastParser(PydanticOutputParser):
    """Strict parser for podcast content that MUST be in dialogue format."""

    def __init__(self) -> None:
        super().__init__(pydantic_object=DialoguePodcast)

    def get_format_instructions(self) -> str:
        """Return strict format instructions for dialogue format."""
        base_instructions = super().get_format_instructions()

        # Add very specific instructions for dialogue format
        dialogue_instructions = """

        CRITICAL REQUIREMENTS FOR DIALOGUE FORMAT:
        1. MANDATORY: ALL chapters MUST contain "chapter_content" as an array of dialogue objects
        2. MANDATORY: Each dialogue object MUST have exactly these fields:
           - "speaker": MUST be exactly "S1" or "S2" (no other values allowed)
           - "content": MUST be a non-empty string with the speaker's words
        3. MANDATORY: Each chapter MUST have dialogue from BOTH S1 and S2
        4. FORBIDDEN: Do NOT use any "dialogue" field - it is deprecated
        5. FORBIDDEN: Do NOT use string content in "chapter_content" - only arrays

        EXACT REQUIRED JSON STRUCTURE:
        {
          "chapters": [
            {
              "position": 1,
              "title": "Chapter Title",
              "chapter_content": [
                {"speaker": "S1", "content": "Host introduction..."},
                {"speaker": "S2", "content": "Expert response..."},
                {"speaker": "S1", "content": "Follow-up question..."}
              ]
            }
          ],
          "title": "Podcast Title",
          "tags": ["tag1", "tag2"]
        }

        SPEAKERS DEFINITION:
        - S1: Host/Interviewer - asks questions, guides conversation
        - S2: Expert/Guest - provides insights, answers questions
        """

        return base_instructions + dialogue_instructions

    def parse(self, text: str) -> DialoguePodcast:
        """Parse text into a strict DialoguePodcast object with validation."""
        try:
            result = super().parse(text)
            # Additional validation to ensure dialogue quality
            for chapter in result.chapters:
                if len(chapter.chapter_content) < 2:
                    raise ValueError(
                        f"Chapter '{chapter.title}' has insufficient dialogue turns"
                    )
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse strict dialogue format: {str(e)}")
