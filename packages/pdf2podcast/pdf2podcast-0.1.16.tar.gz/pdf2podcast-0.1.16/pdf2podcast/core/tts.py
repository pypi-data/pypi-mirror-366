"""
Text-to-Speech (TTS) implementations for pdf2podcast.
"""

import io
import os
import time
from typing import Dict, Any, Optional, List, Callable, Tuple, Union
from contextlib import closing
import tempfile
import logging
from functools import wraps

# Audio processing
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# Kokoro TTS
from kokoro import KPipeline
import soundfile as sf

# Elevenlabs TTS
import base64
from elevenlabs import ElevenLabs


from .base import BaseTTS

# Setup logging
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


def validate_mp3_file(file_path: str) -> bool:  # Renamed from validate_audio_file
    """
    Validate that an audio file is properly formatted MP3.

    Args:
        file_path (str): Path to the audio file

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.warning(f"MP3 file does not exist or is empty: {file_path}")
            return False
        audio = AudioSegment.from_mp3(file_path)
        return len(audio) > 0
    except (CouldntDecodeError, OSError):
        logger.warning(f"Could not decode MP3 file or OS error: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating MP3 audio {file_path}: {str(e)}")
        return False


def _validate_wav_file(file_path: str) -> bool:
    """
    Validate that an audio file is a properly formatted WAV.
    Relies on pydub's ability to load it and checks for non-zero length.
    """
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.warning(f"WAV file does not exist or is empty: {file_path}")
            return False
        # Attempt to load the WAV file to check its integrity and get duration
        audio = AudioSegment.from_wav(file_path)
        return len(audio) > 0  # Ensure it has a positive duration
    except CouldntDecodeError:  # pydub raises this for bad WAVs
        logger.error(f"Could not decode WAV file: {file_path}")
        return False
    except FileNotFoundError:  # Should be caught by os.path.exists, but good to have
        logger.error(f"WAV file not found for validation: {file_path}")
        return False
    except Exception as e:  # Catch any other pydub or OS errors
        logger.error(f"Unexpected error validating WAV audio {file_path}: {str(e)}")
        return False


def split_text(text: str, max_length: int = 3000) -> List[str]:
    """
    Split text into chunks that are safe for TTS processing.

    Args:
        text (str): Text to split
        max_length (int): Maximum length per chunk

    Returns:
        List[str]: List of text chunks
    """
    chunks = []
    sentences = text.split(". ")
    current_chunk = ""

    for sentence in sentences:
        if not sentence.strip():
            continue

        # Add period back if it was removed by split
        sentence = sentence.strip() + ". "

        if len(current_chunk) + len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def _merge_audio_chunks_and_export_wav(  # Renamed from merge_audio_files
    chunk_files: List[str], output_path: str
) -> bool:
    """
    Merge multiple WAV audio chunks into a single WAV file.
    Handles cleanup of temporary chunk files.
    """
    combined = AudioSegment.empty()
    valid_input_files_for_cleanup = []

    logger.info(
        f"Starting merge of {len(chunk_files)} audio chunks into WAV: {output_path}"
    )

    for file_path in chunk_files:
        try:
            # Expecting WAV files primarily.
            # GoogleTTS might initially produce MP3, which should be converted to WAV before this stage.
            if file_path.lower().endswith(".wav"):
                if not _validate_wav_file(file_path):
                    logger.error(f"Skipping invalid or empty WAV chunk: {file_path}")
                    continue
                audio_chunk = AudioSegment.from_wav(file_path)
            elif file_path.lower().endswith(
                ".mp3"
            ):  # Fallback for non-converted GoogleTTS chunks
                logger.warning(
                    f"Processing MP3 chunk {file_path} for WAV output pipeline. Consider converting to WAV earlier."
                )
                if not validate_mp3_file(file_path):
                    logger.error(f"Skipping invalid or empty MP3 chunk: {file_path}")
                    continue
                audio_chunk = AudioSegment.from_mp3(
                    file_path
                )  # This implies a decode step
            else:
                logger.warning(f"Unsupported chunk file format: {file_path}. Skipping.")
                continue

            combined += audio_chunk
            valid_input_files_for_cleanup.append(file_path)
            logger.debug(
                f"Added chunk {file_path} to combined audio. Current combined length: {len(combined)} ms."
            )

        except Exception as e:
            logger.error(f"Error processing chunk {file_path} for WAV merge: {e}")
            continue

    if not combined or len(combined) == 0:
        logger.error(
            "No valid audio data to merge into WAV after processing all chunks."
        )
        for (
            f_path
        ) in (
            valid_input_files_for_cleanup
        ):  # Clean up successfully processed chunks even if merge fails
            try:
                if os.path.exists(f_path):
                    os.remove(f_path)
            except OSError:
                pass
        return False

    try:
        # Export the combined audio segment to a WAV file
        combined.export(output_path, format="wav")
        logger.info(f"Successfully exported merged WAV to {output_path}")

        # Clean up all processed temporary chunk files after successful export
        for f_path in valid_input_files_for_cleanup:
            try:
                if os.path.exists(f_path):
                    os.remove(f_path)
            except OSError as e_clean:
                logger.warning(
                    f"Failed to remove temporary chunk file {f_path}: {e_clean}"
                )
        return True
    except Exception as e_export:
        logger.error(f"Error exporting final WAV to {output_path}: {e_export}")
        # Consider not cleaning up chunks if export fails, for debugging.
        return False


class KokoroTTS(BaseTTS):
    """
    Kokoro TTS implementation with timing information.
    """

    def __init__(
        self,
        voice_id: Union[str, List[str], Dict[str, str]] = "af_heart",
        temp_dir: str = "temp",
        language: Optional[str] = None,  # Add but ignore language parameter
        **kwargs,  # Accept additional params but ignore them
    ):
        # Handle voice mapping for multi-speaker support
        if isinstance(voice_id, list):
            # Map list to S1, S2
            self.speakers = {
                "S1": voice_id[0] if len(voice_id) > 0 else "af_heart",
                "S2": voice_id[1] if len(voice_id) > 1 else "am_liam",
            }
            self.voice_id = voice_id[0]  # Default voice for non-dialogue content
        elif isinstance(voice_id, dict):
            # Use dict directly
            self.speakers = voice_id
            self.voice_id = voice_id.get("S1", "af_heart")  # Default voice
        else:
            # Single voice for all speakers
            self.speakers = {"S1": voice_id, "S2": voice_id}
            self.voice_id = voice_id

        # Map languages to Kokoro's lang_codes
        lang_map = {
            "it": "i",  # Italian
            "en": "a",  # American English (or "b" for British English)
            "fr": "f",  # French
            "es": "e",  # Spanish
            "hi": "h",  # Hindi
            "ja": "j",  # Japanese
            "zh": "z",  # Mandarin Chinese
            "pt": "p",  # Brazilian Portuguese
        }
        # Get the language code, default to "en" if not supported
        lang_code = (
            lang_map.get(language, "a") if language else "a"
        )  # Default to American English
        # Store language for text preprocessing
        self.language = language

        # Initialize pipeline with basic language support
        self.pipeline = KPipeline(repo_id="hexgrad/Kokoro-82M", lang_code=lang_code)
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def _generate_dialogue_audio(
        self,
        dialogue_turns: List[Dict[str, str]],
        chapter_index: int,
        current_time: float = 0.0,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Generate audio for dialogue turns with different speakers."""

        chapter_wav_path = os.path.join(
            self.temp_dir, f"dialogue_chapter_{chapter_index}.wav"
        )
        timing_data = {
            "start_time": current_time,
            "character_timings": [],
            "duration": 0.0,
        }

        try:
            audio_segments = []
            segment_index = 0

            for turn_index, turn in enumerate(dialogue_turns):
                speaker = turn.get("speaker", "S1")
                content = turn.get("content", "")

                if not content.strip():
                    continue

                # Get voice for this speaker
                voice = self.speakers.get(speaker, self.voice_id)

                # Preprocess text
                processed_text = self._preprocess_text(content)

                # Generate audio for this turn
                generator = self.pipeline(
                    processed_text, voice=voice, speed=0.9, split_pattern=r"\n+"
                )

                for result in generator:
                    # Process timing information
                    if (
                        self.language == "en"
                        and result.tokens is not None
                        and len(result.tokens) > 0
                    ):
                        for token in result.tokens:
                            if token.start_ts is not None and token.end_ts is not None:
                                timing_data["character_timings"].append(
                                    {
                                        "word": token.text,
                                        "start": token.start_ts
                                        + current_time
                                        + timing_data["duration"],
                                        "end": token.end_ts
                                        + current_time
                                        + timing_data["duration"],
                                        "speaker": speaker,
                                    }
                                )

                    # Save audio segment
                    if result.audio is not None:
                        audio_data = result.audio.cpu().numpy()
                        temp_segment_path = os.path.join(
                            self.temp_dir,
                            f"dialogue_{chapter_index}_{speaker}_{segment_index}.wav",
                        )
                        sf.write(temp_segment_path, audio_data, 24000)
                        audio_segments.append(temp_segment_path)
                        segment_index += 1

                        # Update duration based on actual audio length
                        audio_duration = len(audio_data) / 24000  # 24kHz sample rate
                        timing_data["duration"] += audio_duration

            # Merge all dialogue segments
            if len(audio_segments) > 1:
                if not _merge_audio_chunks_and_export_wav(
                    audio_segments, chapter_wav_path
                ):
                    raise Exception(
                        f"Failed to merge dialogue chapter {chapter_index} segments"
                    )
            elif len(audio_segments) == 1:
                os.rename(audio_segments[0], chapter_wav_path)
            else:
                raise Exception(
                    f"No dialogue audio segments generated for chapter {chapter_index}"
                )

            timing_data["end_time"] = current_time + timing_data["duration"]
            return chapter_wav_path, timing_data

        except Exception as e:
            logger.error(f"Error generating dialogue chapter {chapter_index}: {str(e)}")
            return None, timing_data

    def _generate_chapter_audio(
        self, text: str, chapter_index: int, current_time: float = 0.0
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Generate audio for a chapter and collect timing information."""

        chapter_wav_path = os.path.join(self.temp_dir, f"chapter_{chapter_index}.wav")
        timing_data = {
            "start_time": current_time,
            "character_timings": [],
            "duration": 0.0,
        }

        try:
            # Apply language-specific text preprocessing
            processed_text = self._preprocess_text(text)

            # Use pipeline with preprocessed text
            generator = self.pipeline(processed_text, voice=self.voice_id)
            audio_segments = []
            current_position = 0.0  # Track timing manually

            for result in generator:
                # Process timing information only for English
                if (
                    self.language == "en"
                    and result.tokens is not None
                    and len(result.tokens) > 0
                ):
                    for token in result.tokens:
                        if token.start_ts is not None and token.end_ts is not None:
                            timing_data["character_timings"].append(
                                {
                                    "word": token.text,
                                    "start": token.start_ts + current_time,
                                    "end": token.end_ts + current_time,
                                }
                            )
                            timing_data["duration"] = max(
                                timing_data["duration"], token.end_ts
                            )
                # For non-English or if tokens are not available, just estimate duration
                elif result.tokens is not None and len(result.tokens) > 0:
                    last_token = result.tokens[-1]
                    if last_token.end_ts is not None:
                        timing_data["duration"] = max(
                            timing_data["duration"], last_token.end_ts
                        )
                    else:
                        timing_data["duration"] += len(result.tokens) * 0.5

                # Save audio segment
                if result.audio is not None:
                    audio_data = result.audio.cpu().numpy()
                    temp_segment_path = os.path.join(
                        self.temp_dir,
                        f"chapter_{chapter_index}_segment_{len(audio_segments)}.wav",
                    )
                    sf.write(temp_segment_path, audio_data, 24000)
                    audio_segments.append(temp_segment_path)

            # Merge audio segments if needed
            if len(audio_segments) > 1:
                if not _merge_audio_chunks_and_export_wav(
                    audio_segments, chapter_wav_path
                ):
                    raise Exception(f"Failed to merge chapter {chapter_index} segments")
            elif len(audio_segments) == 1:
                os.rename(audio_segments[0], chapter_wav_path)
            else:
                raise Exception(
                    f"No audio segments generated for chapter {chapter_index}"
                )

            timing_data["end_time"] = current_time + timing_data["duration"]
            return chapter_wav_path, timing_data

        except Exception as e:
            logger.error(f"Error generating chapter {chapter_index}: {str(e)}")
            return None, timing_data

    @retry_on_exception(retries=3, delay=1.0, exceptions=(Exception,))
    def generate_audio(
        self,
        text_segments: Union[List[str], List[List[Dict[str, str]]]],
        output_path: str,
        voice_id: Optional[Union[str, List[str], Dict[str, str]]] = None,
        **kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate audio for each chapter with timing information.
        Supports both text segments and dialogue segments.
        """
        if voice_id:
            if isinstance(voice_id, (list, dict)):
                # Update speaker mapping
                if isinstance(voice_id, list):
                    self.speakers = {
                        "S1": voice_id[0] if len(voice_id) > 0 else "af_heart",
                        "S2": voice_id[1] if len(voice_id) > 1 else "am_liam",
                    }
                    self.voice_id = voice_id[0]
                else:
                    self.speakers = voice_id
                    self.voice_id = voice_id.get("S1", "af_heart")
            else:
                self.voice_id = voice_id

        chapter_wav_files = []
        timing_data = {"chapters": [], "total_duration": 0.0}

        try:
            current_time = 0.0

            # Process each chapter
            for i, chapter_content in enumerate(text_segments):
                if not chapter_content:
                    continue

                # Check if this is a dialogue (list of dicts) or regular text (string)
                if isinstance(chapter_content, list) and all(
                    isinstance(item, dict) and "speaker" in item and "content" in item
                    for item in chapter_content
                ):
                    # This is a dialogue segment
                    wav_path, chapter_timing = self._generate_dialogue_audio(
                        chapter_content, i, current_time
                    )
                else:
                    # This is regular text
                    chapter_text = str(chapter_content)
                    if not chapter_text.strip():
                        continue
                    wav_path, chapter_timing = self._generate_chapter_audio(
                        chapter_text, i, current_time
                    )

                if wav_path:
                    chapter_wav_files.append(wav_path)
                    timing_data["chapters"].append(chapter_timing)
                    current_time = chapter_timing["end_time"]

            if not chapter_wav_files:
                raise Exception("No audio was generated for any chapter")

            # Merge all chapter audio files
            if not _merge_audio_chunks_and_export_wav(chapter_wav_files, output_path):
                raise Exception("Failed to merge chapter audio files")

            # Validate final output
            if not _validate_wav_file(output_path):
                raise Exception("Final audio file is invalid")

            timing_data["total_duration"] = current_time
            size = os.path.getsize(output_path)

            return {
                "success": True,
                "path": output_path,
                "size": size,
                "timing_data": timing_data,
            }

        except Exception as e:
            logger.error(f"Audio generation failed: {str(e)}")
            # Cleanup
            try:
                for f_name in os.listdir(self.temp_dir):
                    if f_name.startswith(("chapter_", "dialogue_", "kokoro_chunk_")):
                        os.remove(os.path.join(self.temp_dir, f_name))
            except OSError:
                pass

            return {
                "success": False,
                "error": str(e),
                "path": None,
                "size": 0,
                "timing_data": None,
            }


class ElevenLabsTTS(BaseTTS):

    def __init__(
        self,
        api_key: str,
        voice_id: Union[str, List[str], Dict[str, str]] = "XrExE9yKIg1WjnnlVkGX",
        temp_dir: str = "temp",
        language: Optional[str] = None,  # Add but ignore language parameter
        **kwargs,  # Accept additional params but ignore them
    ):
        # Handle voice mapping for multi-speaker support
        if isinstance(voice_id, list):
            # Map list to S1, S2
            self.speakers = {
                "S1": voice_id[0] if len(voice_id) > 0 else "XrExE9yKIg1WjnnlVkGX",
                "S2": voice_id[1] if len(voice_id) > 1 else "pqHfZKP75CvOlQylNhV4",
            }
            self.voice_id = voice_id[0]  # Default voice for non-dialogue content
        elif isinstance(voice_id, dict):
            # Use dict directly
            self.speakers = voice_id
            self.voice_id = voice_id.get("S1", "XrExE9yKIg1WjnnlVkGX")  # Default voice
        else:
            # Single voice for all speakers
            self.speakers = {"S1": voice_id, "S2": voice_id}
            self.voice_id = voice_id

        self.client = ElevenLabs(api_key=api_key)

        # Store language for text preprocessing
        self.language = language

        # Initialize pipeline with basic language support
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def _generate_dialogue_audio(
        self,
        dialogue_turns: List[Dict[str, str]],
        chapter_index: int,
        last_turn_end_time: float = 0.0,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Generate audio for dialogue turns with different speakers."""

        chapter_wav_path = os.path.join(
            self.temp_dir, f"dialogue_chapter_{chapter_index}.wav"
        )

        try:
            audio_segments = []
            timing_data = {}

            for turn_index, turn in enumerate(dialogue_turns):
                speaker = turn.get("speaker", "S1")
                content = turn.get("content", "")

                if not content.strip():
                    continue

                # Get voice for this speaker
                voice = self.speakers.get(speaker, self.voice_id)

                # Preprocess text
                processed_text = self._preprocess_text(content)

                response = self.client.text_to_speech.convert_with_timestamps(
                    voice_id=voice, text=processed_text
                )

                print("ElevenLabs response:", response)

                # Save audio segment
                if response.audio_base_64 is not None:

                    # Decoding audio from base64
                    audio = base64.b64decode(response.audio_base_64)
                    timing_data_turn = {"speaker": speaker, **response.alignment.dict()}

                    # Adjust timing data based on last turn end time
                    timing_data_turn["duration"] = (
                        timing_data_turn["character_end_times_seconds"][-1]
                        - timing_data_turn["character_start_times_seconds"][0]
                    )
                    timing_data_turn["character_start_times_seconds"] = [
                        t + last_turn_end_time
                        for t in timing_data_turn["character_start_times_seconds"]
                    ]
                    timing_data_turn["character_end_times_seconds"] = [
                        t + last_turn_end_time
                        for t in timing_data_turn["character_end_times_seconds"]
                    ]
                    timing_data_turn["start_time"] = (
                        last_turn_end_time
                        + timing_data_turn["character_start_times_seconds"][0]
                    )
                    last_turn_end_time = timing_data_turn[
                        "character_end_times_seconds"
                    ][-1]
                    timing_data_turn["end_time"] = last_turn_end_time

                    # Store timing data for this turn
                    timing_data[speaker] = timing_data_turn

                    temp_segment_path = os.path.join(
                        self.temp_dir,
                        f"dialogue_{chapter_index}_{speaker}_{turn_index}.wav",
                    )

                    try:
                        # Convert base64 audio to WAV
                        audio_stream = io.BytesIO(audio)
                        audio_segment = AudioSegment.from_file(
                            audio_stream, format="mp3"
                        )
                        audio_segment.export(temp_segment_path, format="wav")
                        audio_segments.append(temp_segment_path)

                    except Exception as e:
                        logger.error(f"Failed to convert ElevenLabs audio: {str(e)}")
                        continue

                # time.sleep(20)  # Avoid hitting rate limits

            # Merge all dialogue segments
            if len(audio_segments) > 1:
                if not _merge_audio_chunks_and_export_wav(
                    audio_segments, chapter_wav_path
                ):
                    raise Exception(
                        f"Failed to merge dialogue chapter {chapter_index} segments"
                    )
            elif len(audio_segments) == 1:
                os.rename(audio_segments[0], chapter_wav_path)
            else:
                raise Exception(
                    f"No dialogue audio segments generated for chapter {chapter_index}"
                )

            return chapter_wav_path, timing_data, last_turn_end_time

        except Exception as e:
            logger.error(f"Error generating dialogue chapter {chapter_index}: {str(e)}")
            return None, timing_data, 0

    def generate_audio(
        self,
        text_segments: Union[List[str], List[List[Dict[str, str]]]],
        output_path: str,
        voice_id: Optional[Union[str, List[str], Dict[str, str]]] = None,
        **kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate audio for each chapter with timing information.
        Supports both text segments and dialogue segments.
        """

        if voice_id:
            if isinstance(voice_id, (list, dict)):
                # Update speaker mapping
                if isinstance(voice_id, list):
                    self.speakers = {
                        "S1": (
                            voice_id[0] if len(voice_id) > 0 else "XrExE9yKIg1WjnnlVkGX"
                        ),
                        "S2": (
                            voice_id[1] if len(voice_id) > 1 else "pqHfZKP75CvOlQylNhV4"
                        ),
                    }
                    self.voice_id = voice_id[0]
                else:
                    self.speakers = voice_id
                    self.voice_id = voice_id.get("S1", "XrExE9yKIg1WjnnlVkGX")
            else:
                self.voice_id = voice_id

        total_duration = 0.0
        last_turn_end_time = 0.0
        chapter_wav_files = []
        timing_data = {"chapters": [], "total_duration": 0.0}

        try:
            # Process each chapter
            for i, chapter_content in enumerate(text_segments):
                if not chapter_content:
                    continue

                # This is a dialogue segment
                wav_path, chapter_timing, last_turn_end_time = (
                    self._generate_dialogue_audio(
                        chapter_content, i, last_turn_end_time
                    )
                )

                if wav_path:
                    chapter_wav_files.append(wav_path)
                    timing_data["chapters"].append(
                        {"character_timings": chapter_timing}
                    )
                    total_duration += chapter_timing["duration"]

            if not chapter_wav_files:
                raise Exception("No audio was generated for any chapter")

            # Merge all chapter audio files
            if not _merge_audio_chunks_and_export_wav(chapter_wav_files, output_path):
                raise Exception("Failed to merge chapter audio files")

            # Validate final output
            if not _validate_wav_file(output_path):
                raise Exception("Final audio file is invalid")

            timing_data["total_duration"] = total_duration
            size = os.path.getsize(output_path)

            return {
                "success": True,
                "path": output_path,
                "size": size,
                "timing_data": timing_data,
            }

        except Exception as e:
            logger.error(f"Audio generation failed: {str(e)}")
            # Cleanup
            try:
                for f_name in os.listdir(self.temp_dir):
                    if f_name.startswith(
                        ("chapter_", "dialogue_", "elevenlabs_chunk_")
                    ):
                        pass
                        os.remove(os.path.join(self.temp_dir, f_name))
            except OSError:
                pass

            return {
                "success": False,
                "error": str(e),
                "path": None,
                "size": 0,
                "timing_data": None,
            }
