from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.cashdoro.domain.cashdoro import Cashdoro
from src.cashdoro.infrastructure.models import CashdoroModel


def to_entity(model: CashdoroModel) -> Cashdoro:
    return Cashdoro(
        id=model.id,
        user_id=model.user_id,
        session_time=model.session_time,
        pause_time=model.pause_time,
        long_pause_time=model.long_pause_time,
        sessions_until_long_break=model.sessions_until_long_break,
        hourly_rate=model.hourly_rate,
        total_earnings=model.total_earnings,
    )


def to_model(cashdoro: Cashdoro) -> CashdoroModel:
    return CashdoroModel(
        user_id=cashdoro.user_id,
        session_time=cashdoro.session_time,
        pause_time=cashdoro.pause_time,
        long_pause_time=cashdoro.long_pause_time,
        sessions_until_long_break=cashdoro.sessions_until_long_break,
        hourly_rate=cashdoro.hourly_rate,
        total_earnings=cashdoro.total_earnings,
    )


class SqlAlchemyCashdoroRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, cashdoro: Cashdoro) -> None:
        self._session.add(to_model(cashdoro))

    def get_by_user_id(self, user_id: UUID) -> Cashdoro | None:
        model = self._session.scalar(select(CashdoroModel).where(CashdoroModel.user_id == user_id))
        return to_entity(model) if model else None

    def save_settings(self, cashdoro: Cashdoro) -> None:
        model = self._session.get_one(CashdoroModel, cashdoro.id)
        model.session_time = cashdoro.session_time
        model.pause_time = cashdoro.pause_time
        model.long_pause_time = cashdoro.long_pause_time
        model.sessions_until_long_break = cashdoro.sessions_until_long_break
        model.hourly_rate = cashdoro.hourly_rate

    def commit(self) -> None:
        self._session.commit()
