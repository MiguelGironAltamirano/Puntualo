from pathlib import Path

CURRENT_PROMPT_VERSION = "system_v1"


def load_system_prompt(version: str = CURRENT_PROMPT_VERSION) -> str:
    return (Path(__file__).parent / f"{version}.txt").read_text(encoding="utf-8")
