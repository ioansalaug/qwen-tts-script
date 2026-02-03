# Qwen TTS CLI — User Guide

A command-line tool for generating speech audio using Qwen3-TTS models on Apple Silicon, powered by [mlx-audio](https://github.com/Blaizzy/mlx-audio).

## Requirements

- macOS on Apple Silicon (M1/M2/M3/M4)
- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager

No manual dependency installation needed — `uv run` handles everything automatically.

## Quick Start

```bash
# Voice design (describe the voice you want)
uv run qwen_tts.py design -t "Hello world" -v "A warm female voice"

# Custom voice (use a predefined speaker)
uv run qwen_tts.py custom -t "Hello world" -s Aiden

# Voice cloning (clone from reference audio)
uv run qwen_tts.py clone -t "Hello world" -r reference.wav --ref-text "Transcript of the reference audio"
```

## Commands

### `design` — Voice from description

Generate speech using a natural-language voice description. Only available with the 1.7B model.

```bash
uv run qwen_tts.py design [OPTIONS]
```

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--text` | `-t` | Yes | — | Text to synthesize |
| `--voice` | `-v` | No | Generic warm female | Voice description string or path to `.txt` file |
| `--language` | `-l` | No | `English` | Language |
| `--output` | `-o` | No | `output_design.wav` | Output WAV path |

**Examples:**

```bash
# Inline voice description
uv run qwen_tts.py design -t "Welcome to the show." -v "An energetic young male voice with a bright tone"

# Voice description from file
uv run qwen_tts.py design -t "Welcome to the show." -v voices/playful_buddy.txt

# Specify language and output path
uv run qwen_tts.py design -t "Bonjour le monde" -v "A soft French female voice" -l French -o bonjour.wav
```

### `custom` — Predefined speaker

Use a built-in speaker voice with optional emotion/style instructions.

```bash
uv run qwen_tts.py custom [OPTIONS]
```

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--text` | `-t` | Yes | — | Text to synthesize |
| `--speaker` | `-s` | No | `Aiden` | Speaker name |
| `--instruct` | `-i` | No | None | Style instruction string or path to `.txt` file |
| `--language` | `-l` | No | `English` | Language |
| `--output` | `-o` | No | `output_custom.wav` | Output WAV path |
| `--model-size` | — | No | `1.7B` | Model size (`0.6B` or `1.7B`) |

**Available speakers:**

| Language | Speakers |
|----------|----------|
| English | Aiden, Ryan |
| Chinese | Vivian, Serena, Uncle_Fu, Dylan, Eric |

**Examples:**

```bash
# Basic usage
uv run qwen_tts.py custom -t "Good morning everyone." -s Ryan

# With emotion instruction
uv run qwen_tts.py custom -t "I can't believe we won!" -s Aiden -i "Very excited and happy"

# Chinese speaker
uv run qwen_tts.py custom -t "你好世界" -s Vivian -l Chinese

# Use smaller model for faster generation
uv run qwen_tts.py custom -t "Hello world" -s Aiden --model-size 0.6B
```

### `clone` — Voice cloning

Clone a voice from a reference audio file.

```bash
uv run qwen_tts.py clone [OPTIONS]
```

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--text` | `-t` | Yes | — | Text to synthesize |
| `--ref-audio` | `-r` | Yes | — | Path to reference WAV file |
| `--ref-text` | — | Yes | — | Transcript of the reference audio |
| `--output` | `-o` | No | `output_clone.wav` | Output WAV path |
| `--model-size` | — | No | `1.7B` | Model size (`0.6B` or `1.7B`) |

**Tips for best results:**

- Use a clean reference audio (minimal background noise)
- 3–10 seconds of reference audio works well
- Provide an accurate transcript of the reference audio
- 24kHz WAV files work best; other formats/rates are resampled automatically

**Example:**

```bash
uv run qwen_tts.py clone \
  -t "This sentence will be spoken in the cloned voice." \
  -r my_voice_sample.wav \
  --ref-text "This is what I said in the recording."
```

## Voice Description Files

The `voices/` directory contains example voice descriptions that can be passed to `--voice` or `--instruct`:

| File | Description |
|------|-------------|
| `voices/warm_teacher.txt` | Patient female teacher in her 40s |
| `voices/playful_buddy.txt` | Energetic young male in his 20s |
| `voices/calm_narrator.txt` | Deep baritone documentary narrator in his 50s |

Create your own `.txt` files with voice descriptions and pass them directly:

```bash
uv run qwen_tts.py design -t "Your text here" -v my_custom_voice.txt
```

## Models

Models are downloaded automatically from HuggingFace on first use and cached locally.

| Mode | 0.6B | 1.7B (default) |
|------|------|-----------------|
| clone | `Qwen3-TTS-12Hz-0.6B-Base-bf16` | `Qwen3-TTS-12Hz-1.7B-Base-bf16` |
| custom | `Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | `Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` |
| design | N/A | `Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` |

The 0.6B models are faster but lower quality. The 1.7B models produce better results and are the default.

## Supported Languages

Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian.

## Output

All output files are 24kHz mono WAV. The sample rate is fixed by the Qwen3-TTS-12Hz models.

## Troubleshooting

**First run is slow:** Models are downloaded from HuggingFace on first use (~2–5 GB per model). Subsequent runs use the cached model.

**"Warning: This script is optimized for Apple Silicon":** The script uses MLX which requires Apple Silicon. It will not work on Intel Macs or other platforms.

**Speaker not found:** Use one of the available speaker names listed above. Speaker names are case-insensitive.
