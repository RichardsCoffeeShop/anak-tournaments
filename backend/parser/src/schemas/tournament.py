from datetime import datetime

from src.schemas.base import BaseRead

__all__ = ("TournamentRead", "TournamentGroupRead")


class TournamentGroupRead(BaseRead):
    name: str
    description: str | None
    is_groups: bool
    challonge_id: int | None
    challonge_slug: str | None


class TournamentRead(BaseRead):
    number: int | None
    name: str
    description: str | None
    challonge_id: int | None
    challonge_slug: str | None
    is_league: bool
    is_finished: bool
    start_date: datetime | None = None
    end_date: datetime | None = None

    groups: list[TournamentGroupRead]
