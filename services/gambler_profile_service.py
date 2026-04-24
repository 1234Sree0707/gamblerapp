# services/gambler_profile_service.py

import logging
from repositories.gambler_repository import (
    GamblerRepository
)

from repositories.betting_preferences_repository import (
    BettingPreferencesRepository
)

logger = logging.getLogger(__name__)


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

    def update_balance(
        self,
        gambler_id,
        current_stake
    ):
        """
        Update gambler's current balance in database.
        
        Args:
            gambler_id (int): Gambler ID
            current_stake (float): New balance amount
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate inputs
            if not gambler_id or gambler_id <= 0:
                raise ValueError(f"Invalid gambler_id: {gambler_id}")
            
            if current_stake is None or current_stake < 0:
                raise ValueError(f"Invalid current_stake: {current_stake}")
            
            # Update in repository
            self.gambler_repository.update_balance(
                gambler_id,
                current_stake
            )
            
            logger.info(
                f"✓ Balance updated: gambler_id={gambler_id}, "
                f"new_balance=${current_stake:.2f}"
            )
            
        except Exception as e:
            logger.error(
                f"✗ Failed to update balance for gambler {gambler_id}: {str(e)}"
            )
            raise

    def verify_balance(
        self,
        gambler_id,
        expected_stake
    ):
        """
        Verify that gambler's balance was persisted correctly in database.
        
        Args:
            gambler_id (int): Gambler ID
            expected_stake (float): Expected balance
            
        Returns:
            bool: True if balance matches expected value
        """
        return self.gambler_repository.verify_balance(
            gambler_id,
            expected_stake
        )

    def get_current_balance(self, gambler_id):
        """
        Get gambler's current balance from database.
        
        Args:
            gambler_id (int): Gambler ID
            
        Returns:
            float: Current balance or None if gambler not found
        """
        gambler = self.get_gambler(gambler_id)
        if gambler:
            return gambler.get('current_stake')
        return None