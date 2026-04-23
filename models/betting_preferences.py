from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class BettingPreferences(Base):

    __tablename__ = "betting_preferences"

    id = Column(Integer, primary_key=True)

    gambler_id = Column(
        Integer,
        ForeignKey("gamblers.id"),
        unique=True
    )

    min_bet = Column(Float)
    max_bet = Column(Float)

    preferred_strategy = Column(String(50))

    auto_play = Column(String(10))

    session_limit = Column(Integer)

    gambler = relationship(
        "GamblerProfile",
        back_populates="preferences"
    )
