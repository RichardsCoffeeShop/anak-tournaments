from pathlib import Path

import aiofiles
from loguru import logger

from src.core import config


class LocalStorageClient:
    def __init__(self, logs_path: str):
        self.base_path = Path(logs_path)

    async def get_logs_by_tournament(self, tournament_id: int) -> list[str]:
        tournament_dir = self.base_path / str(tournament_id)
        if not tournament_dir.is_dir():
            return []
        try:
            return [
                f"logs/{tournament_id}/{f.name}"
                for f in sorted(tournament_dir.iterdir())
                if f.is_file()
            ]
        except OSError as e:
            logger.exception(f"Error listing logs: {e}")
            return []

    async def get_log_by_filename(self, tournament_id: int, filename: str) -> bytes:
        if filename.startswith("logs/"):
            rel = filename.split("/", 2)[-1] if filename.count("/") >= 2 else filename
        else:
            rel = f"{tournament_id}/{filename}"

        file_path = self.base_path / rel
        if not file_path.is_file():
            logger.error(f"File '{file_path}' does not exist.")
            return b""
        try:
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()
        except OSError as e:
            logger.exception(f"Error reading log file: {e}")
            return b""


async_client = LocalStorageClient(logs_path=config.app.logs_path)
