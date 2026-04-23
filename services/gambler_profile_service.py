# services/gambler_profile_service.py

from repositories.gambler_repository import (
    GamblerRepository
)

from repositories.betting_preferences_repository import (
    BettingPreferencesRepository
)


class GamblerProfileService:

    def __init__(self):

        self.gambler_repository = (
            GamblerRepository()
        )

        self.preferences_repository = (
            BettingPreferencesRepository()
        )

    def create_gambler(
        self,
        name,
        email,
        initial_stake,
        win_threshold,
        loss_threshold
    ):

        return self.gambler_repository.create(
            name,
            email,
            initial_stake,
            win_threshold,
            loss_threshold
        )

    def update_preferences(
        self,
        gambler_id,
        min_bet,
        max_bet,
        strategy
    ):

        self.preferences_repository.create(
            gambler_id,
            min_bet,
            max_bet,
            strategy
        )

    def get_gambler(
        self,
        gambler_id
    ):

        return self.gambler_repository.get_by_id(
            gambler_id
        )

    def reset_profile(
        self,
        gambler_id
    ):

        self.gambler_repository.reset_profile(
            gambler_id
        )