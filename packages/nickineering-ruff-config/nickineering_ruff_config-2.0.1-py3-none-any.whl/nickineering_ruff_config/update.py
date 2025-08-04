import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def update_ruff_base() -> None:
    """Copy the ruff.toml file to the new package so it can be extended from."""
    filename = "nickineering-ruff-base.toml"
    src_file = Path(__file__).parent / filename
    dest_file = Path.cwd() / filename
    shutil.copy(src_file, dest_file)
    logging.info(
        "The up to date %s was copied to the current working directory.", filename
    )
