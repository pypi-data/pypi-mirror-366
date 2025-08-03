from dataclasses import dataclass
from pathlib import Path
import tomllib
import os
import logging

_CONFIG: "Config | None" = None


def set_logger():
    logging_level_envar_map = {
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }

    logging_level = logging_level_envar_map[
        os.environ.get("RECEIPT_STATEMENT_LINKER_LOG_LEVEL", "error")
    ]
    logging.basicConfig(level=logging_level)


@dataclass
class Config:
    categorization_notes: str | None = None
    transcription_model: str = "gemini/gemini-2.5-flash"
    categorization_model: str = "gemini/gemini-2.5-flash-lite"
    matching_model: str = "gemini/gemini-2.5-flash"

    @classmethod
    def get_config(cls) -> "Config":
        global _CONFIG
        if not _CONFIG:
            xdg_data_config = os.environ.get("XDG_CONFIG_HOME")
            base_dir = (
                Path(xdg_data_config) if xdg_data_config else Path.home() / ".config"
            )

            app_dir = base_dir / "receipt_statement_linker"
            app_dir.mkdir(parents=True, exist_ok=True)

            config_file = app_dir / "config.toml"

            try:
                config_str = config_file.read_text(encoding="utf-8")

                _CONFIG = cls(**tomllib.loads(config_str))
            except Exception as e:
                logging.warning("Config file parsing failed", e, exc_info=True)
                _CONFIG = cls()
        return _CONFIG
