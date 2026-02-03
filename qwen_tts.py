# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "typer",
#     "mlx-audio @ git+https://github.com/Blaizzy/mlx-audio.git",
#     "soundfile",
# ]
# ///
"""Qwen3-TTS CLI — voice clone, voice design, and custom voice generation on Apple Silicon."""

import platform
import time
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import soundfile as sf
import typer
from rich.console import Console

app = typer.Typer(help="Generate speech audio via Qwen3-TTS models on Apple Silicon.")
console = Console()

SAMPLE_RATE = 24_000

MODELS = {
    "clone": {
        "0.6B": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16",
        "1.7B": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
    },
    "custom": {
        "0.6B": "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16",
        "1.7B": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16",
    },
    "design": {
        "1.7B": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
    },
}


class ModelSize(str, Enum):
    small = "0.6B"
    large = "1.7B"


def _check_apple_silicon() -> None:
    if platform.machine() not in ("arm64", "aarch64"):
        console.print(
            "[bold yellow]Warning:[/] This script is optimized for Apple Silicon (arm64). "
            "Performance may be degraded on this platform."
        )


def _read_file_or_string(value: str) -> str:
    """If *value* ends with .txt and the file exists, read its contents; otherwise return as-is."""
    p = Path(value)
    if p.suffix == ".txt" and p.is_file():
        return p.read_text().strip()
    return value


def _load_model(model_id: str):
    """Load a Qwen3-TTS model, returning the model object."""
    from mlx_audio.tts.utils import load_model

    with console.status("[bold green]Loading model…"):
        model = load_model(model_id)
    return model


def _generate_and_save(model, output: Path, **gen_kwargs) -> None:
    """Run model.generate(), concatenate audio chunks, write WAV, print timing."""
    audio_chunks = []

    with console.status("[bold green]Generating audio…"):
        t0 = time.perf_counter()
        for result in model.generate(**gen_kwargs):
            audio_chunks.append(np.array(result.audio, copy=False))
        elapsed = time.perf_counter() - t0

    if not audio_chunks:
        console.print("[bold red]Error:[/] No audio generated.")
        raise typer.Exit(1)

    audio = np.concatenate(audio_chunks)
    sf.write(str(output), audio, SAMPLE_RATE)
    duration = len(audio) / SAMPLE_RATE
    console.print(f"[bold]Saved:[/] {output}  ({duration:.1f}s audio, generated in {elapsed:.1f}s)")


# ── clone ────────────────────────────────────────────────────────────────────


@app.command()
def clone(
    text: Annotated[str, typer.Option("--text", "-t", help="Text to synthesize.")],
    ref_audio: Annotated[Path, typer.Option("--ref-audio", "-r", help="Path to reference WAV file.")],
    ref_text: Annotated[str, typer.Option(help="Transcript of the reference audio.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output WAV path.")] = Path("output_clone.wav"),
    model_size: Annotated[ModelSize, typer.Option(help="Model size.")] = ModelSize.large,
) -> None:
    """Voice cloning from reference audio."""
    _check_apple_silicon()

    if not ref_audio.is_file():
        console.print(f"[bold red]Error:[/] Reference audio not found: {ref_audio}")
        raise typer.Exit(1)

    model_id = MODELS["clone"][model_size.value]
    console.print(f"Mode [bold]clone[/] | model [bold]{model_id}[/]")

    model = _load_model(model_id)
    _generate_and_save(
        model,
        output,
        text=text,
        ref_audio=str(ref_audio),
        ref_text=ref_text,
    )


# ── design ───────────────────────────────────────────────────────────────────


@app.command()
def design(
    text: Annotated[str, typer.Option("--text", "-t", help="Text to synthesize.")],
    voice: Annotated[str, typer.Option("--voice", "-v", help="Voice description string or path to .txt file.")] = "A warm, friendly female voice with clear enunciation.",
    language: Annotated[str, typer.Option("--language", "-l", help="Language.")] = "English",
    output: Annotated[Path, typer.Option("--output", "-o", help="Output WAV path.")] = Path("output_design.wav"),
) -> None:
    """Generate speech using a natural-language voice description."""
    _check_apple_silicon()

    voice_desc = _read_file_or_string(voice)
    model_id = MODELS["design"]["1.7B"]
    console.print(f"Mode [bold]design[/] | model [bold]{model_id}[/]")
    console.print(f"Voice: [dim]{voice_desc[:80]}{'…' if len(voice_desc) > 80 else ''}[/]")

    model = _load_model(model_id)
    _generate_and_save(
        model,
        output,
        text=text,
        instruct=voice_desc,
        lang_code=language,
    )


# ── custom ───────────────────────────────────────────────────────────────────


@app.command()
def custom(
    text: Annotated[str, typer.Option("--text", "-t", help="Text to synthesize.")],
    speaker: Annotated[str, typer.Option("--speaker", "-s", help="Speaker name.")] = "Aiden",
    instruct: Annotated[Optional[str], typer.Option("--instruct", "-i", help="Style instruction string or path to .txt file.")] = None,
    language: Annotated[str, typer.Option("--language", "-l", help="Language.")] = "English",
    output: Annotated[Path, typer.Option("--output", "-o", help="Output WAV path.")] = Path("output_custom.wav"),
    model_size: Annotated[ModelSize, typer.Option(help="Model size.")] = ModelSize.large,
) -> None:
    """Predefined speaker with optional emotion/style instruction."""
    _check_apple_silicon()

    model_id = MODELS["custom"][model_size.value]
    console.print(f"Mode [bold]custom[/] | model [bold]{model_id}[/] | speaker [bold]{speaker}[/]")

    instruct_text = None
    if instruct:
        instruct_text = _read_file_or_string(instruct)
        console.print(f"Instruct: [dim]{instruct_text[:80]}{'…' if len(instruct_text) > 80 else ''}[/]")

    model = _load_model(model_id)
    _generate_and_save(
        model,
        output,
        text=text,
        voice=speaker,
        instruct=instruct_text,
        lang_code=language,
    )


if __name__ == "__main__":
    app()
