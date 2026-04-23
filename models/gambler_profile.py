from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base


class GamblerProfile(Base):

    __tablename__ = "gamblers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name = Column(
        String(100),
        nullable=False
    )

    email = Column(String(100))

    initial_stake = Column(Float)

    current_stake = Column(Float)

    win_threshold = Column(Float)

    loss_threshold = Column(Float)

    total_bets = Column(
        Integer,
        default=0
    )
    total_wins = Column(
        Integer,
        default=0
    )
    total_losses = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    ) 
    preferences = relationship(
        "BettingPreferences",
        back_populates="gambler",
        uselist=False,
        cascade="all, delete-orphan"
    )