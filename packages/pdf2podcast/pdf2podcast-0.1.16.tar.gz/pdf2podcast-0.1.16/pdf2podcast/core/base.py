"""
Base abstract classes for the pdf2podcast library components.
"""

from functools import wraps
import json  # Added import
from abc import ABC, abstractmethod
import logging
import re
import time
from typing import Callable, Dict, Any, Optional, List

from pdf2podcast.core.parsers import PodcastParser, StrictDialoguePodcastParser

logger = logging.getLogger(__name__)


def retry_on_exception(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        retries (int): Maximum number of retries
        delay (float): Initial delay between retries in seconds
        backoff (float): Backoff multiplier
        exceptions (tuple): Exceptions to catch
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_delay = delay
            last_exception = None

            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if i < retries - 1:
                        logger.warning(
                            f"Attempt {i + 1}/{retries} failed: {str(e)}. "
                            f"Retrying in {retry_delay:.1f}s..."
                        )
                        time.sleep(retry_delay)
                        retry_delay *= backoff
                    else:
                        logger.error(f"All {retries} attempts failed.")

            raise last_exception

        return wrapper

    return decorator


class BasePromptBuilder(ABC):
    """Base class for building prompts."""

    @abstractmethod
    def build_prompt(self, text: str, **kwargs) -> "PromptTemplate":
        """
        Build a prompt for content generation.

        Args:
            text (str): Source text
            **kwargs: Additional prompt parameters

        Returns:
            PromptTemplate: Formatted prompt template
        """
        pass


class BaseRAG(ABC):
    """Base class for RAG (Retrieval Augmented Generation) implementations."""

    @abstractmethod
    def process(self, pdf_path: str) -> str:
        """
        Process a PDF document and extract relevant text content.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            str: Extracted and processed text from the PDF
        """
        pass


class BaseChunker(ABC):
    """Base class for text chunking implementations."""

    @abstractmethod
    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split text into manageable chunks.

        Args:
            text (str): Text to be chunked
            chunk_size (int): Maximum size of each chunk in characters

        Returns:
            List[str]: List of text chunks
        """
        pass


class BaseRetriever(ABC):
    """Base class for semantic text retrieval implementations."""

    @abstractmethod
    def add_texts(self, texts: List[str]) -> None:
        """
        Add texts to the retrieval system.

        Args:
            texts (List[str]): List of text chunks to be indexed
        """
        pass

    @abstractmethod
    def get_relevant_chunks(self, query: str, k: int = 3) -> List[str]:
        """
        Retrieve most relevant text chunks for a query.

        Args:
            query (str): Query text to find relevant chunks for
            k (int): Number of chunks to retrieve (default: 3)

        Returns:
            List[str]: List of relevant text chunks
        """
        pass


class BaseLLM(ABC):
    """Base class for Large Language Model implementations."""

    def __init__(self, prompt_builder: Optional[BasePromptBuilder] = None):
        """
        Initialize LLM with optional prompt builder.

        Args:
            prompt_builder (Optional[BasePromptBuilder]): Custom prompt builder
        """
        self.prompt_builder = prompt_builder

    def _clean_text(self, text: str) -> str:
        """
        Clean text using regex patterns to remove visual references and formatting.

        Args:
            text (str): Input text to clean

        Returns:
            str: Cleaned text with visual references removed
        """
        patterns = [
            r"(Figure|Fig\.|Table|Image)\s+\d+[a-z]?",
            r"(shown|illustrated|depicted|as seen) (in|on|above|below)",
            r"(refer to|see|view) (figure|table|image)",
            r"\(fig\.\s*\d+\)",
            r"as (shown|depicted) (here|below|above)",
        ]

        processed = text
        for pattern in patterns:
            processed = re.sub(pattern, "", processed, flags=re.IGNORECASE)

        processed = re.sub(r"\s+", " ", processed)
        return processed.strip()

    @retry_on_exception()
    def generate_podcast_script(
        self,
        text,
        **kwargs: Dict[str, Any],
    ) -> str:
        """
        Generate a coherent podcast script.

        Args:
            **kwargs: Additional parameters for customization, including:
                - text (str): Input text to convert into a podcast script
                - dialogue (bool): Whether to generate dialogue between speakers
                - query (str): Optional query to guide content generation
                - instructions (str): Optional additional instructions for generation

        Returns:
            str: Generated podcast script
        """
        from pdf2podcast.core.prompts import PodcastPromptBuilder

        try:
            # Clean and validate input text
            if not text or not text.strip():
                raise ValueError("Input text cannot be empty")

            processed_text = self._clean_text(text)
            if not processed_text:
                raise ValueError("Text cleaning resulted in empty content")

            dialogue = kwargs.get("dialogue", False)
            print(f"Dialogue: {dialogue}")

            # Generate initial script
            try:
                # Create a prompt builder
                if self.prompt_builder is None:
                    prompt_builder = PodcastPromptBuilder(dialogue=dialogue)
                else:
                    # If we have a custom prompt builder, use it as is
                    prompt_builder = self.prompt_builder

                # Get the prompt template with language
                prompt_template = prompt_builder.build_prompt(
                    text=processed_text,
                    **kwargs,
                )

                # Create the chain based on format
                logger.info("Creating podcast chain...")
                # Use strict parser for better reliability when dialogue is requested
                if dialogue:
                    parser = StrictDialoguePodcastParser()
                    logger.info(
                        "Using StrictDialoguePodcastParser for guaranteed dialogue format"
                    )
                else:
                    parser = PodcastParser()
                    logger.info("Using standard PodcastParser for text format")

                # Create chain with properly formatted prompt and format variables
                chain = prompt_template | self.llm | parser

                # Get format instructions from the selected parser
                format_instructions = parser.get_format_instructions()

                # Build input variables based on template requirements
                input_variables = {
                    "text": processed_text,
                    "query": kwargs.get("query", ""),
                    "format_instructions": format_instructions,
                    "language": self.language,
                }

                # Only add instructions if the template expects them (not pre-filled)
                if "instructions" in prompt_template.input_variables:
                    input_variables["instructions"] = kwargs.get("instructions", "")

                result = chain.invoke(input_variables)

                logger.info("Successfully generated script")
                return result.model_dump_json()

            except Exception as e:
                logger.error(f"Google API error: {str(e)}")
                raise  # Will be caught by retry decorator

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            raise


class BaseTTS(ABC):
    """Base class for Text-to-Speech implementations."""

    def _preprocess_text(self, text: str) -> str:
        """Basic text preprocessing."""
        # Basic cleanup
        processed_text = " ".join(text.split())
        # Basic punctuation handling and remove special formatting
        processed_text = (
            processed_text.replace(" ,", ",")
            .replace(" .", ".")
            .replace("*", "")
            .replace("_", "")
            .replace("[SOUND]", "<SOUND>")  # Convert any tags to English format with <>
            .replace("[PAUSE]", "<PAUSE>")
            .replace("[MUSIC]", "<MUSIC>")
            .replace("[EFFECT]", "<EFFECT>")
        )
        processed_text = (
            processed_text.replace(".", ". ").replace("!", "! ").replace("?", "? ")
        )
        return processed_text

    @abstractmethod
    def generate_audio(
        self,
        text_segments: List[str],  # Changed from text: str to text_segments: List[str]
        output_path: str,
        voice_id: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert text segments to speech and save as audio file.
        If multiple segments, they will be concatenated.

        Args:
            text_segments (List[str]): List of text segments to convert to speech
            output_path (str): Path where to save the audio file
            voice_id (Optional[str]): ID of the voice to use
            **kwargs: Additional TTS-specific parameters

        Returns:
            Dict[str, Any]: Dictionary containing audio metadata
                          (e.g., {'duration': float, 'size': int})
        """
        pass


class BasePodcastGenerator:
    """Base class for podcast generation orchestration."""

    def __init__(
        self,
        rag_system: BaseRAG,
        llm_provider: str,
        tts_provider: str,
        llm_config: Optional[Dict[str, Any]] = None,
        tts_config: Optional[Dict[str, Any]] = None,
        chunker: Optional[BaseChunker] = None,
        retriever: Optional[BaseRetriever] = None,
        k: int = 3,
    ):
        """
        Initialize podcast generator with required components.

        Args:
            rag_system (BaseRAG): System for PDF text extraction
            llm_provider (str): Type of LLM to use ("gemini", "anthropic", etc.)
            tts_provider (str): Type of TTS to use ("elevenlabs", "kokoro", etc.)
            llm_config (Optional[Dict[str, Any]]): Configuration for LLM
            tts_config (Optional[Dict[str, Any]]): Configuration for TTS
            chunker (Optional[BaseChunker]): System for text chunking
            retriever (Optional[BaseRetriever]): System for semantic retrieval
            k (int): Number of chunks to retrieve for a query (default: 3)
        """
        from .managers import LLMManager, TTSManager

        self.rag = rag_system

        # Initialize models using managers
        llm_manager = LLMManager(llm_provider, **(llm_config or {}))
        tts_manager = TTSManager(tts_provider, **(tts_config or {}))

        self.llm = llm_manager.get_llm()
        self.tts = tts_manager.get_tts()
        self.chunker = chunker
        self.retriever = retriever
        self.k = k

    def generate(
        self,
        pdf_path: Optional[str] = None,
        voice_id: Optional[str] = None,
        output_path: str = "output.mp3",
        text: str = None,
        **kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a podcast from a PDF document.

        Args:
            pdf_path (str): Path to the input PDF file
            output_path (str): Path where to save the output audio file
            voice_id (Optional[str]): ID of the voice to use for TTS
            text (str): Optional text input for podcast generation
            **kwargs: Additional parameters for RAG, LLM, or TTS systems

        Returns:
            Dict[str, Any]: Dictionary containing generation results and metadata
        """
        # Extract text from PDF
        if pdf_path:
            processed_text_for_llm = self.rag.process(pdf_path)
        elif text:
            # If text is directly provided, assume it's already processed or doesn't need RAG
            processed_text_for_llm = text
        else:
            raise ValueError("Either pdf_path or text must be provided.")

        # Process with chunking and retrieval if available and if pdf_path was used
        if self.chunker and self.retriever:
            chunks = self.chunker.chunk_text(processed_text_for_llm)
            self.retriever.add_texts(chunks)

            query = kwargs.get("query")
            if not query:
                # Use default query if none provided
                query = "Generate a podcast script based on the extracted text."

            # Use retrieved chunks to generate the script
            relevant_chunks = self.retriever.get_relevant_chunks(query, k=self.k)
            processed_text_for_llm = "\n\n".join(relevant_chunks)

        # Generate podcast script (which is a JSON string)
        script_json_string = self.llm.generate_podcast_script(
            text=processed_text_for_llm,
            **kwargs,
        )

        # Parse the JSON string into a Python dictionary
        parsed_script_data = json.loads(script_json_string)

        print(parsed_script_data)

        # Always process as chapters since that's now our only mode
        script_segments_for_tts: List[str] = []

        # Extract text from each chapter
        if "chapters" in parsed_script_data and isinstance(
            parsed_script_data["chapters"], list
        ):
            for chapter in parsed_script_data["chapters"]:
                # Check if chapter_content is a dialogue array
                if isinstance(chapter.get("chapter_content"), list):
                    # È un dialogo - array di {speaker, content}
                    dialogue_text = "\n".join(
                        [
                            f"[{turn['speaker']}]: {turn['content']}"
                            for turn in chapter["chapter_content"]
                        ]
                    )
                    script_segments_for_tts.append(dialogue_text)
                else:
                    # È un monologo - stringa semplice
                    script_segments_for_tts.append(
                        str(chapter.get("chapter_content", ""))
                    )
        else:
            # Fallback if structure is not as expected
            script_segments_for_tts = [
                parsed_script_data.get("text", "No content generated")
            ]
            print("Warning: No chapters found in script. Using fallback content.")

        # Process chapters individually to get timing data
        # For KokoroTTS, pass the original dialogue structure if available
        if (
            hasattr(self.tts, "_generate_dialogue_audio")
            and "chapters" in parsed_script_data
        ):
            # Check if we have dialogue content to pass to KokoroTTS
            dialogue_segments = []
            for chapter in parsed_script_data["chapters"]:
                if isinstance(chapter.get("chapter_content"), list):
                    # È un dialogo - array di {speaker, content}
                    dialogue_segments.append(chapter["chapter_content"])
                else:
                    # È un monologo - stringa semplice
                    dialogue_segments.append(str(chapter.get("chapter_content", "")))

            audio_result = self.tts.generate_audio(
                text_segments=dialogue_segments,
                output_path=output_path,
                voice_id=voice_id,
                **kwargs,
            )
        else:
            # For other TTS engines, use the converted text segments
            audio_result = self.tts.generate_audio(
                text_segments=script_segments_for_tts,
                output_path=output_path,
                voice_id=voice_id,
                **kwargs,
            )

        if audio_result.get("timing_data") and "chapters" in parsed_script_data:
            # Update chapter timing information in the script
            for chapter, timing in zip(
                parsed_script_data["chapters"], audio_result["timing_data"]["chapters"]
            ):
                chapter["start_time"] = timing["character_timings"]["start_time"]
                chapter["end_time"] = timing["character_timings"]["end_time"]
                chapter["duration"] = timing["character_timings"]["duration"]
                chapter["character_timings"] = timing["character_timings"]

        return {
            "script": parsed_script_data,
            "audio": audio_result,
            "total_duration": audio_result.get("timing_data", {}).get(
                "total_duration", 0.0
            ),
        }
